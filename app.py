"""Run with: streamlit run app.py"""
from dataclasses import asdict
import json
import re
import uuid
import pandas as pd
import streamlit as st
from predictor import repository
from predictor.eligibility import Student, GRADES, check
from predictor.scoring import estimate_semester

st.set_page_config(page_title='Semester Compass · SJSU SWE',page_icon='🧭',layout='centered')

st.markdown('''
<style>
.block-container{padding-top:2.5rem;padding-bottom:4rem;max-width:820px;}
h1,h2,h3{letter-spacing:-.01em;}
h1{font-weight:700;}
/* Tabs */
div[data-baseweb="tab-list"]{gap:.25rem;border-bottom:1px solid #e5e9f0;margin-bottom:1.25rem;}
button[data-baseweb="tab"]{padding:.5rem .9rem;font-weight:500;}
/* Buttons */
.stButton>button,.stDownloadButton>button,.stLinkButton>a,.stFormSubmitButton>button{border-radius:10px;font-weight:600;}
/* Bordered containers as clean cards */
div[data-testid="stVerticalBlockBorderWrapper"]{border-radius:14px;border-color:#e5e9f0;}
/* Metrics as soft cards */
div[data-testid="stMetric"]{background:#f7f9fc;border:1px solid #eef1f6;border-radius:12px;padding:.9rem 1rem;}
/* Inputs */
div[data-baseweb="select"]>div,.stTextInput input,.stTextArea textarea,.stNumberInput input{border-radius:10px;}
/* Expanders */
details{border-radius:12px !important;border-color:#e5e9f0 !important;}
</style>
''',unsafe_allow_html=True)

@st.cache_resource
def bootstrap():
    """Create the local database and return its course records."""
    repository.initialize()
    return repository.load_courses()

courses=bootstrap()
by_code={c['code']:c for c in courses}
metadata=json.loads((repository.DATA/'metadata.json').read_text())
if 'student_id' not in st.session_state:st.session_state.student_id=str(uuid.uuid4())

def demo():
    """Load a sample student and course selection into the session."""
    st.session_state.update(confirmed=[],year=2,earned_units=32.0,completed=['CS 46A','CS 46B','MATH 30','MATH 42','ENGL 1A'],selected=['CS 146','CMPE 131','COMM 20','AAS 1'],java_46a=True,java_46b=True)
    for c in st.session_state.completed:st.session_state['grade_'+c]='B'

st.caption('SJSU SOFTWARE ENGINEERING · 2026–2027')
st.title('Plan a semester that fits.')
st.write('Tell us where you are, pick your courses, and see what your week could look like.')
background_tab,catalog_tab,plan_tab,saved_tab,about_tab=st.tabs([
    '1 · Your background','2 · Pick courses','3 · Review semester','Saved plans','About'])

with background_tab:
    st.subheader('Start with the basics')
    st.caption('You can explore now and fill in the details later.')
    left,right=st.columns([2,1])
    with left:
        year=st.selectbox('Student year',[1,2,3,4],key='year')
        completed=st.multiselect('Completed SJSU courses / approved equivalents',list(by_code),key='completed',placeholder='Search courses you have already taken')
    with right:
        st.write('**Just trying it out?**')
        st.button('Load sample student',on_click=demo,width='stretch')
        st.caption('Loads an example profile and four courses.')
    grades={}
    with st.expander('Grades and transfer credit'):
        student_type=st.selectbox('Student type',['First-time undergraduate','Transfer student','Returning student'])
        st.caption('For transfer credit, use the confirmed SJSU equivalent. Unknown grades may need review.')
        if not completed:st.caption('Select completed courses above to enter their grades.')
        grade_columns=st.columns(2)
        for i,code in enumerate(completed):
            grades[code]=grade_columns[i%2].selectbox(code,['Unknown','CR / transfer credit']+list(GRADES),key='grade_'+code)
        extra=st.text_area('Other prerequisite courses',placeholder='CS 47, B\nCMPE 50, C',help='One SJSU course code and grade per line for prerequisites outside this catalog.')
    for line in extra.splitlines():
        if not line.strip():continue
        pair=[p.strip().upper() for p in line.split(',')]
        if len(pair)==2 and re.fullmatch(r'[A-Z][A-Z0-9]* \d+[A-Z]*',pair[0]) and pair[1] in GRADES:
            grades[pair[0]]=pair[1]
        else:st.warning(f'Could not read: {line}. Use CODE, GRADE.')
    with st.expander('Placement and upper-division details'):
        earned=st.number_input('Total earned units',min_value=0.0,max_value=300.0,step=1.0,key='earned_units',help='Include accepted transfer units. Upper division standing depends on earned units.')
        core=st.checkbox('Core GE completion confirmed')
        java_a=st.checkbox('CS 46A was taught in Java',key='java_46a')
        java_b=st.checkbox('CS 46B was taught in Java',key='java_46b')
        standing=st.checkbox('Good academic/major standing and applied for graduation')
    with st.expander('Study preference (optional)'):
        style=st.selectbox('Study preference',['No preference','Practice problems','Reading and notes','Discussion','Hands-on projects'])
        st.caption('Used for study advice, not your score.')
    student=Student(year,earned,student_type,style,grades,core,java_a,java_b,standing)
    st.info('Next: open **2 · Pick courses** to build your semester.')

with catalog_tab:
    st.subheader('Build your course list')
    selected=st.multiselect('Your selected courses',list(by_code),format_func=lambda code:code,key='selected')
    st.caption('Search below to add courses, or use this box to add and remove them directly.')
    experiences={};unit_choices={}
    if selected:
        st.session_state.confirmed=[c for c in st.session_state.get('confirmed',[]) if c in selected]
        with st.expander('Adjust experience and units (optional)',expanded=False):
            for code in selected:
                c=by_code[code]
                cols=st.columns([3,1])
                experiences[code]=cols[0].selectbox(f'{code} — prior experience',[0,1,2],format_func=lambda x:['New to these concepts','Some exposure','Substantial practice'][x],key='exp_'+code)
                if c['units_min']!=c['units_max']:
                    unit_choices[code]=cols[1].number_input(f'{code} units',min_value=c['units_min'],max_value=c['units_max'],value=c['units_min'],step=.5,key='units_'+code)
                else:cols[1].caption(f'{c["units_min"]:g} units')
        with st.expander('Confirm conditions checked outside this app'):
            st.write('Only confirm a course after reviewing all catalog prerequisites, restrictions, grade/placement requirements, and concurrent enrollment with an advisor or official record.')
            student.verified_conditions=st.multiselect('Courses with all conditions independently confirmed',selected,key='confirmed')



    st.divider()
    f1,f2=st.columns([1,2])
    scope=f1.selectbox('Browse',['SWE roadmap','All GE options','Math/science electives','All courses'])
    query=f2.text_input('Search code, title, or description',placeholder='Try CS 146, biology, or writing')
    with st.expander('Filter by GE area or eligibility'):
        area=st.selectbox('GE area',['All']+sorted({a for c in courses for a in c['ge_areas']}))
        status_filter=st.selectbox('Eligibility filter',['All','Eligible on entered information','Needs review','Not eligible','Completed'])
        st.caption('SWE waives Area 1B and PE; several other GE areas are covered by major courses.')
    shown=[]
    for c in courses:
        if scope=='SWE roadmap' and c['swe_role']!='Roadmap course / option':continue
        if scope=='All GE options' and not c['ge_areas']:continue
        if scope=='Math/science electives' and not (any(a in c['ge_areas'] for a in ['5A','5B','5C']) or c['code'] in ['MATH 32','MATH 108','MATH 115','MATH 126','MATH 142','MATH 150','MATH 170']):continue
        if area!='All' and area not in c['ge_areas']:continue
        if query.lower() not in (c['code']+' '+c['title']+' '+c['description']).lower():continue
        e=check(c,student,st.session_state.get('selected',[]))
        if status_filter!='All' and e.status!=status_filter:continue
        shown.append({'Course':c['code'],'Title':c['title'],'Units':str(c['units_min']) if c['units_min']==c['units_max'] else f'{c["units_min"]}–{c["units_max"]}','GE areas':', '.join(c['ge_areas']),'Eligibility':e.status})
    st.caption(f'{len(shown)} courses found')
    with st.expander('See all matching courses'):
        st.dataframe(shown,hide_index=True,width='stretch')
    if shown:
        inspect=st.selectbox('View course details',[r['Course'] for r in shown])
        c=by_code[inspect]
        with st.container(border=True):
            st.subheader(f'{c["code"]} · {c["title"]}')
            e=check(c,student,st.session_state.get('selected',[]))
            units=f'{c["units_min"]:g}' if c['units_min']==c['units_max'] else f'{c["units_min"]:g}–{c["units_max"]:g}'
            st.caption(f'{units} units · {c["level"]} · {e.status}')
            with st.expander('Description and prerequisites'):
                st.write(c['description'])
                for reason in e.reasons:st.write('• '+reason)
                st.write('**Prerequisites:** '+(c['prerequisites_raw'] or 'None listed.'))
                if c['corequisites_raw']:st.write('**Corequisites:** '+c['corequisites_raw'])
                if c['notes']:st.write('**Notes:** '+c['notes'])
                for g in c['ge_memberships']:st.caption(g['area']+' · '+g['listing'])
                st.link_button('View official catalog',c['source_url'])
        def add_course():
            """Add the viewed course to the plan without duplicates."""
            st.session_state.selected=list(dict.fromkeys(st.session_state.get('selected',[])+[inspect]))
        st.button('Add this course to my plan',on_click=add_course,type='primary',disabled=inspect in st.session_state.get('selected',[]))
    else:st.info('No matches. Try another search or clear a filter.')
    if selected:st.info(f'{len(selected)} courses selected · Next: open **3 · Review semester**.')


with plan_tab:
    results=estimate_semester([by_code[c] for c in selected],student,experiences,unit_choices)
    eligibility={code:asdict(check(by_code[code],student,selected)) for code in selected}
    with st.container(border=True):
        st.subheader('Your semester at a glance')
        a,b,c=st.columns(3)
        a.metric('Difficulty estimate',f'{results["difficulty"]:.1f} / 10' if selected else '—')
        b.metric('Total units',f'{results["units"]:g}')
        c.metric('Academic workload / week',f'{results["hours_low"]:g}–{results["hours_high"]:g} hours' if selected else '—')
        st.caption('Rough estimates, including class and study time. Not an official course rating.')
        if selected:
            st.write(f'**{results["balance"]}**')
            for message in results['warnings']:st.warning(message)
            st.info(results['recommendation'])
            advice={'Practice problems':'Schedule short problem-solving sessions across the week.','Reading and notes':'Reserve reading blocks before class and time to consolidate notes.','Discussion':'Arrange a regular study group and prepare questions beforehand.','Hands-on projects':'Break projects into weekly milestones and test early.'}
            if style in advice:st.caption(advice[style])
    if selected:
        st.subheader('Course breakdown')
        for code in ['MATH 30','MATH 31','PHYS 50']:
            grade=student.completed.get(code)
            if grade in GRADES and 0.7<=GRADES[grade]<2.0:
                st.warning(f'{code}: your entered grade {grade} is below the SWE degree minimum of C, even if a later course accepts C− as a prerequisite.')
        rows=[{'Course':r['code'],'Units':r['units'],'Difficulty / 10':r['difficulty'],'Hours / week':r['weekly_hours'],'Eligibility':eligibility[r['code']]['status']} for r in results['courses']]
        st.dataframe(rows,hide_index=True,width='stretch')
        with st.expander('Compare weekly workload'):
            st.bar_chart(pd.DataFrame(results['courses']).set_index('code')[['weekly_hours']],color='#087e8b')
        for row in sorted(results['courses'],key=lambda r:r['difficulty'],reverse=True):
            c=by_code[row['code']]; e=eligibility[c['code']]
            with st.expander(f'{c["code"]} · {c["title"]} — {e["status"]}'):
                for reason in e['reasons']:st.write('• '+reason)
                st.write(c['description'])
                st.write('**Estimate factors:** '+row['explanation'])
                st.write('**Prerequisites:** '+(c['prerequisites_raw'] or 'None listed.'))
                if c['corequisites_raw']:st.write('**Corequisites:** '+c['corequisites_raw'])
                if c['notes']:st.write('**Catalog notes:** '+c['notes'])
                if c['ge_memberships']:st.write('**GE listing conditions:** '+'; '.join(g['listing'] for g in c['ge_memberships']))
                st.link_button('Official course catalog',c['source_url'])
        payload={'schema_version':1,'catalog_year':'2026-2027','dataset_sha256':metadata['sha256'],'student':asdict(student),'result':results,'eligibility':eligibility}
        st.download_button('Download plan JSON',json.dumps(payload,indent=2),file_name='semester-plan.json',mime='application/json')
        with st.form('save_plan'):
            plan_name=st.text_input('Plan name',placeholder='Fall 2026 · Option A')
            if st.form_submit_button('Save plan locally'):
                if plan_name.strip():
                    repository.save_plan(st.session_state.student_id,plan_name,payload);st.success('Plan saved. See Saved plans.')
                else:st.error('Enter a name for this plan.')
    else:st.info('Open **2 · Pick courses** to start your plan.')

with saved_tab:
    st.subheader('Compare saved plans')
    st.caption('Saved to local SQLite for this browser session. Download JSON to retain a portable copy; a new session receives a new anonymous profile.')
    plans=repository.list_plans(st.session_state.student_id)
    if not plans:st.info('Save a plan from the planner to compare alternatives here.')
    for p in plans:
        r=p['payload']['result']
        with st.expander(f'{p["name"]} · {r["units"]:g} units · {r["difficulty"]}/10'):
            st.write(', '.join(x['code'] for x in r['courses']))
            st.write(f'{r["hours_low"]}–{r["hours_high"]} academic hours/week')
            st.download_button('Download saved plan',json.dumps(p['payload'],indent=2),file_name='saved-plan.json',key=p['plan_id'])

with about_tab:
    st.subheader('Transparent estimates, useful conversations')
    st.write('This MVP supports Software Engineering at SJSU using a fixed 2026–2027 public catalog snapshot. It is a semester planning prototype, not a degree audit or registration system.')
    st.write('Course difficulty = 2 + 0.55 × units + 1 for upper division + 0.55 per description signal (up to 3) + 0.5 for early-year upper division − 0.65 per experience level, bounded to 1–10. Signals include quantitative reasoning, projects, writing/research, and labs. GE courses are not assumed to be easy.')
    st.write('Semester difficulty scales the unit-weighted average by √(total units / 15), capped at 10. Weekly hours start at 3 per unit, with small signal, level, and experience adjustments. These are team-defined heuristics, not trained or validated predictions.')
    st.write('Eligibility uses explicit SWE rules where modeled. Other requirements retain their original catalog wording and require review. A course selected this semester cannot satisfy a prerequisite that must already be completed; capstone corequisites are checked together.')
    st.write('Transfer credit and CR grades require verification of equivalence and minimum grades. Course offerings, seats, timetable conflicts, full graduation requirements, and professor-specific ratings are outside this MVP.')
    st.markdown('**SWE requirement notes**\n\n- 120 total units; 6 advisor-approved upper division technical elective units and 6 university elective units.\n- Choose MATH 33LA or MATH 142; choose MATH 161A or ISE 130.\n- Additional math/science electives: 7 units from the approved set. Avoid counting one course twice toward distinct unit requirements.\n- MATH 30, MATH 31, and PHYS 50 require C or higher for the degree, even when a prerequisite rule accepts C−.\n- ENGR 100W covers UD 2/5 and GWAR; the four-course engineering capstone combination covers UD 3/4, subject to catalog grades and sequence conditions.\n- American Institutions (US1/2/3) can overlap approved GE choices; verify the exact course/sequence conditions.')
    for label,key in [('SWE degree requirements','program_url'),('GE requirements','ge_url'),('Suggested four-year roadmap','roadmap_url')]:st.link_button(label,metadata[key])
    st.download_button('Download complete course dataset',(repository.DATA/'courses.json').read_bytes(),file_name='sjsu-2026-2027-courses.json',mime='application/json')
