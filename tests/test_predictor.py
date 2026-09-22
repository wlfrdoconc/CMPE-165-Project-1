import json
from dataclasses import asdict
from pathlib import Path
import pytest
from predictor import repository
from predictor.eligibility import Student, check
from predictor.scoring import estimate_course, estimate_semester

DATA=json.loads((repository.DATA/'courses.json').read_text())
COURSES={c['code']:c for c in DATA['courses']}

def test_catalog_complete_and_consistent():
    assert len(COURSES)==492
    assert len({c['course_id'] for c in DATA['courses']})==492
    assert sum(bool(c['ge_memberships']) for c in DATA['courses'])==467
    assert sum(len(c['ge_memberships']) for c in DATA['courses'])==475
    assert all(c['description'] and c['source_text'] and c['units_min']<=c['units_max'] for c in DATA['courses'])
    assert set(COURSES['PHYS 50']['ge_areas'])=={'5A','5C'}
    assert 'UD 3' in COURSES['CMPE 195B']['ge_areas']
    assert COURSES['MATH 31']['units_min']==4
    for code in ['MATH 108','MATH 115','MATH 126','MATH 150','MATH 170']:assert code in COURSES

def test_or_prerequisite_and_minimum_grade():
    c=COURSES['CMPE 131']
    assert check(c,Student(completed={'CS 46B':'C-'})).status.startswith('Eligible')
    assert check(c,Student(completed={'CMPE 50':'B'})).status.startswith('Eligible')
    assert check(c,Student(completed={'CS 46B':'D'})).status=='Not eligible'
    assert check(c,Student(completed={'CS 46B':'CR / transfer credit'})).status=='Needs review'

def test_and_grouping():
    c=COURSES['CMPE 120']
    assert check(c,Student(completed={'CS 46B':'B','CS 47':'B'})).status.startswith('Eligible')
    assert check(c,Student(completed={'CS 46B':'B'})).status=='Not eligible'

def test_java_is_not_assumed_and_planned_is_not_completed():
    s=Student(completed={'MATH 30':'B','MATH 42':'B','CS 46B':'B'})
    assert check(COURSES['CS 146'],s).status=='Needs review'
    s.java_46b=True
    assert check(COURSES['CS 146'],s).status.startswith('Eligible')
    assert check(COURSES['CMPE 131'],Student(),['CS 46B']).status=='Not eligible'

def test_capstone_corequisites_and_minimum_grade():
    s=Student(completed={'CMPE 195A':'C'})
    assert check(COURSES['CMPE 195B'],s).status=='Not eligible'
    assert check(COURSES['CMPE 195B'],s,['ENGR 195B']).status.startswith('Eligible')
    s.completed['CMPE 195A']='C-'
    assert check(COURSES['CMPE 195B'],s,['ENGR 195B']).status=='Not eligible'

def test_upper_standing_uses_units_not_year():
    assert check(COURSES['ISE 164'],Student(year=4,earned_units=30)).status=='Not eligible'
    assert check(COURSES['ISE 164'],Student(year=2,earned_units=65)).status.startswith('Eligible')

def test_completed_and_exclusion():
    assert check(COURSES['CS 146'],Student(completed={'CS 146':'B'})).status=='Completed'
    assert check(COURSES['ENGL 1B'],Student(completed={'ENGL 2':'B','ENGL 1A':'A'})).status=='Not eligible'

def test_variable_units_and_experience():
    c=COURSES['BIOL 150']
    low=estimate_course(c,units=1);high=estimate_course(c,units=2)
    assert high['weekly_hours']>low['weekly_hours']
    with pytest.raises(ValueError):estimate_course(c,units=3)
    assert estimate_course(COURSES['CS 146'],experience=2)['difficulty']<estimate_course(COURSES['CS 146'])['difficulty']

def test_semester_load_and_deduplication():
    s=Student(year=3)
    one=estimate_semester([COURSES['CS 146']],s)
    two=estimate_semester([COURSES['CS 146'],COURSES['CS 149']],s)
    duplicate=estimate_semester([COURSES['CS 146']]*2,s)
    assert two['weekly_hours']>one['weekly_hours']
    assert two['difficulty']>one['difficulty']
    assert duplicate==one
    assert estimate_semester([],s)['difficulty']==0

def test_learning_style_does_not_change_score():
    assert estimate_semester([COURSES['CS 146']],Student(learning_style='Reading'))==estimate_semester([COURSES['CS 146']],Student(learning_style='Practice'))

def test_sqlite_roundtrip_isolation_and_parameterization(tmp_path):
    path=tmp_path/'test.sqlite3';repository.initialize(path)
    assert len(repository.load_courses(path))==492
    s=Student(completed={'CS 46B':'B'})
    payload={'student':asdict(s),'result':estimate_semester([COURSES['CMPE 131']],s)}
    name="Fall'); DROP TABLE course; --"
    repository.save_plan('student-1',name,payload,path)
    assert repository.list_plans('student-1',path)[0]['payload']==payload
    assert repository.list_plans('student-2',path)==[]
    repository.initialize(path)
    assert repository.list_plans('student-1',path)[0]['name']==name
    assert len(repository.load_courses(path))==492
