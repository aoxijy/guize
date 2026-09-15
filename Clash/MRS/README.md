# Mihomo MRS 分类规则集

来源：原 `zhu111.yaml` 的 `rules:` 段 + 仓库根目录 `lanjie.list` / `zhilian.list` + `sources/upstreams.yml` 中配置的上游 Clash 规则源。这里只保存规则和编译后的 `.mrs`，不包含任何代理节点、密码、UUID 或服务器配置。

## 分类文件

| 分类 | domain .mrs | domain 规则数 | ipcidr .mrs | ipcidr 规则数 |
|---|---:|---:|---:|---:|
| AI平台 | `ai-platform-domain.mrs` | 84 | `ai-platform-ipcidr.mrs` | 2 |
| 社交聊天 | `social-chat-domain.mrs` | 813 | `social-chat-ipcidr.mrs` | 80 |
| 开发平台 | `developer-platform-domain.mrs` | 133 | `developer-platform-ipcidr.mrs` | 22 |
| 国外媒体 | `foreign-media-domain.mrs` | 34124 | `foreign-media-ipcidr.mrs` | 1243 |
| 微软苹果 | `microsoft-apple-domain.mrs` | 2236 | `microsoft-apple-ipcidr.mrs` | 13 |
| 全球直连 | `direct-domain.mrs` | 2247 | `direct-ipcidr.mrs` | 7663 |
| 全球拦截 | `reject-domain.mrs` | 159 | - | 0 |

## 自动更新

- GitHub Actions：`.github/workflows/update-mrs.yml`。
- 默认每天 UTC `02:17` 运行一次，也支持手动 `workflow_dispatch`。
- 当你 push 修改 `lanjie.list`、`zhilian.list`、`Clash/MRS/sources/**`、`scripts/update_mrs.py` 或 workflow 文件时，也会自动触发。
- 更新逻辑：读取 `sources/base/*.txt` 作为本仓库基础规则，读取根目录 `lanjie.list` 作为手工全球拦截源、`zhilian.list` 作为手工全球直连源，再拉取 `sources/upstreams.yml` 中的上游，去重合并后用 `mihomo convert-ruleset` 重新生成 `.mrs`。
- 每次运行都会发布/覆盖 `mrs-latest` Release，生成固定下载地址；没有规则变化也会刷新 Release 资产。

## 已配置上游分类

- AI平台：OpenAI / ChatGPT、Claude、Gemini、Microsoft Copilot、Bing，并把包含 `copilot` 的 GitHub 相关规则归入 AI 平台。
- 社交聊天：WhatsApp、Telegram、Twitter / X、Facebook、Instagram。
- 开发平台：GitHub、GitLab、Docker、JetBrains、Cloudflare、Vercel、SourceForge、GitBook。
- 国外媒体：YouTube、Netflix、Hulu、Disney / Disney+、Spotify、Twitch、HBO、Prime Video、Bahamut。
- 微软苹果：Apple、Microsoft、OneDrive、Xbox。
- 全球直连：仓库根目录 `zhilian.list` 手工源 + 基础直连规则。
- 全球拦截：仓库根目录 `lanjie.list` 手工源 + Adobe 上游（blackmatrix7、ACL4SSR）。`lanjie.list` 中已有 CorelDRAW/Corel 相关规则；CorelDRAW 和 SOLIDWORKS 暂未找到常用规则库里的稳定独立上游。
- 后续要增加其它服务，只需向 `sources/upstreams.yml` 添加对应 URL；手工拦截规则可直接加到根目录 `lanjie.list`；手工直连规则可直接加到根目录 `zhilian.list`。

## Release 固定下载地址

Release 标签固定为 `mrs-latest`，Actions 每次自动更新后会覆盖上传最新 `.mrs`。

- AI平台 domain: https://github.com/aoxijy/guize/releases/latest/download/ai-platform-domain.mrs
- AI平台 ipcidr: https://github.com/aoxijy/guize/releases/latest/download/ai-platform-ipcidr.mrs
- 社交聊天 domain: https://github.com/aoxijy/guize/releases/latest/download/social-chat-domain.mrs
- 社交聊天 ipcidr: https://github.com/aoxijy/guize/releases/latest/download/social-chat-ipcidr.mrs
- 开发平台 domain: https://github.com/aoxijy/guize/releases/latest/download/developer-platform-domain.mrs
- 开发平台 ipcidr: https://github.com/aoxijy/guize/releases/latest/download/developer-platform-ipcidr.mrs
- 国外媒体 domain: https://github.com/aoxijy/guize/releases/latest/download/foreign-media-domain.mrs
- 国外媒体 ipcidr: https://github.com/aoxijy/guize/releases/latest/download/foreign-media-ipcidr.mrs
- 微软苹果 domain: https://github.com/aoxijy/guize/releases/latest/download/microsoft-apple-domain.mrs
- 微软苹果 ipcidr: https://github.com/aoxijy/guize/releases/latest/download/microsoft-apple-ipcidr.mrs
- 全球直连 domain: https://github.com/aoxijy/guize/releases/latest/download/direct-domain.mrs
- 全球直连 ipcidr: https://github.com/aoxijy/guize/releases/latest/download/direct-ipcidr.mrs
- 全球拦截 domain: https://github.com/aoxijy/guize/releases/latest/download/reject-domain.mrs

## 转换规则

- `DOMAIN` → domain payload 原域名（精确匹配，只匹配该域名本身）。
- `DOMAIN-SUFFIX` → domain payload `+.域名`。
  - ⚠️ mihomo 的 `behavior: domain` 规则集里，`.域名` **只匹配子域名、不匹配域名本身**，`+.域名` 才同时匹配域名本身及其所有子域名。
  - 所以所有后缀类规则（含 `sources/base/*-domain.txt` 里以 `.` 开头的条目）统一编译为 `+.域名`，否则 `openai.com`、`baidu.com` 这类顶级域名会漏掉、被丢给 `MATCH` 兜底。
- `IP-CIDR` / `IP-CIDR6` → ipcidr payload，去除策略组和 `no-resolve` 参数。
- `DOMAIN-KEYWORD`、`PROCESS-NAME`、`GEOIP`、`MATCH` 等不能安全写入 domain/ipcidr `.mrs`，会保存在 `unsupported-classical-only.list`。

## rule-providers 示例

```yaml
rule-providers:
  ai-platform-domain:
    type: http
    behavior: domain
    format: mrs
    url: https://github.com/aoxijy/guize/releases/latest/download/ai-platform-domain.mrs
    path: ./ruleset/ai-platform-domain.mrs
    interval: 86400
  ai-platform-ipcidr:
    type: http
    behavior: ipcidr
    format: mrs
    url: https://github.com/aoxijy/guize/releases/latest/download/ai-platform-ipcidr.mrs
    path: ./ruleset/ai-platform-ipcidr.mrs
    interval: 86400
  social-chat-domain:
    type: http
    behavior: domain
    format: mrs
    url: https://github.com/aoxijy/guize/releases/latest/download/social-chat-domain.mrs
    path: ./ruleset/social-chat-domain.mrs
    interval: 86400
  social-chat-ipcidr:
    type: http
    behavior: ipcidr
    format: mrs
    url: https://github.com/aoxijy/guize/releases/latest/download/social-chat-ipcidr.mrs
    path: ./ruleset/social-chat-ipcidr.mrs
    interval: 86400
  developer-platform-domain:
    type: http
    behavior: domain
    format: mrs
    url: https://github.com/aoxijy/guize/releases/latest/download/developer-platform-domain.mrs
    path: ./ruleset/developer-platform-domain.mrs
    interval: 86400
  developer-platform-ipcidr:
    type: http
    behavior: ipcidr
    format: mrs
    url: https://github.com/aoxijy/guize/releases/latest/download/developer-platform-ipcidr.mrs
    path: ./ruleset/developer-platform-ipcidr.mrs
    interval: 86400
  foreign-media-domain:
    type: http
    behavior: domain
    format: mrs
    url: https://github.com/aoxijy/guize/releases/latest/download/foreign-media-domain.mrs
    path: ./ruleset/foreign-media-domain.mrs
    interval: 86400
  foreign-media-ipcidr:
    type: http
    behavior: ipcidr
    format: mrs
    url: https://github.com/aoxijy/guize/releases/latest/download/foreign-media-ipcidr.mrs
    path: ./ruleset/foreign-media-ipcidr.mrs
    interval: 86400
  microsoft-apple-domain:
    type: http
    behavior: domain
    format: mrs
    url: https://github.com/aoxijy/guize/releases/latest/download/microsoft-apple-domain.mrs
    path: ./ruleset/microsoft-apple-domain.mrs
    interval: 86400
  microsoft-apple-ipcidr:
    type: http
    behavior: ipcidr
    format: mrs
    url: https://github.com/aoxijy/guize/releases/latest/download/microsoft-apple-ipcidr.mrs
    path: ./ruleset/microsoft-apple-ipcidr.mrs
    interval: 86400
  direct-domain:
    type: http
    behavior: domain
    format: mrs
    url: https://github.com/aoxijy/guize/releases/latest/download/direct-domain.mrs
    path: ./ruleset/direct-domain.mrs
    interval: 86400
  direct-ipcidr:
    type: http
    behavior: ipcidr
    format: mrs
    url: https://github.com/aoxijy/guize/releases/latest/download/direct-ipcidr.mrs
    path: ./ruleset/direct-ipcidr.mrs
    interval: 86400
  reject-domain:
    type: http
    behavior: domain
    format: mrs
    url: https://github.com/aoxijy/guize/releases/latest/download/reject-domain.mrs
    path: ./ruleset/reject-domain.mrs
    interval: 86400
```
