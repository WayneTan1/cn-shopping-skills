# 中国电商购物技能包

面向 Windows、Microsoft Edge 和支持 MCP 的 Codex 环境，包含淘宝/天猫、京东、拼多多购物流程的两个技能，以及本地浏览器桥接和 Price Pilot 源码。

技能指令覆盖同规格比价、免费优惠券查找与领取、抵扣核验、配送地区检查、正常访问异常恢复，以及已获用户授权的淘宝/京东加购与拼多多商品收藏。结算和付款需要单独处理，不属于本包授权范围。平台登录及验证码由本人完成。

## 包含内容

- `skills/cn-shopping-cart/`：商品核验、优惠券、配送、加购与收藏操作指引。
- `skills/cn-shopping-compare/`：候选商品筛选、相同 SKU 分组和价格比较。
- `tools/shopping-browser/`：Playwright MCP 桥接、会话保持和比较工具。
- `vendor/price-pilot/`：Price Pilot 0.3.0 源码及原许可证。
- `scripts/install.ps1`：依赖安装、技能备份与复制、生成本机连接信息。
- `VALIDATION.md`、`PACKAGE_MANIFEST.json`：本次发布的检查范围及文件校验值。

本包不包含账户、浏览器资料、Cookie、订单、购物证据或已安装依赖。首次安装依赖需要联网；ZIP 本身不是完全离线的浏览器发行版。

## 安装

前提：Windows、Microsoft Edge、Node.js 22 或更新的 LTS 版本，以及 Python 3.10+。打包时使用 Node.js 24 和 Python 3.12 检查。

将 ZIP 解压到一个长期保留的位置，进入解压后的目录，然后运行：

```powershell
.\scripts\install.ps1 -PythonExecutable 'C:\Path\To\Python\python.exe'
```

如果 `python` 已指向真实的 Python 解释器，可省略 `-PythonExecutable`。脚本会执行 `npm ci --ignore-scripts`、创建 `tools/.venv-price-pilot`，并从本包安装 Price Pilot。不会安装或打包其他浏览器的登录信息。

技能默认安装到 `$env:CODEX_HOME/skills`，未设置时使用用户目录下的 `.codex/skills`。可用 `-CodexHomePath` 指定其他目录。已有同名技能会先移入 `skill-backups/<时间戳>/`，再复制本包版本。

安装后，在目标 Codex 目录中查看：

- `shopping-browser-install.json`：实际运行路径、Node 路径和技能路径。
- `shopping-browser-mcp.json`：标准 stdio MCP 连接参数示例。根据客户端的 MCP 配置入口添加名为 `shopping_browser` 的服务；这不是直接覆盖 Codex 配置的文件。

脚本不修改现有 MCP 配置。添加服务后重启相关客户端会话，使技能和工具被重新发现。应保留本包目录，移动目录后需重新安装以更新路径。

## 使用示例

```text
使用 $cn-shopping-compare 比较送到长沙的必品阁饺子，核对重量、冷链运费和实际可用券，按到手价排序。

使用 $cn-shopping-cart 找到选定规格，领取可直接免费领取的相关券并核验抵扣；把选中的商品加入京东购物车，拼多多则收藏商品，核对保存结果。
```

若工具尚未出现在当前会话，可先读取技能中的 `references/runtime.md`，使用安装记录给出的路径运行 `node bridge.mjs`。启动服务会使用专用 Edge 资料目录，并绑定本机 `127.0.0.1:8931` 和 `127.0.0.1:8932`。已有购物会话可能共享这两个端口，操作前先核对标签页及商品。

## 验证范围

本次打包检查见 `VALIDATION.md`。本地自动检查和合成商品用例不能证明平台当前允许访问，也不能证明某张券实际适用。领取、抵扣、加购或收藏成功均需以当次平台页面和保存结果为准。

## 依赖来源

Price Pilot 来源：<https://github.com/wby1121/price-pilot>，版本 0.3.0，源提交 `08fa9193b7e0e30125e48f85a3b369580177c265`，保留 MIT 许可证。Node 依赖通过 `package-lock.json` 固定；第三方声明见 `THIRD_PARTY_NOTICES.md`。

除附带的第三方许可外，本仓库未为其他内容额外授予开源许可。
