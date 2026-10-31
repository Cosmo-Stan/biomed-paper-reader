"""Verify the preserved Portable release, including the embedded ZIP. Stdlib only."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1] / 'portable'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def verify_manifest(root, filename, ignored):
    manifest = json.loads((root / filename).read_text(encoding='utf-8'))
    expected = set()
    for item in manifest['files']:
        path = (root / item['path']).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError('Missing or unsafe manifest entry: ' + item['path'])
        if digest(path.read_bytes()) != item['sha256']:
            raise ValueError('Hash mismatch: ' + item['path'])
        expected.add(item['path'])
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    if actual != expected | set(ignored):
        raise ValueError('File inventory differs: ' + str(sorted(actual ^ (expected | set(ignored)))))
    return manifest

def main():
    zip_name = 'biomed-paper-reader-v1.0-portable.zip'
    manifest = verify_manifest(ROOT, 'SHA256SUMS.json', ['SHA256SUMS.json', zip_name, zip_name + '.sha256'])
    skill = ROOT / 'skill/biomed-paper-reader'
    verify_manifest(skill, 'skill-manifest.json', ['skill-manifest.json'])
    expected = (ROOT / (zip_name + '.sha256')).read_text(encoding='ascii').split()[0]
    if digest((ROOT / zip_name).read_bytes()) != expected:
        raise ValueError('ZIP hash mismatch')
    with zipfile.ZipFile(ROOT / zip_name) as archive:
        if archive.testzip() is not None:
            raise ValueError('ZIP CRC failed')
        archive_manifest = json.loads(archive.read('SHA256SUMS.json'))
        if archive_manifest != manifest:
            raise ValueError('ZIP manifest differs')
        if set(archive.namelist()) != {f['path'] for f in manifest['files']} | {'SHA256SUMS.json'}:
            raise ValueError('ZIP inventory differs')
        for item in manifest['files']:
            if digest(archive.read(item['path'])) != item['sha256']:
                raise ValueError('ZIP file hash mismatch: ' + item['path'])
    print(json.dumps({'status':'passed', 'version':'1.0-portable.2', 'package_files':len(manifest['files']), 'zip_sha256':expected}))

if __name__ == '__main__':
    main()
