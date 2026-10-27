# sing-box SRS 分类规则集

与 `Clash/MRS` 使用完全相同的规则。工作流先生成 MRS，再使用 Mihomo 官方解码器读取同批 MRS 的实际内容，最后用 sing-box 1.14.4 编译 SRS 并反解核对。不会额外拉取另一套规则源。

- 定时、手工触发、上游与手工规则变更均沿用 `.github/workflows/update-mrs.yml`。
- 与 MRS 一同覆盖发布到 `mrs-latest`，原 MRS 下载地址保持不变。
- 固定地址：`https://github.com/aoxijy/guize/releases/download/mrs-latest/<分类>-<domain或ipcidr>.srs`。
- 也支持原来的 `releases/latest/download/<文件名>.srs` 形式；明确标签的地址不受以后其他 Release 成为 latest 影响。
- 分类、是否存在 IP 文件均与同名 MRS 一致，目前 13 份。`summary-srs.json` 记录对应 MRS/SRS 的 SHA256 与解码后条目数。
- 源格式版本为 3，需 sing-box 1.11.0 或以上版本；当前构建和校验使用 1.14.4。
- `+.example.com` 转为不带前导点的 `domain_suffix`，覆盖主域与子域；精确域名保留 `domain`；`.example.com` 保留前导点，只覆盖子域。未支持的通配符会让构建失败，不会静默扩大匹配范围。
- 规则集仅包含匹配条件，不包含策略组、节点或账号。主配置中的规则顺序、出站目标及 no-resolve 语义仍由主配置控制。

## 下载地址

- [ai-platform-domain.srs](https://github.com/aoxijy/guize/releases/download/mrs-latest/ai-platform-domain.srs)
- [ai-platform-ipcidr.srs](https://github.com/aoxijy/guize/releases/download/mrs-latest/ai-platform-ipcidr.srs)
- [developer-platform-domain.srs](https://github.com/aoxijy/guize/releases/download/mrs-latest/developer-platform-domain.srs)
- [developer-platform-ipcidr.srs](https://github.com/aoxijy/guize/releases/download/mrs-latest/developer-platform-ipcidr.srs)
- [direct-domain.srs](https://github.com/aoxijy/guize/releases/download/mrs-latest/direct-domain.srs)
- [direct-ipcidr.srs](https://github.com/aoxijy/guize/releases/download/mrs-latest/direct-ipcidr.srs)
- [foreign-media-domain.srs](https://github.com/aoxijy/guize/releases/download/mrs-latest/foreign-media-domain.srs)
- [foreign-media-ipcidr.srs](https://github.com/aoxijy/guize/releases/download/mrs-latest/foreign-media-ipcidr.srs)
- [microsoft-apple-domain.srs](https://github.com/aoxijy/guize/releases/download/mrs-latest/microsoft-apple-domain.srs)
- [microsoft-apple-ipcidr.srs](https://github.com/aoxijy/guize/releases/download/mrs-latest/microsoft-apple-ipcidr.srs)
- [reject-domain.srs](https://github.com/aoxijy/guize/releases/download/mrs-latest/reject-domain.srs)
- [social-chat-domain.srs](https://github.com/aoxijy/guize/releases/download/mrs-latest/social-chat-domain.srs)
- [social-chat-ipcidr.srs](https://github.com/aoxijy/guize/releases/download/mrs-latest/social-chat-ipcidr.srs)

## sing-box 远程规则示例

```json
{
  "route": {
    "rule_set": [
      {
        "type": "remote",
        "tag": "ai-platform-domain",
        "format": "binary",
        "url": "https://github.com/aoxijy/guize/releases/download/mrs-latest/ai-platform-domain.srs",
        "download_detour": "代理组名称",
        "update_interval": "1d"
      }
    ],
    "rules": [
      {"rule_set": ["ai-platform-domain"], "action": "route", "outbound": "AI平台组名称"}
    ]
  }
}
```

替换示例中的代理组、AI 平台组名称。开启缓存文件可持久保存远程规则；下载代理自身必须能独立建立连接，避免规则下载与 DNS 相互依赖。

本地转换：

```sh
python3 scripts/build_srs.py --mihomo /path/to/mihomo --sing-box /path/to/sing-box
```
