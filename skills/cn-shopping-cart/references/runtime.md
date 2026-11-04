# 本地运行入口

先执行发布包中的 `scripts/install.ps1`。读取 `$env:CODEX_HOME/shopping-browser-install.json`，未设置 `CODEX_HOME` 时读取用户目录下的 `.codex/shopping-browser-install.json`。若使用了自定义 `-CodexHomePath`，在该目录查找记录。文件中的 `projectDir` 和 `nodePath` 给出本机实际路径。

优先使用已连接的 `shopping_browser` MCP。其 stdio 入口是记录中的 `serverPath`；连接参数示例在同目录 `shopping-browser-mcp.json`。添加服务需使用当前客户端支持的配置方式，不要将示例直接覆盖现有配置。

CLI 备用入口，以 `projectDir` 为工作目录：

```powershell
node .\bridge.mjs start
node .\bridge.mjs tools
node .\bridge.mjs call browser_snapshot
node .\bridge.mjs call browser_navigate --input .\runtime\navigate.json
```

将工具参数写入 UTF-8 JSON 文件，避免在 shell 字符串中拼接输入。例如导航参数为 `{"url":"https://www.taobao.com/"}`。标签页索引必须来自新取得的 `browser_tabs`，点击参数为 `{"target":"<观察到的引用>","element":"<描述>"}`。调用前查看 `bridge.mjs tools` 中的当前参数定义。

服务绑定 `127.0.0.1:8931` 和 `127.0.0.1:8932`，使用用户目录下 `.codex/shopping-browser-profile` 的独立 Edge 资料。不要复制、读取凭证或上传该目录。多个实例可能共用本机服务，保持浏览器操作顺序执行，修改前重新核对标签页。

`compare INPUT.json` 仅把已观察的报价传给 Price Pilot，不使用 `--fetch`，不要导出 Cookie。原生 `shopping_compare` 还会检查分组与报价证据；存在时优先使用它。

缺少依赖时重新运行安装脚本。浏览器或会话服务在加购期间中断后，应重连并先检查购物车，再决定是否重试。完整 MCP 协议测试会启动或复用服务，不应在另一购物任务运行时执行；本包的隔离检查范围见根目录 `VALIDATION.md`。
