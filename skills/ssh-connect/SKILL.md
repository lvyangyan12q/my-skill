---
name: ssh-connect
description: 使用 SSH 公钥认证连接服务器并执行只读检查；说明服务器与客户端配置，排查认证、权限和网络故障。禁止删除等危险操作。
---

# SSH 连接与只读检查

## 操作限制

- 本 skill 仅用于连接验证和只读诊断，例如查看状态、日志、配置与网络信息。配置要求用于指导用户准备环境，不代表允许自动修改。
- **禁止删除、清空、覆盖或破坏文件和数据**，包括删除日志、删库删表、格式化磁盘、删除容器/镜像/卷，以及执行具有同等效果的脚本、API 或间接命令。
- **禁止停止或重启服务、终止进程、重建部署、修改权限或防火墙、安装卸载软件等会改变运行状态的操作。** 发现需要变更时，只报告原因和建议，不执行修复；连接或排错授权不解除这些限制。
- 私钥只用于 SSH 认证，不读取、展示或复制其内容。输出日志时隐藏口令、令牌等敏感信息。

## 连接前确认

从当前任务或已有 SSH 配置取得主机、外部端口、账号、私钥路径或别名；缺少必要参数再询问。不固定服务器、不默认 root。确认两端操作系统及所需 VPN、跳板机是否可用。

## 服务器需要的配置

- OpenSSH Server（sshd）运行，目标账号允许登录，网络和防火墙允许连接端口。NAT 外部端口可映射到内部 22，两者不必相同。
- 允许公钥认证；客户端 `.pub` 公钥完整一行位于目标账号的有效授权文件中。首次部署由用户通过已有登录或管理控制台完成，保留原有公钥。
- Linux：通常使用 `~/.ssh/authorized_keys`，目录权限 700、文件权限 600，归属目标用户；家目录不能允许无关用户写入。检查 sshd 的 Include、Match 和账号限制。
- Windows：普通用户通常使用 `%USERPROFILE%\.ssh\authorized_keys`；管理员按有效 Match 配置使用 `%ProgramData%\ssh\administrators_authorized_keys`，后者仅授予 SYSTEM 和 Administrators 访问。

## 当前电脑需要的配置

- OpenSSH Client 可用，用 `ssh -V` 检查；客户端无需安装 SSH Server。
- 私钥保存在本机，公钥部署到服务器。没有密钥时，指导用户自行运行 `ssh-keygen -t ed25519`，避免覆盖已有密钥。
- Linux/macOS 私钥通常为 600；Windows 私钥应归当前账号所有，无关普通用户或组不能读取。加密私钥由用户通过 `ssh-add` 在本机解锁，不在聊天中提交口令。
- 首次连接由用户经可信渠道核对主机指纹并记录到 known_hosts。指纹变化时停止连接并核实，不删除旧记录或关闭主机校验。

## 验证连接

替换以下 PowerShell 示例参数；使用已经核对过主机指纹的目标：

```powershell
$sshHostName = 'server.example.com'
$sshPort = 22
$sshUser = 'remote-user'
$sshKeyPath = Join-Path $env:USERPROFILE '.ssh\id_ed25519'
ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=yes -o IdentitiesOnly=yes -p $sshPort -i $sshKeyPath "$sshUser@$sshHostName" hostname
```

另一次调用执行 `whoami`，避免依赖远端 shell 的命令分隔符。退出码为 0 且主机名和账号符合预期才算验证成功；一次调用不代表持续会话。后续仅执行用户任务所需的只读命令，报告时间范围、结果和未验证项。

## 故障定位

| 报错 | 只读检查 |
| --- | --- |
| 超时、拒绝连接、无路由 | 地址、端口、VPN、NAT、服务监听和防火墙状态 |
| `connect to host ... Permission denied` | 确认是否为本地沙箱限制；有证据时按工具授权流程原样申请沙箱外重试 |
| `bad permissions` | 本机私钥所有者和 ACL；Windows 使用 `Get-Acl -LiteralPath $sshKeyPath` 或 `icacls $sshKeyPath`，报告多余访问项，由用户处理 |
| `Permission denied (publickey)` | 用户名、所用密钥、服务端授权文件位置/权限及认证日志 |
| 主机指纹校验失败 | 核对可信指纹和 known_hosts；非默认端口条目通常为 `[HOST]:PORT` |
| 交互成功、BatchMode 失败 | 私钥是否已解锁、ssh-agent 对当前进程是否可用，以及额外认证要求 |

必要时使用 `ssh -v` 获取脱敏诊断信息。提权仅用于解除执行环境对已授权只读操作的限制，不扩大本 skill 的操作范围；被拒绝后停止该操作。
