# mcporter Setup Guide

Use this guide when you want Price Pilot to discover marketplace MCP servers.

## What Price Pilot checks

Price Pilot looks for `mcporter.json` in common local paths and checks whether
platform aliases exist for:

- `jd`
- `taobao`
- `pinduoduo`
- `xianyu`
- `zhuanzhuan`

## Common config location

OpenClaw commonly stores it at:

```text
~/.openclaw/workspace/config/mcporter.json
```

## Example aliases

```json
{
  "mcpServers": {
    "taobao": {
      "baseUrl": "http://localhost:18081/mcp"
    },
    "xianyu": {
      "baseUrl": "http://localhost:18082/mcp"
    }
  }
}
```

## Verify

```bash
price-pilot doctor
price-pilot config show
```

