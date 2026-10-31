"""Rebuild checksums and ZIP for this repository's Portable working copy only."""
import hashlib
import json
from pathlib import Path
import zipfile

root=Path(__file__).resolve().parents[1]/'portable'
skill=root/'skill/biomed-paper-reader'
version=json.loads((skill/'version.json').read_text(encoding='utf-8'))['version']
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def manifest(base,exclude):
    return {'algorithm':'SHA-256','version':version,'files':[{'path':p.relative_to(base).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(base.rglob('*')) if p.is_file() and p.relative_to(base).as_posix() not in exclude]}
def write(path,data):
    with path.open('w',encoding='utf-8',newline='\n') as f:f.write(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
write(skill/'skill-manifest.json',manifest(skill,{'skill-manifest.json'}))
archive=root/'biomed-paper-reader-v1.0-portable.zip'
write(root/'SHA256SUMS.json',manifest(root,{'SHA256SUMS.json',archive.name,archive.name+'.sha256'}))
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.name not in {archive.name,archive.name+'.sha256'}:z.write(p,p.relative_to(root).as_posix())
(root/(archive.name+'.sha256')).write_text(sha(archive)+'  '+archive.name+'\n',encoding='ascii')
print(json.dumps({'version':version,'zip_sha256':sha(archive)}))
