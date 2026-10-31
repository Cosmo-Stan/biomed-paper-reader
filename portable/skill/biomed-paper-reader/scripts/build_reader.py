"""Build local HTML and Markdown from one controlled evidence document. Stdlib only."""
import argparse, hashlib, json, sys
from pathlib import Path

if sys.version_info < (3, 9):
    raise SystemExit('Python 3.9 or newer is required.')
if not __debug__:
    raise SystemExit('Validation requires normal Python mode; do not use -O or PYTHONOPTIMIZE.')

def source_path(value, root):
    p = Path(value)
    return p if p.is_absolute() else root / p

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(d, root):
    assert d['schema_version']==1, 'Unsupported schema'
    assert d['chapters'] and d['evidence'], 'At least one chapter and evidence group are required'
    maps={}
    for key in ('sources','assets','methods','evidence','chapters'):
        maps[key]={x['id']:x for x in d[key]}
        assert len(maps[key])==len(d[key]), f'Duplicate {key} IDs'
    for s in d['sources']:
        if s.get('path'):
            p=source_path(s['path'], root)
            assert p.is_file(), f'Source missing: {s["id"]}'
            assert s.get('sha256') and digest(p)==s['sha256'], f'Source changed: {s["id"]}'
            if s.get('original_path'): assert digest(source_path(s['original_path'], root))==s['original_sha256'], f'Original snapshot changed: {s["id"]}'
    def refs(xs):
        assert xs, 'Missing source locator'
        for x in xs:
            s=maps['sources'][x['source_id']]
            assert x.get('locator'), 'Missing precise locator'
            if 'page' in x: assert 1<=x['page']<=s['pages'], 'Invalid PDF page'
    for a in d['assets']:
        p=(root/a['path']).resolve()
        assert p.is_relative_to(root.resolve()), 'Asset path escapes output'
        assert p.is_file() and digest(p)==a['sha256'], f'Asset missing/changed: {a["id"]}'
        assert a['source_id'] in maps['sources']
        assert a.get('source_sha256')==maps['sources'][a['source_id']]['sha256'], 'Asset/source identity mismatch'
        assert 1<=a['page']<=maps['sources'][a['source_id']]['pages']
        dims=maps['sources'][a['source_id']]['page_sizes']
        w,h=dims[a['page']-1]; x0,y0,x1,y1=a['bbox']
        assert 0<=x0<x1<=w+.01 and 0<=y0<y1<=h+.01, f'Crop out of bounds: {a["id"]}'
    for m in d['methods']: refs(m['sources'])
    for e in d['evidence']:
        assert e.get('captions') or e.get('caption_missing_reason'), f'Missing caption without explanation: {e["id"]}'
        assert e['asset'] in maps['assets']
        if e.get('focus_asset'): assert e['focus_asset'] in maps['assets']
        assert e['metric'] and e['sample_unit']
        assert all(m in maps['methods'] for m in e['methods'])
        refs(e['sources'])
    bids=set()
    for c in d['chapters']:
        assert any(b['depth']==1 for b in c['blocks']), f'Chapter needs a depth-1 overview: {c["id"]}'
        assert c['evidence'] and all(e in maps['evidence'] for e in c['evidence'])
        for b in c['blocks']+c['background']:
            assert b['kind'] in ['原文转述','结果','作者解释','AI推论','外部知识']
            assert b['evidence'] and all(e in maps['evidence'] for e in b['evidence'])
            if b['kind']=='外部知识': refs(b.get('sources',[]))
        for b in c['blocks']:
            assert b['id'] not in bids
            bids.add(b['id'])
            assert b['depth'] in (1,2,3)
        for b in c['background']: assert b['level'] in (1,2,3)
    for r in d['relations']: assert r['from'] in maps['chapters'] and r['to'] in maps['chapters']
    return maps

def markdown(d, maps):
    p=d['paper']; out=[f'# {p["title"]}',p['citation'],f'DOI: {p["doi"]}',p['scope'],f'验证状态：{p["status"]}',p['intro']]
    def links(ids): return ' · '.join(f'[{maps["evidence"][i]["title"]}](#{i})' for i in ids)
    def loc(xs): return '；'.join(f'{maps["sources"][s["source_id"]]["label"]} / PDF p.{s.get("page","—")} / {s["locator"]}' for s in xs)
    for c in d['chapters']:
        out += [f'<a id="{c["id"]}"></a>',f'## {c["title"]}',c['question']]
        for b in c['blocks']: out += [f'**{b["kind"]} · {b["id"]} · 阅读深度 {b["depth"]}**\n\n{b["text"]}\n\n证据：{links(b["evidence"])}']
        for b in c['background']: out += [f'### 背景 {b["level"]}：{b["title"]}',f'**{b["kind"]}**\n\n{b["text"]}\n\n{links(b["evidence"])}']
    out += ['## 证据账本']
    for e in d['evidence']:
        a=maps['assets'][e.get('focus_asset',e['asset'])]; whole=maps['assets'][e['asset']]
        out += [f'<a id="{e["id"]}"></a>',f'### {e["title"]}',f'**读出：{e["metric"]}；样本单位：{e["sample_unit"]}。**',e['summary'],f'![{e["title"]}]({a["path"]})',f'[原始整图]({whole["path"]})',f'来源：{loc(e["sources"])}']
        out += ['- '+v for v in e['details']]
        out += ['**解释边界**\n\n'+'\n\n'.join(e['limits'])]
        for m in e['methods']:
            v=maps['methods'][m]; out += [f'**方法：{v["title"]}**\n\n{v["text"]}\n\n{loc(v["sources"])}']
        if e.get('captions'): out += ['<details><summary>源图注（复用已审读转录）</summary>\n\n'+'\n\n'.join(e['captions'])+'\n\n</details>']
        else: out += ['图注缺失：'+e['caption_missing_reason']]
    out += ['## 证据关系（阅读推进不等于因果证明）']+[f'- {r["from"]} → {r["to"]}：{r["type"]} / {r["label"]}' for r in d['relations']]
    out += ['## 完整性与限制']+['- '+v for v in d['limitations']]
    out += ['## 来源清单']
    for s in d['sources']:
        out += [f'- **{s["id"]} / {s["label"]}**：{s["status"]}；{s.get("pages","—")}页。\n  路径/链接：{s.get("path",s.get("url",""))}\n  SHA-256：{s.get("sha256","不适用")}']
        if s.get('original_path'): out += [f'原始输入快照：{s["original_path"]}\n\n原始SHA-256：{s["original_sha256"]}\n\n{s["normalization_note"]}']
    if d.get('raw_data'): out += ['## 原始数据入口（未复算）']+[f'- [{r["name"]}]({r["url"]})：{r["status"]}' for r in d['raw_data']]
    return '\n\n'.join(out)+'\n'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('evidence',type=Path); args=ap.parse_args()
    src=args.evidence.resolve(); root=src.parent
    d=json.loads(src.read_text(encoding='utf-8')); maps=validate(d,root)
    assets=Path(__file__).resolve().parents[1]/'assets'
    raw=json.dumps(d,ensure_ascii=False).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    html=(assets/'reader.html').read_text(encoding='utf-8').replace('/*READER_CSS*/',(assets/'reader.css').read_text(encoding='utf-8')).replace('/*READER_JS*/',(assets/'reader.js').read_text(encoding='utf-8')).replace('READER_DATA_JSON',raw)
    (root/'read.html').write_text(html,encoding='utf-8'); (root/'reading.md').write_text(markdown(d,maps),encoding='utf-8')
    (root/'audit').mkdir(exist_ok=True)
    report=dict(status='structural_checks_passed_not_scientific_validation',evidence_sha256=digest(src),chapters=len(d['chapters']),claims=sum(len(c['blocks']) for c in d['chapters']),evidence=len(d['evidence']),assets=len(d['assets']),outputs={p:digest(root/p) for p in ['read.html','reading.md']})
    (root/'audit/build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__': main()
