# 运行环境与依赖

| 组件 | 何时需要 | 检查与配置 |
| --- | --- | --- |
| JDK | 必需 | java -version；兼容项目及固定 Karate 版本 |
| Maven / Maven Wrapper | Maven 项目必需 | mvn -version 或 ./mvnw -version；Windows 用 mvnw.cmd；确认 JAVA_HOME |
| Karate、JUnit、测试插件 | 必需 | 检查 pom.xml、父 POM、runner 和 Surefire；沿用兼容版本 |
| 被测服务、URL、认证 | 必需 | 提供获授权的测试环境，先执行只读健康检查 |
| PostgreSQL MCP | 使用该方式验证数据库时 | 发现当前工具，确认连接目标和 SELECT 角色 |
| Python、uv/uvx、Node、Docker | 仅当 MCP/辅助工具要求 | 按对应工具文档检查版本；不是 Karate 本身的依赖 |
| Speckit、springboot-service skill | 不需要 | 已集成项目可沿用，不作为公共 skill 前提 |

不要因为缺少 uv 就中断纯 HTTP 测试，也不要在未选定 MCP 服务时自动安装 uv。若 MCP 启动命令是 uvx，检查 uvx --version 和子进程 PATH；若是 uv run，检查 uv --version、工作目录及服务自己的依赖清单。桌面应用 PATH 可能与交互终端不同。下载运行时或工具包需要网络、代理及当前执行权限。

## 首次初始化

只有用户要求初始化时执行：

1. 检查固定的 Java、Karate、JUnit 和构建插件版本；依据相同版本的官方文档选择依赖坐标和 Java 包名，不混用不同大版本示例。
2. 使用项目已有 Maven 配置和私有仓库设置；凭据保留在本机 settings.xml 或 CI 凭据系统。
3. 添加最小 runner、karate-config.js 和一个获授权的只读 smoke 场景，沿用资源目录或配置测试资源映射。
4. 启用所需 JUnit XML 和 HTML 报告，确保失败数影响测试退出状态；自定义 Runner 必须断言其结果。
5. 执行 smoke，核对场景、退出码和本次报告，记录可复现命令。

Gradle 项目沿用原有入口，不为本 skill 强行引入 Maven。没有匹配版本的示例时先查文档，不凭记忆升级。

## 常见问题

- Java class 版本错误：检查构建工具实际使用的 JDK，不仅是终端 java。
- 找不到测试或执行数为 0：检查 runner 命名、Surefire 规则、标签和资源目录。
- 无 JUnit XML：检查对应版本的报告选项及目录。
- 401/403：检查身份、令牌有效期及授权范围，不修改断言掩盖错误。
- MCP 无法启动：检查实际命令、运行时、PATH、网络和只读连接配置，不打印含密码的连接串。
- 依赖下载失败：检查 Maven 仓库、代理和凭据，不能以跳过测试声称通过。

## 官方文档

- [安装与依赖](https://docs.karatelabs.io/getting-started/install-dependencies/)
- [JUnit 集成](https://docs.karatelabs.io/running-tests/junit/)
- [测试报告](https://docs.karatelabs.io/running-tests/test-reports/)

入口可能展示新版本；使用前与项目固定版本对照。
