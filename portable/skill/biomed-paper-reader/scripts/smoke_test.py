"""Synthetic-only generator checks. No PDFs, research results or third-party modules."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def fixture(root, chapters=3, assets=7, absolute=False):
    root.mkdir(parents=True, exist_ok=True)
    (root/'assets').mkdir(exist_ok=True)
    (root/'audit').mkdir(exist_ok=True)
    (root/'audit'/'验收报告.md').write_text('# Synthetic test only\nNo scientific validation.\n', encoding='utf-8')
    src = root/'synthetic-source.txt'
    src.write_text('SYNTHETIC SOFTWARE TEST. No experiment, patient, paper or scientific claim.\n', encoding='utf-8')
    refs = [{'source_id':'s1','page':1,'locator':'Synthetic fixture, not a PDF'}]
    d = dict(schema_version=1, paper=dict(title='虚构软件测试 · 非科研结果', citation='Synthetic fixture', doi='not-applicable', scope='Software testing only', status='Not scientifically reviewed', intro='仅用于测试界面与路径。'), sources=[dict(id='s1',label='Synthetic source',path=str(src) if absolute else src.name,sha256=sha(src),pages=1,page_sizes=[[600,400]],status='Artificial page metadata, not PDF')], assets=[], methods=[dict(id='m1', title='软件夹具',text='没有实验、样本或统计推断。',sources=refs)], evidence=[],chapters=[],relations=[],limitations=['All content is artificial. This is not scientific evidence.'])
    for i in range(assets):
        p=root/'assets'/f'test-{i+1}.svg'
        p.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400"><rect width="600" height="400" fill="#eef3f8"/><rect x="40" y="80" width="520" height="240" fill="none" stroke="#245"/><text x="60" y="180" font-size="28">SYNTHETIC TEST {i+1}</text><text x="60" y="230" font-size="20">No scientific data</text></svg>',encoding='utf-8')
        d['assets'].append(dict(id=f'a{i}',label=f'Synthetic asset {i}',path=p.relative_to(root).as_posix(),sha256=sha(p),source_id='s1',source_sha256=sha(src),page=1,bbox=[0,0,600,400],dpi=72,width=600,height=400))
        d['evidence'].append(dict(id=f'e{i}',title=f'测试证据 {i+1}',figure='Synthetic',panels=str(i+1),asset=f'a{i}',metric='Software fixture',sample_unit='Not applicable',summary='仅测试引用关系；无生物物理含义。',details=['No sample size, repetitions or statistical test.'],limits=['Must not be used as a scientific result.'],methods=['m1'],sources=refs,captions=['Synthetic software asset, no original scientific caption.']))
    for i in range(chapters):
        ids=[f'e{k}' for k in range(assets) if k%chapters==i] or [f'e{i%assets}']
        d['chapters'].append(dict(id=f'c{i}',title=f'测试问题 {i+1}',question='Can the reader follow this synthetic reference?',evidence=ids,blocks=[dict(id=f'b{i}-{depth}',kind='AI推论',depth=depth,text=f'虚构测试段落，深度 {depth}；不是科学结论。',evidence=ids) for depth in [1,2,3]],background=[dict(level=level,title='测试背景',kind='AI推论',text='仅演示展开内容，无知识补充。',evidence=ids) for level in [1,2,3]]))
        if i: d['relations'].append({'from':f'c{i-1}','to':f'c{i}','type':'推进','label':'Synthetic navigation only'})
    path=root/'evidence.json'
    path.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
    return path

def run(root):
    script=Path(__file__).with_name('build_reader.py')
    cases=[]
    for chapters,assets in [(1,1),(3,7),(12,53)]:
        target=root/f'case-{chapters}-{assets}'
        evidence=fixture(target,chapters,assets)
        result=subprocess.run([sys.executable,str(script),str(evidence)],cwd=root,check=True,capture_output=True,encoding='utf-8')
        report=json.loads(result.stdout)
        if (report['chapters'],report['assets'],report['evidence']) != (chapters,assets,assets): raise RuntimeError('Dynamic counts failed')
        html=(target/'read.html').read_text(encoding='utf-8')
        md=(target/'reading.md').read_text(encoding='utf-8')
        for a in json.loads(evidence.read_text(encoding='utf-8'))['assets']:
            if a['path'] not in html or a['path'] not in md or not (target/a['path']).is_file(): raise RuntimeError('Image reference missing')
        if '<script src=' in html or 'fetch(' in html: raise RuntimeError('Unexpected external runtime dependency')
        cases.append({'chapters':chapters,'assets':assets,'evidence':assets,'status':'passed'})
    print(json.dumps({'status':'passed','cases':cases,'browser':'not_tested_by_this_script','science':'synthetic_only'}))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path); args=ap.parse_args()
    if args.output:
        if args.output.exists(): raise SystemExit('Output must be a new directory.')
        args.output.mkdir(parents=True); run(args.output.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='reader-synthetic-') as tmp: run(Path(tmp))
