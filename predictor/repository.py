"""Local SQLite adapter. Replace this module when integrating Joseph's backend."""
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/sjsu/2026-2027'
DEFAULT_DB=Path(os.environ.get('PREDICTOR_DB',str(ROOT/'.runtime/predictor.sqlite3')))
SCHEMA='''
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS course (
 course_id TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, catalog_year TEXT NOT NULL,
 title TEXT NOT NULL, units_min REAL NOT NULL, units_max REAL NOT NULL, record_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS course_ge (
 course_id TEXT NOT NULL REFERENCES course(course_id), area TEXT NOT NULL,
 PRIMARY KEY(course_id, area)
);
CREATE TABLE IF NOT EXISTS student (
 student_id TEXT PRIMARY KEY, profile_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS completed_course (
 student_id TEXT NOT NULL REFERENCES student(student_id), course_code TEXT NOT NULL, grade TEXT NOT NULL,
 PRIMARY KEY(student_id,course_code)
);
CREATE TABLE IF NOT EXISTS semester_plan (
 plan_id TEXT PRIMARY KEY, student_id TEXT NOT NULL REFERENCES student(student_id),
 name TEXT NOT NULL, created_at TEXT NOT NULL, payload_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS plan_course (
 plan_id TEXT NOT NULL REFERENCES semester_plan(plan_id), course_id TEXT NOT NULL REFERENCES course(course_id),
 prior_experience INTEGER NOT NULL, units REAL NOT NULL, difficulty_score REAL NOT NULL, estimated_hours REAL NOT NULL,
 PRIMARY KEY(plan_id,course_id)
);
'''

def connect(path=DEFAULT_DB):
    """Open SQLite with foreign-key checks enabled."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path);db.execute('PRAGMA foreign_keys=ON');return db

def initialize(path=DEFAULT_DB):
    """Create tables, refresh catalog records, and return the dataset."""
    payload=json.loads((DATA/'courses.json').read_text())
    with connect(path) as db:
        db.executescript(SCHEMA)
        for c in payload['courses']:
            db.execute('INSERT INTO course VALUES (?,?,?,?,?,?,?) ON CONFLICT(course_id) DO UPDATE SET code=excluded.code,title=excluded.title,units_min=excluded.units_min,units_max=excluded.units_max,record_json=excluded.record_json',
              (c['course_id'],c['code'],c['catalog_year'],c['title'],c['units_min'],c['units_max'],json.dumps(c)))
            db.execute('DELETE FROM course_ge WHERE course_id=?',(c['course_id'],))
            db.executemany('INSERT INTO course_ge VALUES (?,?)',[(c['course_id'],a) for a in c['ge_areas']])
    return payload

def load_courses(path=DEFAULT_DB):
    """Return stored course records ordered by course code."""
    with connect(path) as db:return [json.loads(r[0]) for r in db.execute('SELECT record_json FROM course ORDER BY code')]

def save_plan(student_id,name,payload,path=DEFAULT_DB):
    """Save a student profile and plan snapshot; return the new plan ID."""
    if not name.strip():raise ValueError('Plan name is required')
    plan_id=str(uuid.uuid4())
    with connect(path) as db:
        db.execute('INSERT INTO student VALUES (?,?) ON CONFLICT(student_id) DO UPDATE SET profile_json=excluded.profile_json',(student_id,json.dumps(payload['student'])))
        db.execute('DELETE FROM completed_course WHERE student_id=?',(student_id,))
        db.executemany('INSERT INTO completed_course VALUES (?,?,?)',[(student_id,k,v) for k,v in payload['student']['completed'].items()])
        db.execute('INSERT INTO semester_plan VALUES (?,?,?,?,?)',(plan_id,student_id,name.strip(),datetime.now(timezone.utc).isoformat(),json.dumps(payload)))
        for r in payload['result']['courses']:
            cid=db.execute('SELECT course_id FROM course WHERE code=?',(r['code'],)).fetchone()
            if cid is None:raise ValueError(f'Unknown course: {r["code"]}')
            db.execute('INSERT INTO plan_course VALUES (?,?,?,?,?,?)',(plan_id,cid[0],r['experience'],r['units'],r['difficulty'],r['weekly_hours']))
    return plan_id

def list_plans(student_id,path=DEFAULT_DB):
    """Return this student’s saved plans, newest first."""
    with connect(path) as db:
        return [{'plan_id':r[0],'name':r[1],'created_at':r[2],'payload':json.loads(r[3])} for r in db.execute('SELECT plan_id,name,created_at,payload_json FROM semester_plan WHERE student_id=? ORDER BY created_at DESC',(student_id,))]
