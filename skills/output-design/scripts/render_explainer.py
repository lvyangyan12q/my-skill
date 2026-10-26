"""Render supplied scenario steps as an offline HTML explainer; no business inference."""
import argparse
import html
import json
import re
from pathlib import Path


def validate(data):
    if not isinstance(data, dict):
        raise ValueError('input must be an object')
    for key in ('title', 'question'):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f'{key} must be nonempty text')
    scenarios = data.get('scenarios')
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError('scenarios must be a nonempty list')
    for scenario in scenarios:
        if not isinstance(scenario, dict) or not isinstance(scenario.get('name'), str) or not scenario['name'].strip():
            raise ValueError('each scenario needs a name')
        if not isinstance(scenario.get('steps'), list) or not scenario['steps']:
            raise ValueError('each scenario needs steps')
        for step in scenario['steps']:
            if not isinstance(step, dict):
                raise ValueError('step must be an object')
            for key in ('title', 'explanation'):
                if not isinstance(step.get(key), str) or not step[key].strip():
                    raise ValueError(f'step {key} must be nonempty text')
    if not isinstance(data.get('sources', []), list) or any(not isinstance(s, str) for s in data.get('sources', [])):
        raise ValueError('sources must be a list of text references')


def render(data):
    validate(data)
    # Literal text only. Neither source text nor JSON may become executable HTML.
    payload = json.dumps(data, ensure_ascii=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    esc = html.escape
    all_steps = ''.join('<section><h3>' + esc(s['name']) + '</h3><ol>' + ''.join(
        '<li><strong>' + esc(step['title']) + '</strong><p>' + esc(step['explanation']) + '</p></li>'
        for step in s['steps']) + '</ol></section>' for s in data['scenarios'])
    sources = ''.join('<li>' + esc(s) + '</li>' for s in data.get('sources', []))
    fields = {'TITLE': esc(data['title']), 'QUESTION': esc(data['question']),
              'ALL_STEPS': all_steps, 'SOURCES': sources, 'DATA': payload}
    return re.sub(r'__(TITLE|QUESTION|ALL_STEPS|SOURCES|DATA)__', lambda m: fields[m[1]], PAGE)


PAGE = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title><style>
:root{font-family:system-ui,sans-serif;color:#183047;background:#f4f7fb;line-height:1.65}
body{max-width:960px;margin:auto;padding:24px}h1{line-height:1.25}h2,h3{line-height:1.4}
header,p{overflow-wrap:anywhere}main,details,footer{background:white;border:1px solid #d5deea;border-radius:12px;padding:22px;margin:20px 0}
.controls{display:flex;gap:12px;align-items:center;flex-wrap:wrap}select,button{font:inherit;padding:8px 14px;border:1px solid #8094aa;border-radius:7px;background:white;color:inherit}
select{max-width:100%}button{cursor:pointer}button:disabled{opacity:.45;cursor:default}button:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid #b24c00;outline-offset:3px}
#path{display:flex;gap:10px;padding:0;list-style:none;flex-wrap:wrap}#path button[aria-current="step"]{background:#164e78;color:white;border-color:#164e78}#path li:not(:last-child)::after{content:' →';color:#557080}
#explanation{white-space:pre-wrap;min-height:6em}#position{font-weight:bold;color:#365a7b}summary{cursor:pointer;font-weight:600}li p{white-space:pre-wrap}footer{font-size:.9rem}noscript{color:#8a2800}
@media(max-width:540px){body{padding:12px}main,details,footer{padding:16px}.controls button{flex:1}}
@media print{body{background:white;max-width:none}.interactive,summary{display:none}details{display:block}details>section{display:block!important}main,details,footer{border:0;padding:0}li{break-inside:avoid}}
</style></head><body><header><h1>__TITLE__</h1><p>__QUESTION__</p></header>
<main class="interactive"><div class="controls"><label for="scenario">选择场景</label><select id="scenario"></select><button id="reset" type="button">重新开始</button></div>
<ol id="path" aria-label="解释步骤"></ol><section aria-live="polite" aria-atomic="true"><p id="position"></p><h2 id="step-title"></h2><p id="explanation"></p></section>
<div class="controls"><button id="previous" type="button">上一步</button><button id="next" type="button">下一步</button></div></main>
<noscript>交互需要 JavaScript。全部场景内容仍可在下方阅读。</noscript>
<details id="full-content" open><summary>全部场景与完整说明</summary>__ALL_STEPS__</details>
<footer><strong>来源 / 适用说明</strong><ul>__SOURCES__</ul><p>本页只展示输入内容，不执行真实业务操作。</p></footer>
<script type="application/json" id="explanation-data">__DATA__</script><script>
const data=JSON.parse(document.getElementById('explanation-data').textContent);
const select=document.getElementById('scenario'),path=document.getElementById('path');let step=0;
data.scenarios.forEach((scenario,i)=>{const option=document.createElement('option');option.value=String(i);option.textContent=scenario.name;select.append(option)});
function update(){const steps=data.scenarios[Number(select.value)].steps;path.replaceChildren();
steps.forEach((item,i)=>{const li=document.createElement('li'),button=document.createElement('button');button.type='button';button.textContent=`${i+1}. ${item.title}`;if(i===step)button.setAttribute('aria-current','step');button.onclick=()=>{step=i;update()};li.append(button);path.append(li)});
document.getElementById('position').textContent=`第 ${step+1} / ${steps.length} 步`;
document.getElementById('step-title').textContent=steps[step].title;document.getElementById('explanation').textContent=steps[step].explanation;
document.getElementById('previous').disabled=step===0;document.getElementById('next').disabled=step===steps.length-1;}
select.onchange=()=>{step=0;update()};document.getElementById('reset').onclick=()=>{step=0;update()};
document.getElementById('previous').onclick=()=>{if(step>0){step--;update()}};
document.getElementById('next').onclick=()=>{if(step<data.scenarios[Number(select.value)].steps.length-1){step++;update()}};
const detail=document.getElementById('full-content');detail.open=false;let previousOpen=false;
window.addEventListener('beforeprint',()=>{previousOpen=detail.open;detail.open=true});window.addEventListener('afterprint',()=>{detail.open=previousOpen});update();
</script></body></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = render(json.loads(args.input.read_text(encoding='utf-8-sig')))
    # Explicit new file only: never silently replace a user's hand-edited page.
    with args.output.open('x', encoding='utf-8') as target:
        target.write(result)
    print(args.output.resolve())


if __name__ == '__main__':
    main()
