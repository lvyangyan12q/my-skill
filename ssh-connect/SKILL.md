---
name: ssh-connect
description: 配置并使用 OpenSSH 公钥认证连接远程服务器；用于区分服务器与当前电脑的配置、验证 SSH 登录，以及排查密钥权限、主机指纹、网络或沙箱连接故障。
---

# SSH 公钥连接

使用当前电脑的 OpenSSH 客户端连接用户指定的服务器。公钥部署到服务器，私钥留在当前电脑；只保存私钥路径，不读取、输出或复制私钥内容。具体服务器参数从当前任务取得，不设固定服务器默认值。

## 确定连接参数

从用户消息或已有 SSH 配置确定主机、外部端口、登录用户、私钥绝对路径或 SSH 别名，以及两端操作系统。缺少必要信息时再询问；不要默认 root。确认私网地址所需的 VPN、跳板机或网络已经可用。已有会话授权继续适用，连接授权本身不包含任意远端修改。

## 服务器端需要配置什么

- 安装并运行 OpenSSH Server（sshd），目标账号存在且允许 SSH 登录。
- 放行实际连接路径的 TCP 端口，包括主机防火墙、安全组与 NAT 转发。外部端口可以映射到服务器内部的 22，无需因此把 sshd 的监听端口也改成外部端口。
- 在目标账号的有效授权文件中追加客户端公钥完整一行，保留已有公钥。首次部署需要现有密码登录、管理控制台或管理员协助；未建立登录能力时不要假设可以通过 SSH 安装公钥。
- 确认有效 sshd 配置允许公钥认证，并检查 Include、Match、AllowUsers、AllowGroups 和 AuthenticationMethods 对该用户的约束。以当前有效配置为准，不覆盖整份配置。

### Linux 服务器

常见配置在 `/etc/ssh/sshd_config`，公钥文件在目标用户的 `~/.ssh/authorized_keys`。相关配置项为 `PubkeyAuthentication yes` 和 `AuthorizedKeysFile .ssh/authorized_keys`；已有等价配置无需修改。

以下命令在目标用户身份下执行；先追加公钥，再确认目录和文件归属该用户：

```sh
mkdir -p ~/.ssh
chmod 700 ~/.ssh
# 将客户端 .pub 文件的完整一行追加到 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

用户家目录及授权文件不能允许无关用户写入。有 ssh-copy-id 且已有登录渠道时，可在客户端执行 `ssh-copy-id -p PORT -i PUBLIC_KEY_PATH USER@HOST`，替换参数后运行。

只有修改 sshd 配置时才需要校验并重载：先运行 `sudo sshd -t`，通过后使用该系统实际的 ssh/sshd 服务重载命令。保留现有管理会话，在新会话中验证成功后再结束旧会话。仅追加 authorized_keys 通常不需要重载。不要为解决密钥问题顺带禁用密码登录。

### Windows 服务器

确认 OpenSSH Server 的 sshd 服务和入站防火墙规则。配置通常位于 `%ProgramData%\ssh\sshd_config`。普通用户一般使用 `%USERPROFILE%\.ssh\authorized_keys`；默认配置下 Administrators 组用户使用 `%ProgramData%\ssh\administrators_authorized_keys`，应检查实际 Match 配置。后者的 ACL 按 Windows OpenSSH 要求仅授予 SYSTEM 和 Administrators 访问；使用实际 SID 或本机组名，避免依赖英文系统名称。

## 当前连接电脑需要配置什么

1. 安装 OpenSSH Client，用 `ssh -V` 确认可执行程序；仅发起连接无需安装 SSH Server。
2. 使用已有私钥；没有时运行 `ssh-keygen -t ed25519`，选择未占用路径并由用户交互设置私钥口令。受环境算法政策限制时选择双方支持的算法。公钥 `.pub` 交给服务器，私钥由当前运行 SSH 的账号保管。
3. Linux/macOS 通常使用 `chmod 700 ~/.ssh`、`chmod 600 PRIVATE_KEY_PATH`；Windows 检查所有者及 ACL，见下文。只调整需要修复的文件。
4. 加密私钥可由用户在自己的终端通过 `ssh-add PRIVATE_KEY_PATH` 解锁到可用的 ssh-agent；不要求用户把口令发到聊天里。自动化使用 BatchMode，不等待密码输入；代理必须对实际执行 SSH 的进程可用。
5. 配置主机身份信任。首次连接通过可信管理渠道核对服务器主机公钥指纹，再写入当前账号的 known_hosts。ssh-keyscan 的结果自身不能证明服务器身份。主机密钥变化时先查明原因，不直接删除旧记录或关闭校验。

可选：在当前电脑的 `~/.ssh/config` 添加以下示例，并替换所有示例值：

```sshconfig
Host example-server
    HostName server.example.com
    User remote-user
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

Windows 默认位置为 `$env:USERPROFILE\.ssh\config`，不是 config.txt；使用带空格的密钥路径时加引号。配置中不存放口令。保存前保留已有 Host 条目。

## 连接与完成标准

在主机指纹已核对并记录后，按当前 shell 正确引用参数。以下为 PowerShell 模板，运行前替换示例值：

```powershell
$sshHostName = 'server.example.com'
$sshPort = 22
$sshUser = 'remote-user'
$sshKeyPath = Join-Path $env:USERPROFILE '.ssh\id_ed25519'
ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=yes -o IdentitiesOnly=yes -p $sshPort -i $sshKeyPath "$sshUser@$sshHostName" 'hostname'
```

用第二个同样的 SSH 调用执行 `whoami`，避免假设远端命令分隔符适用于所有系统。已有别名可使用 `ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=yes example-server hostname`。需要后续任务时按用户授权执行远端命令，注意本地与远端 shell 的独立引用规则。

以退出码为 0 且返回预期主机名和用户为登录成功标准。报告验证结果与实际修改；一次 SSH 命令成功不表示存在持续的交互会话。仅有 TCP 可达不能宣称认证成功。

## 按报错排查

| 信号 | 下一步 |
|---|---|
| 超时、拒绝连接、无路由 | 核对地址、外部端口、VPN、NAT、监听服务与防火墙 |
| `connect to host ... Permission denied` | 区分本地沙箱网络限制与远端认证错误；有沙箱证据时按工具权限流程原样申请沙箱外重试 |
| `UNPROTECTED PRIVATE KEY FILE` / `bad permissions` | 检查本地私钥所有者和 ACL，服务器公钥配置不是此报错的首要修复项 |
| `Permission denied (publickey)` | 检查目标用户、实际提供的公钥、授权文件位置/权限及服务端日志；不要把认证拒绝当作网络沙箱问题 |
| `Host key verification failed` 或主机密钥改变 | 通过可信渠道核对指纹及 known_hosts 条目；非默认端口记录通常为 `[HOST]:PORT` |
| BatchMode 失败但交互登录成功 | 检查加密私钥是否已解锁、代理可见性与服务器是否要求额外认证 |

必要时使用 `ssh -v`，只分享与故障有关且已脱敏的日志。

### Windows 私钥 ACL

先只读检查：

```powershell
Get-Acl -LiteralPath $sshKeyPath | Format-List Owner,AccessToString
icacls $sshKeyPath
```

如果报错指明某个普通用户或组可读取私钥（例如 CodexSandboxUsers），确认其真实 SID 和访问项，再针对该文件修复。在具备权限的用户上下文中保留文件所有者的访问及适用的 SYSTEM/Administrators 权限；不要递归重置整个 .ssh 目录。

下面模板先把继承权限转成显式权限，再移除已确认的多余授权；替换 SID 后执行，每一步失败即停：

```powershell
$unwantedSid = 'REPLACE_WITH_VERIFIED_SID'
icacls $sshKeyPath /inheritance:d
if ($LASTEXITCODE -ne 0) { throw '修改继承权限失败' }
icacls $sshKeyPath /remove:g "*$unwantedSid"
if ($LASTEXITCODE -ne 0) { throw '移除权限失败' }
icacls $sshKeyPath
```

重新检查剩余访问项并验证 SSH。权限修改或私钥访问受沙箱限制时使用正式提权流程；不要给沙箱用户重新添加私钥读取权限来绕过限制。拒绝授权后保持文件不变，并提供手动操作步骤。

## 参考

- [OpenSSH sshd_config](https://man.openbsd.org/sshd_config)：服务器配置及匹配规则。
- [Windows OpenSSH 密钥管理](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement)：Windows 授权文件与权限要求。
