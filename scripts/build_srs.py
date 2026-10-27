#!/usr/bin/env python3
"""Compile sing-box SRS from the exact MRS artifacts published in the same run."""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def convert_payload(lines: list[str], behavior: str) -> dict:
    rule: dict[str, list[str]] = {}
    for raw in lines:
        value = raw.strip()
        if not value or value.startswith('#'):
            continue
        if behavior == 'ipcidr':
            value = str(ipaddress.ip_network(value, strict=False))
            key = 'ip_cidr'
        elif value.startswith('+.'):
            key, value = 'domain_suffix', value[2:]
        elif value.startswith('.'):
            # Leading dot in sing-box also excludes the apex domain.
            key = 'domain_suffix'
        else:
            key = 'domain'
        if behavior == 'domain' and any(c in value for c in '*+'):
            raise ValueError(f'Unsupported MRS domain pattern: {value!r}')
        rule.setdefault(key, []).append(value)
    if not rule:
        raise ValueError('Empty MRS payload')
    return {'version': 3, 'rules': [rule]}


def build(mrs_dir: Path, output_dir: Path, mihomo: str, sing_box: str) -> dict:
    inputs = sorted(mrs_dir.glob('*.mrs'))
    if not inputs:
        raise ValueError(f'No MRS files found in {mrs_dir}')
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = {}
    with tempfile.TemporaryDirectory(prefix='guize-srs-') as temp:
        temp_dir = Path(temp)
        for source in inputs:
            if source.stem.endswith('-domain'):
                behavior = 'domain'
            elif source.stem.endswith('-ipcidr'):
                behavior = 'ipcidr'
            else:
                raise ValueError(f'Unknown MRS behavior: {source.name}')
            decoded = temp_dir / source.with_suffix('.txt').name
            subprocess.run([mihomo, 'convert-ruleset', behavior, 'mrs',
                            str(source), str(decoded)], check=True)
            document = convert_payload(decoded.read_text(encoding='utf-8').splitlines(), behavior)
            json_path = temp_dir / source.with_suffix('.json').name
            json_path.write_text(json.dumps(document, ensure_ascii=False), encoding='utf-8')
            binary = temp_dir / source.with_suffix('.srs').name
            subprocess.run([sing_box, 'rule-set', 'compile', '--output', str(binary),
                            str(json_path)], check=True)
            # Decode every compiled artifact before publishing it.
            verified = temp_dir / (source.stem + '-verified.json')
            subprocess.run([sing_box, 'rule-set', 'decompile', '--output', str(verified),
                            str(binary)], check=True)
            roundtrip = json.loads(verified.read_text(encoding='utf-8'))
            if roundtrip['rules'] != document['rules']:
                raise ValueError(f'SRS round-trip differs: {source.name}')
            target = output_dir / binary.name
            target.write_bytes(binary.read_bytes())
            summary[target.name] = {
                'source': source.name,
                'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                'entries': sum(len(values) for values in document['rules'][0].values()),
            }
    # Only remove obsolete generated artifacts after the complete build succeeds.
    for old in output_dir.glob('*.srs'):
        if old.name not in summary:
            old.unlink()
    (output_dir / 'summary-srs.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mihomo', default='mihomo')
    parser.add_argument('--sing-box', default='sing-box')
    parser.add_argument('--mrs-dir', type=Path, default=ROOT / 'Clash' / 'MRS')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'SingBox' / 'SRS')
    args = parser.parse_args()
    summary = build(args.mrs_dir, args.output_dir, args.mihomo, args.sing_box)
    print(f'Compiled and verified {len(summary)} SRS rule sets.')


if __name__ == '__main__':
    main()
