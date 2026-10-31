"""Synthetic language and provenance regression checks; stdlib only."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
sys.dont_write_bytecode=True
from smoke_test import fixture

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def english_fixture(root):
    path=fixture(root,3,7)
    d=json.loads(path.read_text(encoding='utf-8'))
    d['presentation']={'language':'en'}
    d['paper']['title']='Synthetic language test - not scientific evidence'
    d['paper']['intro']='A software fixture with no research data.'
    d['methods'][0].update(title='Synthetic method',text='No experiment or statistical inference.')
    d['sources'][0].update(original_path='synthetic-source.txt',original_sha256=d['sources'][0]['sha256'],normalization_note='Synthetic identity provenance only.')
    d['raw_data']=[{'name':'Synthetic data link','url':'https://example.invalid/synthetic-only','status':'Not downloaded; no real data'}]
    for i,e in enumerate(d['evidence']):
        e.update(title=f'Test evidence {i+1}',summary='Synthetic navigation only.',captions=['Original source quotation: 保留原文'],metric='Synthetic readout')
    for i,c in enumerate(d['chapters']):
        c['title']=f'Test question {i+1}'
        for b in c['blocks']:b['text']='A synthetic explanation, not a scientific claim.'
        for b in c['background']:b.update(title='Test background',text='No external scientific knowledge is asserted.')
    for r in d['relations']:r['type']='Reading progression'
    d['evidence'][-1]['captions']=[]
    d['evidence'][-1]['caption_missing_reason']='Synthetic missing-caption test.'
    (root/'audit/report.md').write_text('# Software review\nSynthetic only; no scientific validation.\n',encoding='utf-8')
    path.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
    return path,d

def run(root, baseline=None):
    script=Path(__file__).with_name('build_reader.py')
    checks=[]
    def check(name,value):
        if not value:raise AssertionError(name)
        checks.append(name)
    def build(path, target=script):
        return subprocess.run([sys.executable,'-X','utf8',str(target),str(path)],cwd=root,capture_output=True,text=True,encoding='utf-8')
    zh=fixture(root/'zh',1,1)
    if baseline:
        check('legacy_baseline_build',build(zh,baseline).returncode==0)
        previous=(zh.parent/'reading.md').read_bytes()
    check('legacy_zh_default_build',build(zh).returncode==0)
    if baseline:check('legacy_chinese_markdown_byte_identical',previous==(zh.parent/'reading.md').read_bytes())
    check('legacy_zh_document_language','<html lang="zh-CN">' in (zh.parent/'read.html').read_text(encoding='utf-8'))
    source,d=english_fixture(root/'en')
    before=sha(source)
    source_hash=sha(source.parent/'synthetic-source.txt')
    images={a['path']:sha(source.parent/a['path']) for a in d['assets']}
    check('english_build',build(source).returncode==0)
    html=(source.parent/'read.html').read_text(encoding='utf-8')
    md=(source.parent/'reading.md').read_text(encoding='utf-8')
    check('english_html_language','<html lang="en">' in html)
    check('english_markdown_labels','## Evidence ledger' in md and '**AI inference' in md)
    check('raw_quotation_preserved','Original source quotation: 保留原文' in md)
    check('no_other_chinese_in_english_notes',not re.search(r'[\u3400-\u9fff]',md.replace('保留原文','')))
    check('english_audit_link','href="audit/report.md"' in html)
    check('canonical_input_unchanged',sha(source)==before)
    check('source_and_assets_unchanged',sha(source.parent/'synthetic-source.txt')==source_hash and all(sha(source.parent/p)==v for p,v in images.items()))
    catalog=json.loads((script.parents[1]/'assets/locales/en.json').read_text(encoding='utf-8'))
    custom=copy.deepcopy(d);custom['presentation']={'language':'qaa','labels':{k:'TEST '+v for k,v in catalog.items()}}
    custom_path=source.parent/'custom.json';custom_path.write_text(json.dumps(custom,ensure_ascii=False),encoding='utf-8')
    check('complete_custom_catalog',build(custom_path).returncode==0)
    check('custom_catalog_used','## TEST Evidence ledger' in (source.parent/'reading.md').read_text(encoding='utf-8'))
    outputs={p:sha(source.parent/p) for p in ['read.html','reading.md']}
    for name,presentation in [('missing_catalog',{'language':'fr'}),('missing_format_argument',{'language':'en','labels':{'验证状态：{status}':'Status'}}),('unsafe_audit_path',{'language':'en','audit_path':'../outside.md'})]:
        invalid=copy.deepcopy(d);invalid['presentation']=presentation
        custom_path.write_text(json.dumps(invalid,ensure_ascii=False),encoding='utf-8')
        check(name+'_rejected',build(custom_path).returncode!=0)
        check(name+'_preserves_outputs',all(sha(source.parent/p)==v for p,v in outputs.items()))
    check('restore_english_fixture',build(source).returncode==0)
    print(json.dumps({'status':'passed','checks':checks,'scope':'synthetic software tests only; prompt language is selected by the agent, not by the renderer'}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);ap.add_argument('--baseline',type=Path);args=ap.parse_args()
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False);run(args.output.resolve(),args.baseline.resolve() if args.baseline else None)
    else:
        with tempfile.TemporaryDirectory(prefix='reader-language-') as tmp:run(Path(tmp),args.baseline.resolve() if args.baseline else None)
