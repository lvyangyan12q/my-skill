# Teambition 接口入参与出参

## 执行条件

站点：`https://tb.cet-electric.com:4753`。下面是该部署已经观察到的业务接口结构，不视为所有 Teambition 部署的通用协议。

认证复用原浏览器会话，由浏览器自动处理；不要求单独凭据文件。独立终端 HTTP 客户端不会自动继承浏览器登录。浏览器工具若不提供可用的会话请求能力，使用页面查询，不编造调用能力。

接口路径中的 `{organizationId}`、`{projectId}`、`{smartgroupId}` 使用当前可见对象的稳定 ID。列表响应外壳按各接口说明处理，不统一假定都是数组或都是 `result`。

## 接口目录

| 方法 | 路径 | 入参 | 主要出参 |
|---|---|---|---|
| GET | `/api/users/me` | 无业务入参 | 用户对象：`_id`、`name`；其余身份与联系字段不导出 |
| GET | `/api/v2/users/me` | 无业务入参 | 当前身份的另一版本；实际响应结构需核对 |
| GET | `/api/v3/projects` | 查询：`_organizationId`、`orderBy`、`selectBy`、`pageSize` | `{result: 项目数组, nextPageToken}`；项目常用 `_id`、`name` |
| GET | `/api/projects/{projectId}` | 路径：项目 ID | 项目详情对象，含 `_id`、`name` |
| GET | `/api/projects/{projectId}/projectfakerolemembers` | 路径：项目 ID | 成员数组：`_id`、`_userId`、`name`、`user`、`_projectId` |
| GET | `/api/v2/projects/{projectId}/tasks` | 查询：`filter`、`pageSize`；可见性参数 `myVisible`、`checkInvisible` | `{result: 任务数组, nextPageToken, totalSize}` |
| GET | `/api/v2/projects/{projectId}/scenariofieldconfigs` | 查询：`objectType=task`、`withTaskflowstatus=true`、`withCustomfields=true` | 工作项配置数组：`_id`、`name`、`type`、`objectType`、`_taskflowId`、字段及状态配置 |
| GET | `/api/projects/scenariofieldconfigs` | 查询：`_projectIds[]`、`objectType=task`、`withCustomfields=true` | 批量项目配置数组 |
| GET | `/api/projects/{projectId}/taskflows` | 查询：`type`、`withTaskflowstatus`，取值按实际页面 | `{result: 工作流数组, nextPageToken, totalSize}`；元素含 `taskflowstatuses` |
| GET | `/api/projects/{projectId}/scenariofields/search` | 查询：`pageSize`、`scope`，scope 取值待实际页面核实 | `{result: 字段描述数组, totalCount, nextPageToken}` |
| GET | `/api/projects/{projectId}/appscenariofieldconfigs` | 路径：项目 ID | 应用字段配置数组，含工时偏好 |
| GET | `/api/organizations/{organizationId}/prioritygroups` | 路径：组织 ID | 优先级组数组，`options` 提供 `priority` 与名称对应 |
| POST | `/api/projects/{projectId}/searchers-bulk` | JSON：`{"taskType":"bug"}` 或 `{"taskType":"story"}` | `{searcher: {defaultValue, searcherList}}`；筛选器元数据，不是任务列表 |
| GET | `/api/projects/{projectId}/smartgroups` | 查询：`withGlobal`，按实际页面取值 | 视图配置数组 |
| GET | `/api/v2/projects/{projectId}/smartgroups` | 查询：`pageSize`、`type`、`withGlobal` | `{result: 视图数组, nextPageToken}`；观察到 `type=bug.custom` |
| GET | `/api/smartgroups/{smartgroupId}` | 路径：视图 ID | 视图对象：`name`、`type`、`filter`、`view` |
| GET | `/api/projects/{projectId}/task-groups` | 查询：`appName`、`includeEmptyTaskGroup`、`scope`、`tql`，按实际页面取值 | `{result: 分组数组, nextPageToken}`；元素含 `tql` |
| GET | `/api/commongroups` | 查询：`_projectId`、`_appId`、`all` | 分类数组，含父子结构信息 |
| GET | `/api/tags` | 查询：`_organizationId` 或 `_projectId`、`tagType` | 标签数组 |
| GET | `/api/projects/{projectId}/sprints` | 路径：项目 ID | 迭代数组，可能为空 |
| GET | `/api/tasklists` | 查询：`_projectId` | 任务清单数组 |
| GET | `/api/stages` | 查询：`_tasklistId` | 阶段数组 |

`searchers-bulk` 虽使用 POST，已观察为读取筛选器元数据。其调用仍须限定于当前查询需要，不能把其他 POST 默认视为只读。

## 任务列表调用约定

已确认的 bug 过滤表达式：

```text
((taskType = bug) AND taskLayer IN (0)) AND isDone = false ORDER BY isDone ASC, created ASC
```

需求将 `bug` 改成 `story`。以上条件仅覆盖未完成、第 0 层工作项，不覆盖所有阶段任务、所有状态或整个任务树。

另观察到按配置筛选及多个层级的表达式：

```text
_scenariofieldconfigId={实际配置ID} AND taskLayer IN (0,1,2,3,4,5,6,7,8)
```

它证明系统存在配置和层级筛选机制，但不能据此保证任何项目的全量表达式及其权限范围。完整功能统计优先通过页面确认全部状态和子任务。

参数类型与观察值：

| 参数 | 类型 / 观察值 | 注意事项 |
|---|---|---|
| filter | 字符串表达式 | 对原始表达式只做一次 URL 查询参数编码 |
| pageSize | 整数，观察到 100 与 5000 | 不代表系统上限 |
| myVisible | 布尔形式字符串 `true` | 保留页面正常可见性范围 |
| checkInvisible | 布尔形式字符串 `true` | 确切机制待核实，不用于扩大权限 |
| nextPageToken（出参） | 字符串 | 已观察到空字符串结束；下一页请求字段尚未确认 |

任务响应结构示意（无真实数据）：

```json
{
  "result": [
    {
      "_id": "任务ID",
      "content": "标题",
      "_projectId": "项目ID",
      "_executorId": "用户ID",
      "_scenariofieldconfigId": "类型配置ID",
      "isDone": false,
      "taskLayer": 0,
      "created": "ISO时间",
      "updated": "ISO时间",
      "startDate": null,
      "dueDate": null,
      "accomplished": null,
      "workTime": {"totalTime": 0, "usedTime": 0, "unit": "minute"},
      "customfields": []
    }
  ],
  "nextPageToken": "",
  "totalSize": 1
}
```

## 字段语义与映射

| 数据字段 | 业务含义 |
|---|---|
| `_id` / `uniqueId` | 稳定 ID / 可读编号；去重使用稳定 ID |
| `content` / `note` | 标题 / 说明；业务正文还可能在自定义富文本字段 |
| `_executorId` / `_creatorId` / `involveMembers` | 负责人 / 创建人 / 参与人 |
| `_scenariofieldconfigId` / `scenariofieldconfig.name` | 类型配置 ID / 名称 |
| `_taskflowstatusId` / `taskflowstatus.name` | 状态 ID / 名称 |
| `isDone` / `isArchived` | 已完成 / 已归档；两者分别处理 |
| `created` / `updated` | 创建 / 更新时间 |
| `startDate` / `dueDate` | 计划开始 / 截止时间 |
| `accomplished` | 完成时间；不能用更新时间替代 |
| `effort` / `effortTimeUnit` | 排期相关原始值；观察到单位标记 `work`，换算待核实 |
| `workTime.totalTime` / `usedTime` / `unit` | 工时结构；观察到单位 `minute`，计划与实际语义仍应与界面核实 |
| `customfields[]._customfieldId` | 关联字段定义 |
| `customfields[].value` / `values` | 实际结构可能是对象数组或空数组，按定义及值结构解析 |

人员列表的成员记录 `_id` 与用户 ID 不同，应使用 `_userId` 或 `user._id` 匹配任务人员字段。筛选元数据使用 `executorId`、`creatorId`，不能未经验证直接等同为 TQL 中同名字段。

已观察到筛选器支持人员 `executorId`、`creatorId`、`involveMembers`，日期 `created`、`updated`、`startDate`、`dueDate`、`accomplished`。日期操作有 `is`、`not`、`before`、`after`；具体编译后的表达式待实际筛选验证。

自定义字段按当前项目定义查找：解决者、开发人员、需求描述、基本要求、原因及解决方案、严重级别、建议解决日期、计划工时、实际工时，以及含子任务的计划 / 实际工时。字段存在不代表每条任务均填写；不固化历史项目字段 ID。

## 尚未验证的契约

- 独立任务详情、子任务、评论、关联项和附件的接口路径与参数。
- 真正的下一页请求、服务端按人员 / 日期过滤表达式及全部状态的调用。
- 当前浏览器工具是否支持直接读取已登录会话中的业务接口。
- 工时汇总字段、工作时间单位的换算规则及当前项目的具体配置。

这些缺口由可见页面查询或明确支持的工具能力补齐，不作为统计为 0 的依据。
