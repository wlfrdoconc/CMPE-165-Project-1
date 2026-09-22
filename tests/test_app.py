from functools import partial
import streamlit as st
from streamlit.testing.v1 import AppTest

def test_sample_student_and_plan_save(tmp_path,monkeypatch):
    st.cache_resource.clear()
    from predictor import repository
    for name in ["initialize", "load_courses", "save_plan", "list_plans"]:
        monkeypatch.setattr(repository, name, partial(getattr(repository, name), path=tmp_path/"app.sqlite3"))
    at=AppTest.from_file(repository.ROOT/'app.py',default_timeout=30).run()
    assert not at.exception
    next(b for b in at.button if b.label=='Load sample student').click().run()
    assert not at.exception
    assert at.session_state['selected']==['CS 146','CMPE 131','COMM 20','AAS 1']
    assert any(m.label=='Total units' and m.value=='12' for m in at.metric)
    next(t for t in at.text_input if t.label=='Plan name').set_value('Test plan')
    next(b for b in at.button if b.label=='Save plan locally').click().run()
    assert not at.exception
    assert any('Plan saved' in s.value for s in at.success)

def test_catalog_filter_add_and_remove_course(tmp_path,monkeypatch):
    st.cache_resource.clear()
    from predictor import repository
    for name in ['initialize','load_courses','save_plan','list_plans']:
        monkeypatch.setattr(repository,name,partial(getattr(repository,name),path=tmp_path/'catalog.sqlite3'))
    at=AppTest.from_file(repository.ROOT/'app.py',default_timeout=30).run()
    next(s for s in at.selectbox if s.label=='Browse').select('All GE options').run()
    next(s for s in at.selectbox if s.label=='GE area').select('1C').run()
    assert not at.exception
    next(b for b in at.button if b.label=='Add this course to my plan').click().run()
    assert not at.exception
    assert len(at.session_state['selected'])==1
    at.multiselect(key='confirmed').set_value(at.session_state['selected']).run()
    at.multiselect(key='selected').set_value(['CS 146']).run()
    assert not at.exception
    assert at.session_state['confirmed']==[]
