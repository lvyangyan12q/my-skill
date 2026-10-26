// Chrome DevTools MCP evaluate_script：format=function，sourcePath 指向本文件。
// 仅同源 GET；会话由浏览器管理，不读取 Cookie、存储、token 或认证头。
async function collectTbProject() {
  const origin = 'https://tb.cet-electric.com:4753';
  if (location.origin !== origin) throw new Error('请在目标 TB 站点的已登录页面运行。');
  const projectId = location.pathname.match(/\/project\/([a-f0-9]{24})(?:\/|$)/)?.[1];
  if (!projectId) throw new Error('请先打开目标项目的需求或工作项页面，再运行脚本。');

  async function get(path, params = {}) {
    const url = new URL(path, origin);
    url.search = new URLSearchParams(params).toString();
    const response = await fetch(url, {
      method: 'GET', credentials: 'same-origin', redirect: 'error',
      headers: {Accept: 'application/json'}
    });
    if (!response.ok) throw new Error(`接口返回 HTTP ${response.status}：${path}`);
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('json')) throw new Error(`接口未返回 JSON，请核实登录：${path}`);
    return response.json();
  }
  function rows(data) {
    const result = Array.isArray(data) ? data : data?.result;
    if (!Array.isArray(result)) throw new Error('接口响应不是预期的数组结构。');
    return result;
  }
  function pick(obj, keys) {
    return Object.fromEntries(keys.filter(key => key in obj).map(key => [key, obj[key]]));
  }
  const taskFilter = 'taskLayer IN (0,1,2,3,4,5,6,7,8)';
  const requests = [
    {name: 'project', path: `/api/projects/${projectId}`},
    {name: 'tasks', path: `/api/v2/projects/${projectId}/tasks`, params: {
      filter: taskFilter, pageSize: '5000', myVisible: 'true', checkInvisible: 'true'
    }},
    {name: 'types', path: `/api/v2/projects/${projectId}/scenariofieldconfigs`, params: {
      objectType: 'task', withTaskflowstatus: 'true', withCustomfields: 'true'
    }},
    {name: 'members', path: `/api/projects/${projectId}/projectfakerolemembers`}
  ];
  const output = {
    projectId, collectedAt: new Date().toISOString(),
    filters: {taskFilter, requestedPageSize: 5000},
    results: {}, errors: [],
    note: '未限制完成状态；层级范围 0 至 8。需核对实际总量、下一页、任务类型、字段单位及关联覆盖后再统计。'
  };
  for (const request of requests) {
    try {
      const data = await get(request.path, request.params);
      if (request.name === 'project') {
        output.results.project = pick(data, ['_id', 'name', 'isArchived']);
      } else if (request.name === 'members') {
        const members = rows(data);
        output.results.members = members.map(m => ({
          userId: m._userId || m.user?._id,
          name: m.name || m.user?.name,
          projectId: m._projectId
        }));
      } else if (request.name === 'types') {
        output.results.types = rows(data).map(t => pick(t, [
          '_id', 'name', 'objectType', 'type', '_taskflowId',
          'scenariofields', 'basicfields', 'customfields', 'taskflowstatuses'
        ]));
      } else {
        const tasks = rows(data);
        if (tasks.some(t => t._projectId !== projectId)) throw new Error('任务响应含其他项目数据，请核实筛选行为。');
        output.results.tasks = tasks.map(t => pick(t, [
          '_id', 'uniqueId', 'content', 'note', '_projectId', '_executorId', '_creatorId',
          'involveMembers', '_scenariofieldconfigId', 'scenariofieldconfig',
          '_taskflowstatusId', 'taskflowstatus', 'isDone', 'isArchived', 'priority',
          'created', 'updated', 'startDate', 'dueDate', 'accomplished',
          'effort', 'effortTimeUnit', 'workTime', 'customfields', 'taskLayer',
          '_taskId', 'ancestorIds', 'subtasks', 'subtaskCount', 'relations', 'relationsString',
          'commentsCount', 'attachmentsCount', 'objectlinksCount'
        ]));
        const total = data.totalSize ?? data.totalCount ?? null;
        output.coverage = {
          returnedCount: tasks.length, total,
          hasNextPage: Boolean(data.nextPageToken),
          completeForReturnedFilter: !data.nextPageToken && total !== null && tasks.length === total,
          continuation: data.nextPageToken ? '需要核实下一页请求；当前为部分数据。' : null
        };
      }
    } catch (error) {
      output.errors.push({endpoint: request.name, message: error.message});
    }
  }
  return output;
}
