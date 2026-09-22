"""Conservative, explainable prerequisite checks for the SWE MVP.

Rules cover the normal SWE pathway. Catalog alternatives that require placement,
consent, articulation, or interpretation remain reviewable, never guessed.
"""
from dataclasses import dataclass, field
import re

GRADES = {'A+':4.0,'A':4.0,'A-':3.7,'B+':3.3,'B':3.0,'B-':2.7,'C+':2.3,'C':2.0,'C-':1.7,'D+':1.3,'D':1.0,'D-':0.7,'F':0.0}

@dataclass
class Student:
    """Student inputs, completed-course grades, and confirmed conditions."""
    year: int = 1
    earned_units: float = 0
    student_type: str = 'First-time undergraduate'
    learning_style: str = 'No preference'
    completed: dict = field(default_factory=dict)
    core_ge_complete: bool = False
    java_46a: bool = False
    java_46b: bool = False
    good_standing_and_graduation: bool = False
    # Explicit course-specific confirmation of conditions that cannot be automated.
    verified_conditions: list = field(default_factory=list)

@dataclass
class Eligibility:
    """Eligibility status and the reasons shown to the student."""
    status: str
    reasons: list

def course(code, grade='C-'):
    """Build a prerequisite rule for a course and minimum grade."""
    return {'course':code,'grade':grade}
def all_of(*rules):
    """Group rules that must all be satisfied."""
    return {'all':list(rules)}
def any_of(*rules):
    """Group alternatives; satisfying one is enough."""
    return {'any':list(rules)}
def flag(name, label):
    """Build a rule for a student confirmation flag."""
    return {'flag':name,'label':label}
UPPER = {'units':60}
CORE = flag('core_ge_complete','Core GE completion must be confirmed')
JAVA_A = any_of(flag('java_46a','CS 46A was taught in Java'),course('CS 46AW'))
JAVA_B = any_of(flag('java_46b','CS 46B was taught in Java'),course('CS 48'),course('CS 49J'))

RULES = {
 'CMPE 131':any_of(course('CMPE 50'),course('CS 46B')),
 'CMPE 70':any_of(course('CMPE 50'),course('CS 46B')),
 'CMPE 165':any_of(course('CMPE 30'),course('CS 46A')),
 'CMPE 120':all_of(any_of(course('CMPE 50'),course('CS 46B')),any_of(course('CMPE 70'),course('CS 47'))),
 'CS 146':all_of(course('MATH 30'),course('MATH 42'),course('CS 46B'),JAVA_B),
 'CS 149':all_of(any_of(course('CS 47'),course('CMPE 70')),course('CS 146')),
 'CS 157A':course('CS 146'),
 'CS 166':all_of(course('CS 146'),any_of(course('CS 47'),course('CMPE 70'),course('CMPE 120'))),
 'CMPE 187':course('CMPE 131'),
 'CMPE 148':all_of(course('CMPE 120'),course('CS 146')),
 'CMPE 172':any_of(course('CMPE 142'),course('CS 149')),
 'MATH 33LA':course('MATH 31'),
 'MATH 142':all_of(course('MATH 31'),course('MATH 42')),
 'MATH 161A':course('MATH 31'),
 'ISE 130':course('MATH 32','D-'),
 'ISE 164':UPPER,
 'ENGL 1B':any_of(course('ENGL 1A'),course('ENGL 1AS')),
 'ENGR 100W':all_of(any_of(course('ENGL 1B'),{'review':'Equivalent second-semester composition may qualify'}),CORE,UPPER),
 'CMPE 195A':all_of(course('CS 146'),course('CMPE 131'),course('ENGR 100W','C'),CORE,UPPER,flag('good_standing_and_graduation','Good academic/major standing and graduation application must be confirmed')),
 'CMPE 195B':course('CMPE 195A','C'),
 'ENGR 195A':all_of(course('ENGR 100W','C'),CORE,UPPER),
 'ENGR 195B':all_of(course('ENGR 195A','C'),CORE,UPPER),
}
COREQUISITES = {'CMPE 195A':'ENGR 195A','ENGR 195A':'CMPE 195A','CMPE 195B':'ENGR 195B','ENGR 195B':'CMPE 195B'}

# Missing normal-path prerequisites can have alternate consent/equivalent paths.
ALTERNATIVES = {'CMPE 165','CS 146','CS 149','CS 157A','CS 166','MATH 33LA','MATH 142','MATH 161A'}

def evaluate(rule, student):
    """Return (met/unmet/review, explanations); AND and OR are not flattened."""
    if 'course' in rule:
        code, minimum = rule['course'], rule['grade']
        grade = student.completed.get(code)
        if grade in GRADES:
            met = GRADES[grade] >= GRADES[minimum]
            return ('met' if met else 'unmet'), ([] if met else [f'{code}: needs {minimum} or higher; entered {grade}'])
        if grade is not None:
            return 'review', [f'{code}: verify grade equivalence ({grade}) against minimum {minimum}']
        return 'unmet', [f'{code} with {minimum} or higher is missing']
    if 'units' in rule:
        return ('met',[]) if student.earned_units>=rule['units'] else ('unmet',[f"Requires at least {rule['units']} earned units"])
    if 'flag' in rule:
        return ('met',[]) if getattr(student,rule['flag']) else ('review',[rule['label']])
    if 'review' in rule: return 'review',[rule['review']]
    key = 'all' if 'all' in rule else 'any'
    results = [evaluate(r,student) for r in rule[key]]
    states = [r[0] for r in results]
    if key=='all': status = 'unmet' if 'unmet' in states else ('review' if 'review' in states else 'met')
    else: status = 'met' if 'met' in states else ('review' if 'review' in states else 'unmet')
    if status=='met': return status,[]
    reasons = [x for state,rs in results if state!='met' for x in rs]
    if key=='any': reasons = ['One of: '+ '; '.join(reasons)]
    return status,reasons

def check(course_record, student, planned=()):
    """Return eligibility using completed courses and planned corequisites."""
    code = course_record['code']
    grade = student.completed.get(code)
    if grade in GRADES and GRADES[grade]>=0.7:
        return Eligibility('Completed',[f'Entered completed grade: {grade}. Degree minimums may be higher.'])
    if code=='ENGL 1B' and student.completed.get('ENGL 2') in GRADES and GRADES[student.completed['ENGL 2']]>=0.7:
        return Eligibility('Not eligible',['Catalog excludes students who have successfully completed ENGL 2.'])
    if code in student.verified_conditions:
        return Eligibility('Confirmed by student',['Student reports all catalog prerequisites, restrictions, and corequisites have been verified.'])
    if code in RULES:
        status,reasons=evaluate(RULES[code],student)
        if status=='unmet' and code in ALTERNATIVES:
            status='review'; reasons.append('An instructor-consent or equivalent-course pathway may apply; verify the catalog conditions.')
    else:
        raw = course_record['prerequisites_raw']
        # Exact standard UD GE statement; additional conditions stay manual.
        standard = re.sub(r'\s+',' ',raw).strip()
        ud_standard = re.fullmatch(r'Completion of Core General Education and upper division standing are prerequisites to all (?:UD GE|SJSU Studies) courses\.(?: Completion of, or co-registration in, 100W is strongly recommended\.)?',standard,re.I)
        if ud_standard:
            status,reasons=evaluate(all_of(CORE,UPPER),student)
        elif raw:
            status,reasons='review',['Review the catalog prerequisite text, including placement, grades, and major restrictions.']
        else:
            status,reasons='met',['No prerequisite is listed in the captured catalog.']
        restrictions = course_record['notes']+' '+ ' '.join(g['listing'] for g in course_record['ge_memberships'])
        if re.search(r'only|not open|consent|permission|must complete sequence|intensive',restrictions,re.I):
            if status=='met':status='review'
            reasons.append('Additional catalog restrictions or sequence conditions require review.')
    required = COREQUISITES.get(code)
    if required and required not in planned:
        status='unmet';reasons.append(f'Add the concurrent course {required} to this plan.')
    elif course_record['corequisites_raw'] and not required:
        if status=='met':status='review'
        reasons.append('Check the catalog corequisite requirement.')
    labels={'met':'Eligible on entered information','unmet':'Not eligible','review':'Needs review'}
    return Eligibility(labels[status],reasons or ['The modeled prerequisites are satisfied for the SWE pathway.'])
