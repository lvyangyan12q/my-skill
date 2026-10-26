# My Skills

可复用的 AI 编程助手技能集合。每个技能位于 `skills/<技能名称>/`，通过 `SKILL.md` 定义用途和操作指引。

## 技能列表

| 技能 | 用途 |
| --- | --- |
| [ssh-connect](skills/ssh-connect/SKILL.md) | 直接连接 SSH 执行只读任务，失败时提示具体缺失条件；禁止删除等危险操作。 |
| [herdr](skills/herdr/SKILL.md) | 在 Herdr 环境中管理终端窗格、标签页和工作区；仅在明确要求使用 Herdr 时启用。 |
| [azure-devops-pr-code-review](skills/azure-devops-pr-code-review/SKILL.md) | PAT/API 优先审查 PR，不完整时回退 Git；加载项目规则，检查缓存、锁、并发与循环调用。 |
| [karate-api-testing](skills/karate-api-testing/SKILL.md) | Karate 接口测试、JUnit/HTML 报告与按需只读数据库验证。 |
| [output-design](skills/output-design/SKILL.md) | 将复杂内容转为清晰中英文、图示或离线交互 HTML，保留事实、条件与来源。 |
| [tb-query](skills/tb-query/SKILL.md) | 复用浏览器登录态查询 Teambition 项目、需求与 bug，按功能和阶段统计工时及缺陷数。 |

## 目录结构

```text
my-skill/
├── README.md
└── skills/
    ├── ssh-connect/
    │   └── SKILL.md
    ├── herdr/
    │   └── SKILL.md
    ├── azure-devops-pr-code-review/
    │   ├── SKILL.md
    │   └── references/（环境、取证与专项检查）
    ├── output-design/
    │   ├── SKILL.md
    │   ├── LICENSE
    │   ├── references/
    │   ├── scripts/
    │   └── examples/
    ├── tb-query/
    │   ├── SKILL.md
    │   └── references/（接口出入参与统计口径）
    └── karate-api-testing/
        ├── SKILL.md
        └── references/environment.md
```

## 环境依赖

安装 skill 只提供操作指引，不会自动安装运行时、配置认证或启动服务。

| 技能 | 必需环境 | 可选依赖与配置 |
| --- | --- | --- |
| ssh-connect | OpenSSH Client、网络及可用 SSH 认证 | 服务端 sshd、公钥和主机指纹信任，详见技能说明 |
| herdr | Herdr CLI，且当前会话处于 Herdr 管理环境 | HERDR_ENV=1；普通终端不能替代 Herdr 会话 |
| azure-devops-pr-code-review | PAT 与 REST 客户端；Git 仅回退/本地测试时需要 | 按被审查项目根目录加载 .claude/rules；不强制 Python/uv，详见[环境配置](skills/azure-devops-pr-code-review/references/environment.md) |
| karate-api-testing | 匹配版本的 JDK、构建工具、Karate/JUnit、runner 和测试服务 | 数据库验证可用 PostgreSQL MCP；仅所选 MCP 要求时配置 uv/uvx、Python、Node 或 Docker，详见[环境配置](skills/karate-api-testing/references/environment.md) |
| output-design | 文字与图示按宿主能力使用；生成离线 HTML 需要 Python 3，仅用标准库 | 浏览器用于视觉与交互验证；生成器无需网络或前端依赖 |
| tb-query | 支持操作已有会话的浏览器工具、可访问 TB 的网络及目标浏览器登录态 | 工具明确支持同源会话请求时可按接口参考读取；否则使用页面查询，无需单独凭据文件 |

新加入的两个技能不依赖 dcom 的 .specify 脚本、固定服务器或内部知识库。使用前检查目标项目版本和实际命令；不要为了安装 skill 自动升级项目依赖。

## 使用 CC Switch 安装

在 CC Switch 的 Skills 页面打开「仓库管理」，添加以下仓库：

| 字段 | 值 |
| --- | --- |
| Owner | `lvyangyan12q` |
| Name | `my-skill` |
| Branch | `main` |
| Subdirectory | `skills` |

保存后刷新技能列表，搜索需要的技能并安装到目标应用。远程安装读取 GitHub 上的内容，本地改动需要提交并推送后才能被扫描到。

仓库地址：<https://github.com/lvyangyan12q/my-skill>

如果列表为空，先确认分支和子目录填写正确，再检查 CC Switch 是否能访问 GitHub。终端 Git 命令使用的临时代理设置不会自动应用到 CC Switch。

参考：[CC Switch 官方 Skills 使用说明](https://github.com/farion1231/cc-switch/blob/main/docs/user-manual/zh/3-extensions/3.3-skills.md)。

## 手动安装

将需要的单个技能文件夹复制到目标应用的技能目录，例如：

- Claude Code：`~/.claude/skills/ssh-connect/SKILL.md`
- Codex：`~/.codex/skills/ssh-connect/SKILL.md`

Windows 上 `~` 对应当前用户目录，例如 `C:\Users\你的用户名`。若应用使用自定义配置目录，以实际设置为准。保持技能文件夹完整，不要把整个仓库作为一个技能复制进去。

## 添加技能

在 `skills/` 下创建独立文件夹，并添加带有 YAML 元数据的 `SKILL.md`：

```markdown
---
name: example-skill
description: 说明这个技能的用途以及何时使用。
---

# Example Skill

写明完成任务需要的操作指引。
```

技能名称使用小写字母、数字和连字符。添加技能后同步更新上方列表。仓库中不存放私钥、口令或其他凭据。
