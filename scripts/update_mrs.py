#!/usr/bin/env python3
"""Update categorized Mihomo MRS rule sets from base payloads + upstream Clash lists."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MRS_DIR = ROOT / "Clash" / "MRS"
BASE_DIR = MRS_DIR / "sources" / "base"
UPSTREAMS_FILE = MRS_DIR / "sources" / "upstreams.yml"
MANUAL_REJECT_FILE = ROOT / "lanjie.list"
MANUAL_DIRECT_FILE = ROOT / "zhilian.list"

CATEGORIES = {
    "ai-platform": "AI平台",
    "social-chat": "社交聊天",
    "developer-platform": "开发平台",
    "foreign-media": "国外媒体",
    "microsoft-apple": "微软苹果",
    "direct": "全球直连",
    "reject": "全球拦截",
}

SUPPORTED_DOMAIN = {"DOMAIN", "DOMAIN-SUFFIX"}
SUPPORTED_IP = {"IP-CIDR", "IP-CIDR6"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--mihomo", default="mihomo", help="mihomo executable path")
    p.add_argument("--dry-run", action="store_true", help="parse and summarize only")
    return p.parse_args()


def read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.strip().startswith("#")]


def load_upstreams(path: Path) -> dict[str, list[dict[str, str]]]:
    """Tiny YAML reader for the specific upstreams.yml structure; no PyYAML dependency."""
    current_category = None
    current_item = None
    data: dict[str, list[dict[str, str]]] = defaultdict(list)
    in_sources = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s == "sources:":
            in_sources = True
            continue
        if not in_sources:
            continue
        if re.match(r"^  [A-Za-z0-9_.-]+:$", line):
            current_category = s[:-1]
            data[current_category]
            current_item = None
            continue
        if s.startswith("- name:"):
            if current_category is None:
                raise ValueError(f"name outside category: {line}")
            current_item = {"name": s.split(":", 1)[1].strip()}
            data[current_category].append(current_item)
            continue
        if s.startswith("url:"):
            if current_item is None:
                raise ValueError(f"url outside item: {line}")
            current_item["url"] = s.split(":", 1)[1].strip()
            continue
    return dict(data)


def fetch_text(url: str) -> str:
    last_error: Exception | None = None
    for attempt in range(1, 6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "aoxijy-guize-mrs-updater"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # transient GitHub/raw CDN resets are common on some networks
            last_error = e
            if attempt == 5:
                break
            time.sleep(attempt * 3)
    raise RuntimeError(f"failed to fetch {url}: {last_error}")


def normalize_rule(line: str) -> str | None:
    s = line.strip()
    if not s or s.startswith("#"):
        return None
    if s.startswith("- "):
        s = s[2:].strip().strip("'\"")
    return s or None


def domain_suffix(value: str) -> str:
    """DOMAIN-SUFFIX 的 mihomo domain payload 写法。

    mihomo(rule-providers, behavior=domain, format=mrs) 中：
      `x`   只精确匹配 x
      `.x`  只匹配 x 的子域名（实测不匹配 x 本身）
      `+.x` 同时匹配 x 本身及其所有子域名
    所以 DOMAIN-SUFFIX 必须写成 `+.x`，否则顶级域名会漏掉。
    """
    return "+." + value.strip().lstrip("+.")


def normalize_domain_payload(item: str) -> str:
    """规范化基础规则文件（sources/base/*-domain.txt）里的域名条目：

    这些文件用「带点 = 后缀、不带点 = 精确」表达原始规则，
    其中 `.x` 在 mihomo 里只匹配子域名，需要补成 `+.x` 才能覆盖 x 本身。
    """
    s = item.strip()
    if s.startswith("+."):
        return s
    if s.startswith("."):
        return "+" + s
    return s


def add_rule(category: str, rule: str, domains: dict[str, list[str]], ips: dict[str, list[str]], unsupported: list[dict[str, str]], source: str) -> None:
    parts = [p.strip() for p in rule.split(",")]
    if len(parts) < 2:
        return
    typ, value = parts[0], parts[1]

    # GitHub Copilot / Microsoft Copilot 属于 AI 平台，不放在普通 GitHub 社交聊天分类。
    if "copilot" in value.lower():
        category = "ai-platform"

    if typ == "DOMAIN":
        domains[category].append(value)
    elif typ == "DOMAIN-SUFFIX":
        domains[category].append(domain_suffix(value))
    elif typ in SUPPORTED_IP:
        ips[category].append(value)
    else:
        unsupported.append({"source": source, "category": category, "rule": rule})


def unique_sorted(items: list[str]) -> list[str]:
    return sorted(set(i.strip() for i in items if i.strip()), key=lambda x: (x.lstrip("+."), x))


def write_payloads(domains: dict[str, list[str]], ips: dict[str, list[str]]) -> None:
    for category in CATEGORIES:
        d = unique_sorted(domains.get(category, []))
        i = unique_sorted(ips.get(category, []))
        domain_path = MRS_DIR / f"{category}-domain.txt"
        ip_path = MRS_DIR / f"{category}-ipcidr.txt"
        if d:
            domain_path.write_text("\n".join(d) + "\n", encoding="utf-8")
        elif domain_path.exists():
            domain_path.unlink()
        if i:
            ip_path.write_text("\n".join(i) + "\n", encoding="utf-8")
        elif ip_path.exists():
            ip_path.unlink()


def compile_mrs(mihomo: str) -> None:
    for txt in sorted(MRS_DIR.glob("*-domain.txt")):
        out = txt.with_suffix(".mrs")
        subprocess.run([mihomo, "convert-ruleset", "domain", "text", str(txt), str(out)], check=True)
        txt.unlink()
    for txt in sorted(MRS_DIR.glob("*-ipcidr.txt")):
        out = txt.with_suffix(".mrs")
        subprocess.run([mihomo, "convert-ruleset", "ipcidr", "text", str(txt), str(out)], check=True)
        txt.unlink()


def main() -> int:
    args = parse_args()
    domains: dict[str, list[str]] = defaultdict(list)
    ips: dict[str, list[str]] = defaultdict(list)
    unsupported: list[dict[str, str]] = []
    source_counts = Counter()

    for category in CATEGORIES:
        domains[category].extend(normalize_domain_payload(x) for x in read_lines(BASE_DIR / f"{category}-domain.txt"))
        ips[category].extend(read_lines(BASE_DIR / f"{category}-ipcidr.txt"))

    # 手工拦截源：用户以后直接改仓库根目录 lanjie.list，push 后 Actions 会重新编译 reject .mrs。
    if MANUAL_REJECT_FILE.exists():
        for raw in MANUAL_REJECT_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
            rule = normalize_rule(raw)
            if not rule:
                continue
            add_rule("reject", rule, domains, ips, unsupported, "manual-lanjie")
            source_counts["manual-lanjie"] += 1

    # 手工直连源：用户以后直接改仓库根目录 zhilian.list，push 后 Actions 会重新编译 direct .mrs。
    if MANUAL_DIRECT_FILE.exists():
        for raw in MANUAL_DIRECT_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
            rule = normalize_rule(raw)
            if not rule:
                continue
            add_rule("direct", rule, domains, ips, unsupported, "manual-zhilian")
            source_counts["manual-zhilian"] += 1

    upstreams = load_upstreams(UPSTREAMS_FILE)
    for category, sources in upstreams.items():
        if category not in CATEGORIES:
            raise ValueError(f"unknown category in upstreams: {category}")
        for source in sources:
            name = source["name"]
            text = fetch_text(source["url"])
            for raw in text.splitlines():
                rule = normalize_rule(raw)
                if not rule:
                    continue
                add_rule(category, rule, domains, ips, unsupported, name)
                source_counts[name] += 1

    summary = {
        "categories": CATEGORIES,
        "domain_files": {k: len(unique_sorted(v)) for k, v in domains.items() if unique_sorted(v)},
        "ipcidr_files": {k: len(unique_sorted(v)) for k, v in ips.items() if unique_sorted(v)},
        "upstream_rule_lines": dict(source_counts),
        "unsupported_count": len(unsupported),
    }

    if args.dry_run:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    write_payloads(domains, ips)
    compile_mrs(args.mihomo)

    with (MRS_DIR / "unsupported-classical-only.list").open("w", encoding="utf-8") as w:
        w.write("# 这些规则未写入 domain/ipcidr .mrs，需要 classical 行为或保留在主配置 rules 中。\n")
        for item in unsupported:
            w.write(f"# source: {item['source']} category: {item['category']}\n{item['rule']}\n")

    (MRS_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
