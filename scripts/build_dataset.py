"""Rebuild the versioned dataset offline from retained official catalog captures."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'data/sjsu/2026-2027'
SRC = DEST / 'sources'

def clean(text):
    """Normalize catalog spaces and remove invisible characters."""
    return text.replace('\xa0', ' ').replace('\u200b', '').strip()

def field(text, label):
    """Extract a labeled catalog section, or return an empty string."""
    match = re.search(rf'{re.escape(label)}\s*(.*?)(?=\n(?:Prerequisite\(s\):|Corequisite\(s\):|Grading:|Note\(s\):|Cross-listed|High Impact|Sustainability|Class Schedule)|\Z)', text, re.S)
    return re.sub(r'\s+', ' ', match[1]).strip() if match else ''

def build():
    """Write normalized courses and metadata from saved catalog captures."""
    roadmap = json.loads((SRC/'roadmap_course_details.json').read_text())
    details = {x['id']: x for x in json.loads((SRC/'course_details.json').read_text()) + roadmap}
    memberships = {}
    for heading, cid, listing in json.loads((SRC/'ge_index.json').read_text()):
        area = re.search(r'(?:UD Area |Area )?(\d(?:[ABC]|/5)?)\.', heading)[1]
        if heading.startswith('UD'): area = 'UD '+area
        memberships.setdefault(cid, []).append({'area':area, 'label':heading, 'listing':clean(listing)})
    roadmap_ids = {x['id'] for x in roadmap}
    courses = []
    for cid, item in details.items():
        text = clean(item['text'])
        m = re.search(r'^([A-Z][A-Z0-9]* \d+[A-Z]*)\s*-\s*(.+)\n+([\d.]+)(?:\s*[-–]\s*([\d.]+))? unit\(s\)\n', text, re.M)
        if not m: raise ValueError(f'Unparsed course {cid}: {text[:180]}')
        code, title, lo, hi = m.groups()
        body = text[m.end():].split('Class Schedule')[0].strip()
        description = re.split(r'\n(?:Satisfies|Prerequisite|Corequisite|Grading|Note\(s\)|Cross-listed)', body)[0].strip()
        ge = memberships.get(cid, [])
        areas = sorted({g['area'] for g in ge})
        if any('(L)' in g['listing'] for g in ge) and any(a in areas for a in ['5A','5B']): areas.append('5C')
        number = int(re.search(r'\d+', code.split()[1])[0])
        courses.append(dict(course_id=f'sjsu:23:{cid}', catalog_id=cid, catalog_year='2026-2027', code=code, title=title,
            units_min=float(lo),units_max=float(hi or lo),level='Upper division' if number>=100 else 'Lower division',subject=code.split()[0],
            description=description,prerequisites_raw=field(body,'Prerequisite(s):'),corequisites_raw=field(body,'Corequisite(s):'),notes=field(body,'Note(s):'),
            ge_areas=sorted(set(areas)),ge_memberships=ge,swe_role='Roadmap course / option' if cid in roadmap_ids else ('Math/science elective option' if not ge else 'GE option'),
            source_url=f'https://catalog.sjsu.edu/preview_course.php?catoid=23&coid={cid}&print',source_text=text))
    courses.sort(key=lambda c:(c['subject'],int(re.search(r'\d+',c['code'].split()[1])[0]),c['code']))
    payload={'schema_version':1,'catalog_year':'2026-2027','retrieved_on':'2026-09-21','courses':courses}
    (DEST/'courses.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    metadata={'catalog_year':'2026-2027','retrieved_on':'2026-09-21','course_count':len(courses),'ge_course_count':len(memberships),'ge_listing_count':sum(map(len,memberships.values())),
      'sha256':hashlib.sha256((DEST/'courses.json').read_bytes()).hexdigest(),'method':'Official public catalog pages read in browser; raw text retained. Offline deterministic normalization.',
      'program_url':'https://catalog.sjsu.edu/preview_program.php?catoid=23&poid=18924',
      'ge_url':'https://catalog.sjsu.edu/preview_program.php?catoid=23&poid=18673',
      'roadmap_url':'https://catalog.sjsu.edu/preview_program.php?catoid=23&poid=19349&returnto=8647'}
    (DEST/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps(metadata,indent=2))

if __name__=='__main__': build()
