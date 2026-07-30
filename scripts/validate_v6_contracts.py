from __future__ import annotations
import copy, json, pathlib, sys
import yaml
from jsonschema import Draft202012Validator
ROOT=pathlib.Path(__file__).resolve().parents[1]
errors=[]
def err(msg): errors.append(msg)
for p in ROOT.rglob('*.yaml'):
    try: yaml.safe_load(p.read_text(encoding='utf-8'))
    except Exception as e: err(f'YAML解析失败 {p.relative_to(ROOT)}: {e}')
for p in ROOT.rglob('*.json'):
    try: json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: err(f'JSON解析失败 {p.relative_to(ROOT)}: {e}')
openapi=yaml.safe_load((ROOT/'api/openapi.yaml').read_text(encoding='utf-8'))
def resolve_ref(ref):
    cur=openapi
    for part in ref[2:].split('/'):
        cur=cur[part.replace('~1','/').replace('~0','~')]
    return cur
def deref(s,seen=None):
    seen=set() if seen is None else set(seen)
    if isinstance(s,list): return [deref(x,seen) for x in s]
    if not isinstance(s,dict): return s
    if '$ref' in s:
        ref=s['$ref']
        if ref in seen: return {}
        seen.add(ref)
        base=copy.deepcopy(resolve_ref(ref)); base.update({k:v for k,v in s.items() if k!='$ref'})
        return deref(base,seen)
    return {k:deref(v,seen) for k,v in s.items()}
ops={}
for path,item in openapi.get('paths',{}).items():
    for method,op in item.items():
        if method.lower() not in {'get','post','put','patch','delete'}: continue
        oid=op.get('operationId')
        if not oid: err(f'缺少operationId: {method} {path}'); continue
        if oid in ops: err(f'operationId重复: {oid}')
        ops[oid]=(method,path,op)
        for k in ['x-contract-owner','x-implementation-owner','x-contract-status']:
            if not op.get(k): err(f'{oid} 缺少 {k}')
        d=ROOT/'mocks/http'/oid
        for f in ['request.json','response.json','error_response.json']:
            if not (d/f).exists(): err(f'{oid} 缺少Mock {f}')
        if op.get('requestBody') and (d/'request.json').exists():
            rb=op['requestBody']; content=rb.get('content',{})
            if content:
                media,m=next(iter(content.items())); schema=deref(m.get('schema',{}))
                body=json.loads((d/'request.json').read_text(encoding='utf-8'))['body']
                if media=='multipart/form-data' and isinstance(body,dict) and isinstance(body.get('file'),dict):
                    body=dict(body); body['file']='<binary-file>'
                for e in Draft202012Validator(schema).iter_errors(body): err(f'{oid} 请求Mock不符合Schema: {e.message}')
        responses=op.get('responses',{}); code=next((c for c in responses if str(c).startswith('2')),None)
        if code and responses[code].get('content') and (d/'response.json').exists():
            _,m=next(iter(responses[code]['content'].items())); schema=deref(m.get('schema',{}))
            body=json.loads((d/'response.json').read_text(encoding='utf-8'))['body']
            for e in Draft202012Validator(schema).iter_errors(body): err(f'{oid} 响应Mock不符合Schema: {e.message}')
member_contracts=list((ROOT/'project/member_contracts').glob('*.yaml'))
if len(member_contracts)!=9: err(f'成员契约数量应为9，实际{len(member_contracts)}')
known=set(ops)
for p in member_contracts:
    d=yaml.safe_load(p.read_text(encoding='utf-8'))
    for group in d['api_scope'].values():
        for oid in group:
            if oid not in known: err(f'{p.name} 引用不存在接口 {oid}')
    for rel in d['required_reading']:
        if not (ROOT/rel).exists(): err(f'{p.name} 必读文件不存在 {rel}')
reg=yaml.safe_load((ROOT/'api/internal_agent_interfaces.yaml').read_text(encoding='utf-8'))
for name,meta in reg['interfaces'].items():
    for kind,key in [('request','input_schema'),('response','output_schema')]:
        sp=ROOT/meta[key]; mp=ROOT/'mocks/internal/agents'/name/f'{kind}.json'
        if not sp.exists(): err(f'{name} 缺少Schema {sp.relative_to(ROOT)}'); continue
        if not mp.exists(): err(f'{name} 缺少Mock {mp.relative_to(ROOT)}'); continue
        schema=json.loads(sp.read_text(encoding='utf-8')); mock=json.loads(mp.read_text(encoding='utf-8'))
        for e in Draft202012Validator(schema).iter_errors(mock): err(f'{name} {kind} Mock不符合Schema: {e.message}')
own=yaml.safe_load((ROOT/'project/api_ownership.yaml').read_text(encoding='utf-8'))
rows={x['operation_id']:x for x in own['operations']}
if set(rows)!=known: err('api_ownership.yaml 与OpenAPI操作集合不一致')
flows=yaml.safe_load((ROOT/'project/user_flows.yaml').read_text(encoding='utf-8'))
for flow in flows['flows']:
    for step in flow['steps']:
        if not step.get('output_ids'): err(f"流程 {flow['workflow_name']} 步骤 {step['sequence_no']} 缺少output_ids")
        if 'operation_id' in step and step['operation_id'] not in known: err(f"流程引用不存在接口 {step['operation_id']}")
for rel in ['api/error_codes.yaml','api/field_dictionary.yaml','database/schema.sql','project/interface_owners.yaml','project/work_packages.yaml','contracts/typescript/contracts.ts','contracts/python/models.py']:
    if not (ROOT/rel).exists(): err(f'兼容或基础文件缺失: {rel}')
if errors:
    print('V6契约检查失败：')
    for x in errors: print('-',x)
    sys.exit(1)
print(f'V6契约检查通过：{len(ops)}个公开接口及其Mock、9份成员契约、{len(reg["interfaces"])}个智能体接口。')
