# 环境与访问配置

## 依赖

| 项目 | 要求 |
| --- | --- |
| Git | 内容不完整需回退，或本地测试时才需要；获取固定提交 |
| REST 客户端 | 默认取证方式；可用 PowerShell Invoke-RestMethod、已授权 MCP 或项目已有客户端 |
| PAT | 默认从 AZDO_PAT 或安全本机配置读取；取证需要代码读取权限，发布评论另需相应写权限 |
| 网络 | 地址、企业 CA、VPN 和代理按环境配置，保留 TLS 验证 |
| Python / uv | 本 skill 不需要；仅当选定的外部客户端依赖它们时按其文档配置 |

API 模式不要求 Git；回退时运行 git --version 并确认仓库 remote。PowerShell 可用 Get-Command Invoke-RestMethod 检查客户端。环境不满足时说明缺失项，不自动安装或改系统配置。

Azure DevOps Services 基础地址通常为 https://dev.azure.com/<organization>；Server/TFS 可能包含集合路径。REST api-version 必须匹配服务端，不把最新版写死到旧服务器。Git 仓库权限不代表独立 REST 客户端已认证。

## 读取 PR 的 PowerShell 示例

替换示例参数；令牌由用户预先放入当前进程可读的 AZDO_PAT，不在命令、聊天或仓库中填写令牌。已有安全认证客户端时优先复用。

~~~powershell
$azdoBase = 'https://dev.azure.com/example-org'
$azdoProject = [uri]::EscapeDataString('example-project')
$azdoRepo = [uri]::EscapeDataString('repository-id')
$azdoPr = 123
$azdoApiVersion = '7.1' # 示例：先确认服务端支持
if (-not $env:AZDO_PAT) { throw '请先在本机配置 AZDO_PAT' }
$azdoAuth = [Convert]::ToBase64String(
    [Text.Encoding]::UTF8.GetBytes(':' + $env:AZDO_PAT)
)
$azdoHeaders = @{ Authorization = 'Basic ' + $azdoAuth }
$azdoUri = "$azdoBase/$azdoProject/_apis/git/repositories/$azdoRepo/pullRequests/$($azdoPr)?api-version=$azdoApiVersion"
$azdoPrInfo = Invoke-RestMethod -Method Get -Uri $azdoUri -Headers $azdoHeaders
$azdoPrInfo | Select-Object pullRequestId,title,status,sourceRefName,targetRefName
~~~

不输出请求头或启用记录认证头的调试日志。401/403 检查认证及权限；404 检查集合、项目、仓库、PR 和可见性；网络失败检查代理与企业 CA，不关闭证书校验。

完整分页、固定版本取证和 Git 回退见 [取证流程](review-inputs.md)。

## 官方接口

- [读取 PR](https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pull-requests/get-pull-request?view=azure-devops-rest-7.1)
- [评论线程](https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pull-request-threads?view=azure-devops-rest-7.1)

按目标服务器版本切换文档。发布评论前检查迭代与 diff 行号，发送结构化请求体，不通过 shell 拼接含评论文本的 JSON。
