import json
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    p = root / 'docs' / 'api' / 'openapi.json'
    doc = json.loads(p.read_text(encoding='utf-8'))
    paths = list(doc.get('paths', {}).keys())
    print(f'paths {len(paths)}')
    for x in paths:
        print(x)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
