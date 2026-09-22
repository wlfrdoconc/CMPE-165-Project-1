"""Uncalibrated planning heuristic v1; never an official course rating."""
import re

VERSION = 'heuristic-v1'
# Description signals are visible and applied equally to all subjects.
SIGNALS = {
    'Quantitative / abstract reasoning':r'\b(algorithm|algorithms|calculus|proof|proofs|cryptography|differential|probability|statistical|statistics|quantum|thermodynamics)\b',
    'Project / studio work':r'\b(project|projects|studio|design project|capstone|fieldwork)\b',
    'Writing / research':r'\b(essays|writing|research|argumentation|rhetorical|rhetoric)\b',
    'Laboratory / practice':r'\b(lab|laboratory|clinical|practicum)\b',
}

def estimate_course(course, year=1, experience=0, units=None):
    """Return difficulty and weekly hours; experience ranges from 0 to 2."""
    units = course['units_min'] if units is None else float(units)
    if not course['units_min']<=units<=course['units_max']:raise ValueError('Units outside catalog range')
    if experience not in (0,1,2):raise ValueError('Experience must be 0, 1, or 2')
    if year not in (1,2,3,4):raise ValueError('Year must be 1–4')
    signals=[name for name,pattern in SIGNALS.items() if re.search(pattern,course['description'],re.I)]
    complexity = min(3,len(signals))*0.55
    upper = 1.0 if course['level']=='Upper division' else 0.0
    preparation = 0.5 if upper and year<=2 else 0.0
    score = max(1,min(10,2+0.55*units+upper+complexity+preparation-0.65*experience))
    # Baseline is 3 total hours/unit/week, adjusted gently for complexity and experience.
    total = units*(3+0.25*len(signals)+0.2*upper-0.2*experience)
    # Contact hours in a catalog can exceed the unit baseline for labs/capstones.
    contacts = sum(float(x) for x in re.findall(r'(?:lecture|lab)\s+(\d+(?:\.\d+)?)\s+hours',course['description'],re.I))
    total=max(total,contacts)
    return {'code':course['code'],'title':course['title'],'units':units,'difficulty':round(score,1),
      'weekly_hours':round(total,1),'hours_low':round(total*0.8,1),'hours_high':round(total*1.2,1),
      'experience':experience,'signals':signals,'explanation':f'{units:g} units; {course["level"].lower()}; '+(', '.join(signals) or 'no extra description signals')+f'; experience adjustment −{0.65*experience:.2f}.',
      'factors':{'base':2,'units':round(.55*units,2),'level':upper,'description':complexity,'early_upper_division':preparation,'experience':-.65*experience}}

def estimate_semester(courses, student, experiences=None, unit_choices=None):
    """Combine unique courses into semester estimates and workload advice."""
    experiences,unit_choices=experiences or {},unit_choices or {}
    unique={c['code']:c for c in courses}
    rows=[estimate_course(c,student.year,experiences.get(c['code'],0),unit_choices.get(c['code'])) for c in unique.values()]
    units=sum(r['units'] for r in rows)
    hours=sum(r['weekly_hours'] for r in rows)
    if not units:return {'model_version':VERSION,'courses':[],'units':0,'difficulty':0,'weekly_hours':0,'hours_low':0,'hours_high':0,'balance':'No courses selected','warnings':[],'recommendation':'Choose courses to see an estimate.'}
    average=sum(r['difficulty']*r['units'] for r in rows)/units
    score=round(min(10,average*(units/15)**0.5),1)
    heavy=sum(r['difficulty']>=6 for r in rows)
    project=sum('Project / studio work' in r['signals'] for r in rows)
    warnings=[]
    if units>18:warnings.append('More than 18 units: check your weekly time budget and enrollment limits.')
    if hours>45:warnings.append('Estimated academic work exceeds 45 hours per week, before employment or commuting.')
    if heavy>=3:warnings.append(f'{heavy} demanding courses may concentrate deadlines and difficult material.')
    if project>=3:warnings.append(f'{project} project or studio courses may create overlapping deadlines.')
    hardest=max(rows,key=lambda r:r['difficulty'])
    recommendation=(f'Consider moving {hardest["code"]} to another term or reducing units, after checking degree sequencing.' if warnings else 'Compare the weekly estimate with your available time; keep space for deadlines and other commitments.')
    return {'model_version':VERSION,'courses':rows,'units':units,'difficulty':score,'weekly_hours':round(hours,1),'hours_low':round(sum(r['hours_low'] for r in rows),1),'hours_high':round(sum(r['hours_high'] for r in rows),1),'balance':'Heavy workload' if warnings else 'Manageable estimate','warnings':warnings,'recommendation':recommendation}
