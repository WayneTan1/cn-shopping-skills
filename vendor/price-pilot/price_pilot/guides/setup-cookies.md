# Cookie Setup Guide

Use this guide when direct marketplace access needs a browser login state.

## Recommended export method

1. Log in to the target platform in your browser.
2. Export cookies with a browser extension such as Cookie-Editor.
3. Save the exported JSON locally.
4. Register it with Price Pilot:

```bash
price-pilot config cookie import <platform> --file /path/to/cookies.json
price-pilot config cookie validate <platform> --file /path/to/cookies.json
price-pilot config cookie probe <platform>
price-pilot config cookie status
```

Supported platforms:

- `jd`
- `taobao`
- `pinduoduo`
- `xianyu`
- `zhuanzhuan`

## Notes

- Prefer a dedicated account over a primary personal account.
- Refresh the export when the platform invalidates login state.
- Keep cookie files on the local machine only.
- Use `price-pilot config cookie validate <platform> --file ...` for a dry run before importing.
- Use `price-pilot config cookie probe <platform>` after importing to test whether login likely still works.
