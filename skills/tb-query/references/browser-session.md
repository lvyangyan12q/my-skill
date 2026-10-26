# 浏览器会话内的 API 读取

## Chrome DevTools MCP

默认 JS 执行工具为 Chrome DevTools MCP 的 `evaluate_script`。先 `list_pages`，选择目标 TB 项目所在的已登录 Chrome 页面，后续每次显式传入返回的 `pageId`，不缓存跨会话页面 ID。

连接采用 `--autoConnect`，复用运行中的 Chrome 默认配置。首次使用需要用户在 `chrome://inspect/#remote-debugging` 开启远程调试，并在 Chrome 的连接提示中允许连接。若报 `Could not find DevToolsActivePort`，说明当前 Chrome 调试连接尚未就绪。Edge 中已有的登录态不会自动共享给 Chrome；目标 Chrome 未登录时，由用户本人登录。

1. 用 `evaluate_script` 执行 `() => ({origin: location.origin, path: location.pathname, title: document.title})`，确认目标站点与项目。必要时读取页面可见正文确认登录。
2. 使用 `evaluate_script`，传 `pageId`、`format: "function"`、`sourcePath` 为本技能 `scripts/browser-collect.js` 的绝对路径、`waitForStableDom: false`。脚本是异步函数声明，工具等待并直接返回可序列化 JSON。
3. 如工具版本没有 `sourcePath`，读取脚本原文，作为 `function` 参数传入，保持相同函数语义。不要将函数声明当成已经执行的普通 script。
4. 按结果中的 `errors` 与 `coverage` 判断成功和完整度；大量结果可按该工具支持的 `filePath` 写到本次工作目录，再从文件分析。文件只包含业务数据。

凭据始终由浏览器维护。请求使用 `credentials: same-origin`，不读取或保存 Cookie、token、浏览器存储、认证头或会话文件。只读业务请求使用同源 GET。普通 Node/Python HTTP 客户端不自动继承浏览器登录态。

## 采集范围

脚本从 `/project/{projectId}/...` 解析项目 ID，依次获取项目详情、层级 0 至 8 的任务、工作项类型配置和项目成员。任务查询不限制完成状态，pageSize=5000，filter 仅编码一次。返回经过字段选择的业务数据、查询时刻、过滤条件、数量、是否存在下一页和错误；不创建浏览器下载。

先核实 `coverage.completeForReturnedFilter`，再核实任务类型、工时单位、子任务和关联覆盖。若存在下一页，先观察产品真实翻页请求以补全分页契约；不能把当前页当作全集。其他接口参考 [api.md](api.md)。

接口参数或字段语义尚未确认时，通过 DevTools 网络工具观察目标页面产生的请求，只提取所需路径、非认证入参和业务出参，避免输出认证材料。其他浏览器工具若仅提供只读 DOM evaluate，则只用于页面检查。

## 验证状态

MCP 已安装并注册，当前会话已加载 `list_pages` 和 `evaluate_script`。首次连接检查返回缺少 `DevToolsActivePort`；需先由用户开启 Chrome 远程调试并允许连接。尚未完成 TB 接口实跑，不据此认定接口不可用、查询完成或登录失效。
