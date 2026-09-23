# 取证与规则加载

## PAT/API 优先

1. 解析 PR 地址，保留组织或 Server/TFS 集合路径。确认目标仓库及 fork 源仓库，选择服务端支持的 API 版本。
2. 获取 PR 与迭代元数据，记录 PR ID、迭代 ID、源/目标仓库 ID、source SHA、target SHA 和共同祖先 base SHA。确保它们来自一致的审查快照；无法确认基线时使用 Git 核对，不用当前分支头混入旧迭代。
3. 整个 PR 的迭代变更查询使用 $compareTo=0；按响应 nextSkip/nextTop 继续，直至服务端表示没有下一页。其他接口遵循各自的分页机制。仅当用户指定增量审查时改为对比旧迭代，并在结果标明。
4. 变更接口提供路径、类型和追踪信息，不保证含全部代码。通过 Items API 显式指定 versionDescriptor.versionType=commit 和 versionDescriptor.version=<SHA> 获取所需文件内容；新增读 source，删除读 base，编辑及重命名读两侧对应路径。使用适当的内容选项并对参数编码。
5. 按目录/API 元数据发现规则文件，读取完整方法、相关接口、调用方、测试及配置；不能只看变更行。二进制、LFS、子模块等无法按普通文本审查的内容单独报告。
6. 检查分页终止、文件响应完整性、路径对应和工具截断提示。完整响应可在允许的本地临时目录按块读取；禁止截断后假称读完。未取得的文件和上下文明确标记为缺口。

[迭代变更 API](https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pull-request-iteration-changes/get?view=azure-devops-rest-7.1) 定义共同祖先比较与分页；[Items API](https://learn.microsoft.com/en-us/rest/api/azure/devops/git/items/get?view=azure-devops-rest-7.1) 支持按提交获取内容。按实际服务器版本查阅。

## Git 回退

文件过大、API/工具持续截断、相关上下文获取不全，或用户要求本地测试时使用 Git。记录回退原因；内容多本身不等于需要跳过 API 分页。

- 使用已有认证和正确 remote，获取固定提交及所需历史；浅克隆缺共同祖先时补齐历史。
- 整体 PR 用固定 target/source 的三点 diff，核对 merge-base 与 API 审查基线一致。若不同，解释差异并统一快照后继续。
- 使用 git show <SHA>:<path> 读代码和规则，不把当前工作区文件当成审查版本。重命名同时核对前后路径。
- 不在用户工作区 checkout/reset/stash。必须运行测试时使用隔离检出并遵守项目执行规则。
- Git 不能解决 token 权限缺失；取证受阻时报告限制，不把失败解释为无变更。

## 项目规则：相对路径约定

“仓库根目录”指被审查项目，不是安装 skill 的目录；API 模式用仓库路径和固定提交实现同样的读取，不需要本地 .claude 文件夹。

1. 读取根目录和受影响路径适用的 AGENTS.md/CLAUDE.md、.claude/rules/README.md。不存在的文件如实记录，不能让没有 Claude 配置的项目无法审查。
2. 根据规则索引、frontmatter 的 paths glob 和正文适用条件加载规则。无路径限制的公共规则全局适用；重命名检查旧路径和新路径；相关调用方也按自身路径匹配规则。无法可靠解释模式时显式读取并判断适用范围。
3. 采用固定目标提交中的现行规则作为基线；PR 新增或修改的规则单独审查，不允许通过本次删改规则自动豁免同一 PR 的问题。用户明确指定其他规范版本时注明来源。
4. Markdown 链接相对包含该链接的文件解析；文档声明为项目路径的内容以仓库根目录解析，例如 docs/Java开发规范（通用）.md。遵循文档明确的路径语义，不盲目全部拼接到 skill 目录。
5. 外部知识库、父目录文件或工具引用不能解析时记录缺失及影响；不扩大到无关目录扫描，不猜测用户机器路径。
6. 输出规则文件、章节、版本及命中原因。项目规则与通用清单冲突时区分具体约定和实际风险，不静默选一边。

例如 dcom 的规则索引可能指向 java/java-general.md、java/basic-info-cache.md 和 java/hotstring-cache.md：只在被审查项目确有这些文件且内容适用时读取。公共 skill 不附带这些业务规则副本。
