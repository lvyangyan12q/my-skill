# My Skills

可复用的 AI 编程助手技能集合。每个技能位于 `skills/<技能名称>/`，通过 `SKILL.md` 定义用途和操作指引。

## 技能列表

| 技能 | 用途 |
| --- | --- |
| [ssh-connect](skills/ssh-connect/SKILL.md) | 配置 SSH 公钥认证，明确服务器端和客户端配置，验证连接并排查权限、网络及认证故障。 |
| [herdr](skills/herdr/SKILL.md) | 在 Herdr 环境中管理终端窗格、标签页和工作区；仅在明确要求使用 Herdr 时启用。 |

## 目录结构

```text
my-skill/
├── README.md
└── skills/
    ├── ssh-connect/
    │   └── SKILL.md
    └── herdr/
        └── SKILL.md
```

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
