from __future__ import annotations

import csv
import hashlib
import shutil
import tempfile
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'member-packs-v7.0'
MATRIX = yaml.safe_load((ROOT / 'project/member_reference_matrix.yaml').read_text(encoding='utf-8'))

EXCLUDED_DIRS = {'.pytest_cache', '__pycache__', '.git', 'node_modules', '.venv', 'venv'}
EXCLUDED_SUFFIXES = {'.pyc', '.pyo'}

COMMON_PATHS = [
    'README.md',
    'CONTRIBUTING.md',
    'VERSION',
    'Makefile',
    'requirements-dev.txt',
    '.gitignore',
    'docs/00_总索引.md',
    'docs/03_成员必读文件矩阵.md',
    'docs/14_测试与验收标准.md',
    'docs/16_任务卡与PR规则.md',
    'docs/19_成员入门步骤.md',
    'docs/20_开发启动清单.md',
    'docs/30_跨成员联调顺序.md',
    'docs/40_比赛提交映射与最终交付清单.md',
    'project/agent_blueprint.yaml',
    'project/learning_workflow.yaml',
    'project/qa_workflow.yaml',
    'project/knowledge_maintenance_workflow.yaml',
    'project/tool_catalog.yaml',
    'project/end_to_end_contract_matrix.yaml',
    'project/member_reference_matrix.yaml',
    'project/member_stage_matrix.csv',
    'project/frontend_page_api_matrix.yaml',
    'templates',
]

EXTRAS = {
    'P1': ['docs', 'project', 'api', 'contracts', 'database', 'reports', 'prototypes', 'tasks',
           'knowledge-bases/enterprise-rag-engineering-v2'],
    'P2': ['services/agent_runtime', 'services/agents', 'services/retrieval', 'packages',
           'mocks/workflows', 'api/internal_openapi.yaml', 'api/internal_agent_interfaces.yaml'],
    'P3': ['services/agents', 'services/evaluation', 'mocks/internal/agents',
           'knowledge-bases/enterprise-rag-engineering-v2/data/assessment_blueprints.json',
           'knowledge-bases/enterprise-rag-engineering-v2/data/learner_profiles.json',
           'knowledge-bases/enterprise-rag-engineering-v2/data/rubrics.json'],
    'P4': ['apps/web', 'prototypes', 'api/openapi.yaml', 'contracts/typescript', 'mocks/workflows'],
    'P5': ['apps/api', 'api', 'database/schema.sql', 'infra', 'mocks/http', 'mocks/workflows'],
    'P6': ['database', 'infra', 'project/user_flows.yaml', 'project/learning_workflow.yaml',
           'project/knowledge_maintenance_workflow.yaml', 'mocks/workflows'],
    'P7': ['knowledge-bases/enterprise-rag-engineering-v2', 'services/retrieval',
           'api/knowledge_domain_api.yaml', 'database/migrations/007_adaptive_parallel_rag.sql'],
    'P8': ['services/agents', 'mocks/internal/agents',
           'knowledge-bases/enterprise-rag-engineering-v2/submission/vertical_domain_knowledge_base_slice.json',
           'knowledge-bases/enterprise-rag-engineering-v2/data/personalized_resource_examples.json',
           'knowledge-bases/enterprise-rag-engineering-v2/data/task_bank.json',
           'knowledge-bases/enterprise-rag-engineering-v2/data/question_bank.json'],
    'P9': ['reports', 'mocks', 'knowledge-bases/enterprise-rag-engineering-v2/reports',
           'knowledge-bases/enterprise-rag-engineering-v2/tests',
           'knowledge-bases/enterprise-rag-engineering-v2/submission', '.github'],
}


def ignored(path: Path) -> bool:
    normalized = path.as_posix()
    if normalized.endswith('reports/member_pack_checksums.csv'):
        return True
    if path.name in {'MANIFEST.json', 'MANIFEST.txt'} and len(path.parts) == 1:
        return True
    return any(part in EXCLUDED_DIRS for part in path.parts) or path.suffix in EXCLUDED_SUFFIXES or path.name == '.DS_Store'


def copy_path(relative: str, target_root: Path) -> None:
    src = ROOT / relative
    if not src.exists():
        raise FileNotFoundError(relative)
    dst = target_root / relative
    if src.is_dir():
        for item in sorted(src.rglob('*')):
            if ignored(item.relative_to(src)):
                continue
            rel_inside = item.relative_to(src)
            out = dst / rel_inside
            if item.is_dir():
                out.mkdir(parents=True, exist_ok=True)
            elif item.is_file() and item.suffix != '.zip':
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, out)
    else:
        if src.suffix == '.zip' or ignored(src.relative_to(ROOT)):
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def zip_directory(source: Path, destination: Path) -> None:
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for file in sorted(source.rglob('*')):
            if file.is_file() and not ignored(file.relative_to(source)):
                zf.write(file, file.relative_to(source.parent).as_posix())


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob('*.zip'):
        old.unlink()
    for old in OUT.glob('*.sha256'):
        old.unlink()

    checksum_rows = []
    with tempfile.TemporaryDirectory(prefix='member-packs-', dir=str(ROOT.parent)) as tmp:
        tmp_root = Path(tmp)
        for member in MATRIX['members']:
            code = member['member_code']
            name = member['member']
            role = member['role']
            folder_name = f'{code}_{name}_v7.0_独立开发包'
            pack_root = tmp_root / folder_name
            pack_root.mkdir(parents=True)

            # Resolve member folder.
            member_dir = next(ROOT.glob(f'members/{code}_*'))
            paths = list(COMMON_PATHS)
            paths.extend(member.get('source_docs', []))
            paths.extend(member.get('contracts', []))
            paths.append(member_dir.relative_to(ROOT).as_posix())
            paths.extend(EXTRAS.get(code, []))
            for stage in range(8):
                paths.append(f'tasks/S{stage}/{code}.md')

            # Mock paths are explicitly curated per member.
            mock_doc = yaml.safe_load((member_dir / 'mock_index.yaml').read_text(encoding='utf-8')) or {}
            paths.extend(mock_doc.get('http_mocks', []) or [])
            paths.extend(mock_doc.get('internal_mocks', []) or [])
            paths.extend(mock_doc.get('workflow_mocks', []) or [])

            seen = set()
            for rel in paths:
                if rel in seen:
                    continue
                seen.add(rel)
                copy_path(rel, pack_root)

            task_links = '\n'.join(f'- `tasks/S{s}/{code}.md`' for s in range(8))
            source_links = '\n'.join(f'- `{x}`' for x in member.get('source_docs', []))
            contract_links = '\n'.join(f'- `{x}`' for x in member.get('contracts', []))
            reviewer_text = '、'.join(member.get('reviewers', []))
            (pack_root / 'PACK_INFO.md').write_text(f'''# {code} {name} 独立开发包 v7.0\n\n## 长期角色\n\n{role}\n\n## 使用顺序\n\n1. 阅读 `README.md`；\n2. 阅读 `members/{member_dir.name}/00_开始这里.md`；\n3. 阅读 `members/{member_dir.name}/00_完整开发文件.md`；\n4. 只领取当前阶段任务卡；\n5. 以 API、Schema、数据库和任务卡为事实标准；\n6. 提交 PR、测试日志、接口样例、已知限制和回滚方案。\n\n## 专项设计文件\n\n{source_links}\n\n## 必须遵守的契约\n\n{contract_links}\n\n## 八阶段任务\n\n{task_links}\n\n## 主要复核人\n\n{reviewer_text}\n\n## 禁止事项\n\n- 不得自行增加、删除或重连核心 Agent；\n- 不得绕过后端直接写权威数据库；\n- 不得私自改变冻结字段或接口；\n- 不得把 Mock、规划或未验证指标当成最终成果。\n''', encoding='utf-8')

            zip_path = OUT / f'{code}_{name}_独立开发包_v7.0.zip'
            zip_directory(pack_root, zip_path)
            digest = sha256(zip_path)
            (OUT / f'{zip_path.name}.sha256').write_text(f'{digest}  {zip_path.name}\n', encoding='utf-8')
            checksum_rows.append({
                'member_code': code,
                'member': name,
                'role': role,
                'filename': zip_path.name,
                'sha256': digest,
                'size_bytes': zip_path.stat().st_size,
            })

    with (ROOT / 'reports/member_pack_checksums.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(checksum_rows[0].keys()))
        writer.writeheader()
        writer.writerows(checksum_rows)

    table = '\n'.join(
        f"| {r['member_code']} | {r['member']} | `{r['filename']}` | {r['size_bytes'] / 1024 / 1024:.2f} MB | `{r['sha256'][:16]}...` |"
        for r in checksum_rows
    )
    (OUT / 'README.md').write_text(f'''# 九名成员独立开发包 v7.0\n\n这些压缩包从当前项目事实标准自动生成。接口、Schema 或任务发生变化后，应重新运行：\n\n```bash\npython scripts/build_member_packs.py\n```\n\n| 编号 | 成员 | 文件 | 大小 | SHA-256 摘要 |\n|---|---|---|---:|---|\n{table}\n\n完整哈希见 `reports/member_pack_checksums.csv` 和各自 `.sha256` 文件。\n''', encoding='utf-8')
    print(f'built {len(checksum_rows)} member packs')


if __name__ == '__main__':
    main()
