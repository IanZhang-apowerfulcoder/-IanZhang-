from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

EXCLUDED_DIRS = {'.git', '.pytest_cache', '__pycache__', '.mypy_cache', '.ruff_cache', '.venv', 'venv', 'node_modules'}
EXCLUDED_NAMES = {'MANIFEST.json', 'MANIFEST.txt', '.DS_Store'}
EXCLUDED_SUFFIXES = {'.pyc', '.pyo'}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def generate(target: Path, package: str, version: str) -> dict:
    files = []
    for path in sorted(target.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(target)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if path.name in EXCLUDED_NAMES or path.suffix in EXCLUDED_SUFFIXES:
            continue
        files.append({
            'path': rel.as_posix(),
            'size_bytes': path.stat().st_size,
            'sha256': digest(path),
        })
    manifest = {
        'package': package,
        'version': version,
        'generated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'file_count': len(files),
        'total_size_bytes': sum(x['size_bytes'] for x in files),
        'files': files,
    }
    (target / 'MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (target / 'MANIFEST.txt').write_text(
        ''.join(f"{x['sha256']}  {x['size_bytes']:>12}  {x['path']}\n" for x in files),
        encoding='utf-8',
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', required=True)
    parser.add_argument('--package', required=True)
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    result = generate(Path(args.target).resolve(), args.package, args.version)
    print(json.dumps({k: result[k] for k in ('package','version','file_count','total_size_bytes')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
