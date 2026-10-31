"""Presentation labels only. Scientific prose and source quotations are never translated here."""
import html
import json
import re
from pathlib import Path

def resolve_presentation(data):
    config = data.get('presentation', {})
    language = config.get('language', 'zh-CN')
    if not isinstance(language, str) or not re.fullmatch(r'[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*', language):
        raise ValueError('presentation.language must be a language tag, for example en or zh-CN')
    catalog = json.loads((Path(__file__).resolve().parents[1]/'assets/locales/en.json').read_text(encoding='utf-8'))
    supplied = config.get('labels', {})
    if not isinstance(supplied, dict):
        raise ValueError('presentation.labels must be an object')
    if language.lower() in ('zh', 'zh-cn', 'zh-hans', 'zh-hans-cn'):
        labels = {key:key for key in catalog}
    elif language.lower().split('-')[0] == 'en':
        labels = catalog.copy()
    else:
        missing = set(catalog) - set(supplied)
        if missing:
            raise ValueError('Supply a complete presentation.labels catalog for '+language+'; missing: '+', '.join(sorted(missing)))
        labels = {}
    unknown = set(supplied) - set(catalog)
    if unknown:
        raise ValueError('Unknown presentation label keys: '+', '.join(sorted(unknown)))
    labels.update(supplied)
    if any(not isinstance(value, str) or not value.strip() for value in labels.values()):
        raise ValueError('Presentation labels must be nonempty strings')
    # Translators must preserve format arguments; missing fields must not drop evidence values.
    from string import Formatter
    for key, value in labels.items():
        expected = sorted(field for _,field,_,_ in Formatter().parse(key) if field is not None)
        actual = sorted(field for _,field,_,_ in Formatter().parse(value) if field is not None)
        if actual != expected:
            raise ValueError('Presentation format arguments differ: '+key)
    audit_path = config.get('audit_path', 'audit/验收报告.md' if language.lower() in ('zh','zh-cn','zh-hans','zh-hans-cn') else 'audit/report.md')
    if not isinstance(audit_path, str) or not re.fullmatch(r'audit/[\w./ -]+\.md', audit_path) or '..' in audit_path.split('/'):
        raise ValueError('presentation.audit_path must be a relative Markdown path under audit/')
    return dict(language=language, labels=labels, audit_path=audit_path)

def localize_html(template, presentation):
    labels = presentation['labels']
    # Only the static HTML template is processed: never CSS, JavaScript, or paper JSON.
    pattern = '|'.join(re.escape(key) for key in sorted(labels,key=len,reverse=True))
    template = re.sub(pattern, lambda match:html.escape(labels[match.group()],quote=True), template)
    template = template.replace('lang="zh-CN"', 'lang="'+html.escape(presentation['language'],quote=True)+'"')
    return template.replace('audit/验收报告.md', html.escape(presentation['audit_path'],quote=True))
