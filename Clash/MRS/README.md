# Mihomo MRS 分类规则集

来源：原 `zhu111.yaml` 的 `rules:` 段 + `sources/upstreams.yml` 中配置的上游 Clash 规则源。这里只保存规则和编译后的 `.mrs`，不包含任何代理节点、密码、UUID 或服务器配置。

## 分类文件

| 分类 | domain .mrs | domain 规则数 | ipcidr .mrs | ipcidr 规则数 |
|---|---:|---:|---:|---:|
| AI平台 | `ai-platform-domain.mrs` | 84 | `ai-platform-ipcidr.mrs` | 2 |
| 社交聊天 | `social-chat-domain.mrs` | 842 | `social-chat-ipcidr.mrs` | 80 |
| 国外媒体 | `foreign-media-domain.mrs` | 34124 | `foreign-media-ipcidr.mrs` | 1243 |
| 微软苹果 | `microsoft-apple-domain.mrs` | 2236 | `microsoft-apple-ipcidr.mrs` | 13 |
| 全球直连 | `direct-domain.mrs` | 2247 | `direct-ipcidr.mrs` | 7663 |
| 全球拦截 | `reject-domain.mrs` | 156 | - | 0 |

## 自动更新

- GitHub Actions：`.github/workflows/update-mrs.yml`。
- 默认每天 UTC `02:17` 运行一次，也支持手动 `workflow_dispatch`。
- 更新逻辑：读取 `sources/base/*.txt` 作为本仓库基础规则，再拉取 `sources/upstreams.yml` 中的上游，去重合并后用 `mihomo convert-ruleset` 重新生成 `.mrs`。
- 如果上游新增域名或 IP，Actions 会自动合并到对应分类的 `.mrs`；没有变化则不提交。

## 已配置上游分类

- AI平台：OpenAI / ChatGPT、Claude、Gemini、Microsoft Copilot、Bing，并把包含 `copilot` 的 GitHub 相关规则归入 AI 平台。
- 社交聊天：WhatsApp、Telegram、GitHub、Twitter / X、Facebook、Instagram。
- 国外媒体：YouTube、Netflix、Hulu、Disney / Disney+、Spotify、Twitch、HBO、Prime Video、Bahamut。
- 微软苹果：Apple、Microsoft、OneDrive、Xbox。
- 后续要增加其它服务，只需向 `sources/upstreams.yml` 添加对应 URL。

## 转换规则

- `DOMAIN` → domain payload 原域名。
- `DOMAIN-SUFFIX` → domain payload `.域名`。
- `IP-CIDR` / `IP-CIDR6` → ipcidr payload，去除策略组和 `no-resolve` 参数。
- `DOMAIN-KEYWORD`、`PROCESS-NAME`、`GEOIP`、`MATCH` 等不能安全写入 domain/ipcidr `.mrs`，会保存在 `unsupported-classical-only.list`。


## Release 固定下载地址

Release 标签固定为 `mrs-latest`，Actions 每次自动更新后会覆盖上传最新 `.mrs`。

- AI平台 domain: https://github.com/aoxijy/guize/releases/latest/download/ai-platform-domain.mrs
- AI平台 ipcidr: https://github.com/aoxijy/guize/releases/latest/download/ai-platform-ipcidr.mrs
- 社交聊天 domain: https://github.com/aoxijy/guize/releases/latest/download/social-chat-domain.mrs
- 社交聊天 ipcidr: https://github.com/aoxijy/guize/releases/latest/download/social-chat-ipcidr.mrs
- 国外媒体 domain: https://github.com/aoxijy/guize/releases/latest/download/foreign-media-domain.mrs
- 国外媒体 ipcidr: https://github.com/aoxijy/guize/releases/latest/download/foreign-media-ipcidr.mrs
- 微软苹果 domain: https://github.com/aoxijy/guize/releases/latest/download/microsoft-apple-domain.mrs
- 微软苹果 ipcidr: https://github.com/aoxijy/guize/releases/latest/download/microsoft-apple-ipcidr.mrs
- 全球直连 domain: https://github.com/aoxijy/guize/releases/latest/download/direct-domain.mrs
- 全球直连 ipcidr: https://github.com/aoxijy/guize/releases/latest/download/direct-ipcidr.mrs
- 全球拦截 domain: https://github.com/aoxijy/guize/releases/latest/download/reject-domain.mrs

## rule-providers 示例

```yaml
rule-providers:
  ai-platform-domain:
    type: file
    behavior: domain
    format: mrs
    path: ./Clash/MRS/ai-platform-domain.mrs
  ai-platform-ipcidr:
    type: file
    behavior: ipcidr
    format: mrs
    path: ./Clash/MRS/ai-platform-ipcidr.mrs
  social-chat-domain:
    type: file
    behavior: domain
    format: mrs
    path: ./Clash/MRS/social-chat-domain.mrs
  social-chat-ipcidr:
    type: file
    behavior: ipcidr
    format: mrs
    path: ./Clash/MRS/social-chat-ipcidr.mrs
  foreign-media-domain:
    type: file
    behavior: domain
    format: mrs
    path: ./Clash/MRS/foreign-media-domain.mrs
  foreign-media-ipcidr:
    type: file
    behavior: ipcidr
    format: mrs
    path: ./Clash/MRS/foreign-media-ipcidr.mrs
  microsoft-apple-domain:
    type: file
    behavior: domain
    format: mrs
    path: ./Clash/MRS/microsoft-apple-domain.mrs
  microsoft-apple-ipcidr:
    type: file
    behavior: ipcidr
    format: mrs
    path: ./Clash/MRS/microsoft-apple-ipcidr.mrs
  direct-domain:
    type: file
    behavior: domain
    format: mrs
    path: ./Clash/MRS/direct-domain.mrs
  direct-ipcidr:
    type: file
    behavior: ipcidr
    format: mrs
    path: ./Clash/MRS/direct-ipcidr.mrs
  reject-domain:
    type: file
    behavior: domain
    format: mrs
    path: ./Clash/MRS/reject-domain.mrs
```
