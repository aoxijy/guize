# Mihomo MRS 分类规则集

来源：`zhu111.yaml` 的 `rules:` 段，仅提取规则，不包含任何代理节点、密码、UUID 或服务器配置。

## 分类文件

| 分类 | domain .mrs | domain 规则数 | ipcidr .mrs | ipcidr 规则数 |
|---|---:|---:|---:|---:|
| AI平台 | `ai-platform-domain.mrs` | 30 | - | 0 |
| 社交聊天 | `social-chat-domain.mrs` | 845 | `social-chat-ipcidr.mrs` | 65 |
| 国外媒体 | `foreign-media-domain.mrs` | 34484 | `foreign-media-ipcidr.mrs` | 1240 |
| 微软苹果 | `microsoft-apple-domain.mrs` | 186 | - | 0 |
| 全球直连 | `direct-domain.mrs` | 2274 | `direct-ipcidr.mrs` | 7715 |
| 全球拦截 | `reject-domain.mrs` | 157 | - | 0 |

## 转换规则

- `DOMAIN` → domain payload 原域名。
- `DOMAIN-SUFFIX` → domain payload `.域名`。
- `IP-CIDR` / `IP-CIDR6` → ipcidr payload，去除策略组和 `no-resolve` 参数。

## 未写入 .mrs 的规则

- 共 109 条保存在 `unsupported-classical-only.list`。
- 包括 `DOMAIN-KEYWORD`、`PROCESS-NAME`、`GEOIP`、`MATCH` 等只能用 classical 行为或主配置 `rules` 保留的规则。
- 已实测 mihomo `v1.19.30` 和 `v1.18.10` 的 `convert-ruleset classical` 在本环境对最小 classical 样例会 panic，因此未生成 classical `.mrs`。

## rule-providers 示例

```yaml
rule-providers:
  ai-platform-domain:
    type: file
    behavior: domain
    format: mrs
    path: ./Clash/MRS/ai-platform-domain.mrs
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
