from pathlib import Path
from collections import Counter
import base64
import json
import os
import random
import uuid
import streamlit as st
from dotenv import load_dotenv
from forge.models import Question, Result
from forge.ingest import extract, InputError, MAX_TEXT
from forge.engine import API, generate, meaning_check, ForgeError
from forge.quality import local_grade, score, validate_question
from forge.storage import save, load_bytes
from forge.exports import pdf_bytes, docx_bytes
from forge.demo import demo
from forge.bank import bank_path, relevant_questions, remember_questions, memory_count, clear_memory
from forge.coverage import coverage_summary
from forge.rapid import build_rapid_deck
from forge.guide import generate_study_guide
from forge.guide_storage import save_guide, load_guide_bytes
from forge.guide_exports import guide_pdf_bytes, guide_docx_bytes
from forge.systems import (
    CORE_SYSTEMS, FORGE_OVERSEER, SCRIBE_AUTOMATON, EXAM_AUTOMATON,
    STUDY_AUTOMATON, REVIEW_AUTOMATON, ARCHIVIST_AUTOMATON,
)
from forge.ui import inject_lab_theme, machine_header, core_chamber, navigate

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')
DATA = Path(os.environ.get('FORGE_DATA_DIR', str(ROOT / 'data')))
GUIDE_DATA = DATA / 'guides'
st.set_page_config(page_title='Hector Study Lab', page_icon='◈', layout='wide')
inject_lab_theme()

if 'session' not in st.session_state:
    st.session_state.session = None
if 'position' not in st.session_state:
    st.session_state.position = 0
if 'epoch' not in st.session_state:
    st.session_state.epoch = 0
if 'guide' not in st.session_state:
    st.session_state.guide = None


def reset_rapid(session_id=None):
    st.session_state.rapid_session_id = session_id
    st.session_state.rapid_deck = []
    st.session_state.rapid_index = 0
    st.session_state.rapid_round = 1
    st.session_state.rapid_answered = False
    st.session_state.rapid_result = None
    st.session_state.rapid_attempts = 0
    st.session_state.rapid_accepted = 0
    st.session_state.rapid_counted = False


if 'rapid_session_id' not in st.session_state:
    reset_rapid()


def persist():
    try:
        save(st.session_state.session, DATA)
    except (OSError, ValueError):
        st.error('Autosave failed. Use Download study set to keep your work before closing.')


def activate(session):
    st.session_state.session = session
    st.session_state.position = 0
    st.session_state.epoch += 1
    reset_rapid(session.id)
    persist()


def persist_guide():
    try:
        save_guide(st.session_state.guide, GUIDE_DATA)
    except (OSError, ValueError):
        st.error('Study-guide autosave failed. Download the JSON guide before closing.')


def activate_guide(guide):
    st.session_state.guide = guide
    persist_guide()


if 'lab_page' not in st.session_state:
    st.session_state.lab_page = 'Core Chamber'
page = st.session_state.lab_page
current = st.session_state.session
current_guide = st.session_state.guide
key = st.session_state.get('api_key', '') or os.environ.get('OPENAI_API_KEY', '')
model = st.session_state.get('model', os.environ.get('OPENAI_MODEL', 'gpt-5.4'))

nav, spacer, settings = st.columns([2, 6, 2])
with nav:
    if page != 'Core Chamber':
        st.button('← Return to Core', on_click=navigate, args=('Core Chamber',), use_container_width=True)
    else:
        st.markdown('<div class="console-wordmark">HECTOR / <b>STUDY LAB</b></div>', unsafe_allow_html=True)
with settings:
    st.button('System settings', on_click=navigate, args=('Settings',), use_container_width=True)
machine_header(page, api_connected=bool(key), session=current, guide=current_guide)

if page in ('Saved sets', 'Saved guides'):
    sets, guides = st.columns(2)
    sets.button('Question archive', on_click=navigate, args=('Saved sets',), use_container_width=True)
    guides.button('Guide archive', on_click=navigate, args=('Saved guides',), use_container_width=True)
if page == 'Study' and current_guide:
    st.button('Open active study guide', on_click=navigate, args=('Study guide',))
if page == 'Study guide' and current:
    st.button('Practice active question set', on_click=navigate, args=('Study',))

if page == 'Core Chamber':
    core_chamber(api_connected=bool(key), session=current, guide=current_guide)
    tools, systems = st.columns([1, 2])
    with tools:
        if st.button('Try the biology demo', use_container_width=True):
            activate(demo())
            navigate('Study')
            st.rerun()
    with systems:
        with st.expander('Core systems · Automaton roles'):
            for system in CORE_SYSTEMS:
                st.markdown(f'**{system.name}**')
                st.caption(system.role)
    st.caption('Review protection is always on. Uncertain answers do not lower your score.')

elif page == 'Settings':
    st.title('Your lab. Your settings.')
    st.markdown(f'<div class="system-line">{FORGE_OVERSEER.name} / configuration</div>', unsafe_allow_html=True)
    st.write('Reuse your existing OpenAI API key. It is kept in this running session unless you put it in your local .env file.')
    st.text_input('OpenAI API key', type='password', value=st.session_state.get('api_key', ''), key='_api_key', on_change=lambda: st.session_state.update(api_key=st.session_state['_api_key']), help='Never included in saved study sets or exports.')
    st.text_input('Model ID', value=st.session_state.get('model', os.environ.get('OPENAI_MODEL', 'gpt-5.4')), key='_model', on_change=lambda: st.session_state.update(model=st.session_state['_model']))
    st.caption('Default: gpt-5.4. You may enter another Responses API model with structured-output support that your API account can access.')
    st.info('Generation, visual reading, trusted expansion and meaning checks send selected material to OpenAI. API usage is billed to your API account. Exact checks, saved practice and exports run locally.')
    st.write('**Question-set limits:** 25 MB per file and 180,000 extracted characters. PDF / PPTX / DOCX / TXT / MD.')
    st.write('**Image-aware guides:** Guide mode accepts PDFs, examines page images at high detail, preserves selected original pages, and audits every inventory item. Up to 50 MB combined and 180,000 extractable characters per guide volume.')
    st.write('**Trusted expansion:** When enabled, thin course material may be expanded using restricted OpenStax, NIH/NCBI, NHGRI, MedlinePlus or CDC web results. Added material is labeled and linked.')
    st.write('**Fair grading:** an exact accepted answer passes locally. Meaning checks can accept equivalent wording. All other responses remain unscored until you resolve them. A disputed question can be excluded entirely.')
    st.write('**Persistence:** submitted answers and sets autosave in the app’s data folder. Text still being typed is not saved. Download JSON for a portable backup.')
    st.subheader('Question Memory')
    memory_file = bank_path(DATA)
    try:
        remembered = memory_count(memory_file)
        st.write(f'Archivist Automaton remembers **{remembered}** released questions locally and compares them only when matching source sections are uploaded again.')
        confirm_clear = st.checkbox('I want to clear remembered-question history', value=False)
        if st.button('Clear Question Memory', disabled=not confirm_clear):
            clear_memory(memory_file)
            st.success('Question Memory cleared. Saved study sets were not deleted.')
            st.rerun()
    except (OSError, ValueError):
        st.warning('Question Memory could not be read. Existing study sets are unaffected.')

elif page == 'Forge a set':
    st.title('Build knowledge. Not repetition.')
    st.markdown('<div class="forge-subtitle">Your slides and notes → distinct concepts → questions worth practicing.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="system-line">{FORGE_OVERSEER.name} coordinating {SCRIBE_AUTOMATON.name} + {EXAM_AUTOMATON.name} + {REVIEW_AUTOMATON.name}</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric('01 / SCRIBE', 'Read every source')
    b.metric('02 / EXAM', 'Build distinct questions')
    c.metric('03 / REVIEW', 'Audit before release')
    st.write('')
    files = st.file_uploader('Drop your chapter material here', type=['pdf', 'pptx', 'docx', 'txt', 'md'], accept_multiple_files=True)
    pasted = st.text_area('Or paste notes', placeholder='Paste teaching material or an outline with supporting notes…', height=110)
    allnames = [f.name for f in files]
    selected = st.multiselect('Include files', allnames, default=allnames) if files else []
    outlines = st.multiselect('Prioritize these study outlines', selected,
        default=[n for n in selected if 'outline' in n.lower()]) if selected else []
    sources, warnings, input_errors = [], [], []
    seen = set()
    for f in files:
        if f.name not in selected:
            continue
        try:
            chunks, notes = extract(f.name, f.getvalue(), f.name in outlines)
            if chunks[0].id in seen:
                warnings.append(f'Skipped a duplicate upload: {f.name}')
                continue
            seen.add(chunks[0].id)
            sources.extend(chunks)
            warnings.extend(notes)
        except Exception as exc:
            input_errors.append(str(exc) if isinstance(exc, InputError) else f'{f.name}: could not read this file; re-export it and try again.')
    if pasted.strip():
        try:
            chunks, notes = extract('Pasted notes.txt', pasted.encode())
            if chunks[0].id not in seen:
                sources.extend(chunks)
            warnings.extend(notes)
        except InputError as exc:
            input_errors.append(str(exc))
    for error in input_errors:
        st.error(error)
    if warnings:
        with st.expander(f'{len(warnings)} extraction notes — review before generating', expanded=True):
            for warning in warnings:
                st.warning(warning)
    characters = sum(len(s.text) for s in sources)
    if characters > MAX_TEXT:
        st.error('Too much material for one set. Select fewer files or split the chapter; no text will be silently dropped.')
    if sources:
        with st.expander(f'Preview readable material · {characters:,} characters / {len(sources)} sections'):
            si = st.selectbox('Source section', range(len(sources)), format_func=lambda i: f'{sources[i].name} · {sources[i].location}')
            st.text(sources[si].text)
    with st.form('generate'):
        title = st.text_input('Study set name', value='Biology · Chapter review')
        left, right = st.columns(2)
        count = left.number_input('Number of distinct questions', min_value=5, max_value=100, value=25, step=5)
        difficulty = right.selectbox('Difficulty', ['Mixed', 'Foundational', 'Standard', 'Challenging'])
        cognitive_levels = st.multiselect('Cognitive levels',
            ['Recall', 'Understanding', 'Application', 'Analysis'],
            default=['Recall', 'Understanding', 'Application'])
        kinds = st.multiselect('Question types', ['Multiple choice', 'Short answer', 'True / false', 'Scenario'],
                              default=['Multiple choice', 'Short answer', 'True / false', 'Scenario'])
        focus = st.text_input('Optional chapter, unit or topic focus', placeholder='For example: Chapter 3 membrane transport')
        st.caption('The Forge plans reserve concepts, retains valid questions across repair attempts, and repairs audit failures. Large sets use more API calls. No repeat-padding.')
        submit = st.form_submit_button('🔥 Forge my study set', type='primary')
    if submit:
        if not key:
            st.error('Add your existing API key in Settings first, or try the free built-in demo.')
        elif input_errors or not sources or characters > MAX_TEXT or not kinds or not cognitive_levels:
            st.error('Check the selected sources, limits and question types above.')
        else:
            bar = st.progress(0, text=f'{SCRIBE_AUTOMATON.name}: sources prepared…')
            api = API(key, model)
            try:
                memory_file = bank_path(DATA)
                try:
                    prior_questions = relevant_questions(memory_file, sources)
                except (OSError, ValueError):
                    prior_questions = []
                    warnings.append('Question Memory could not be read for this run; generation continued without it.')
                session = generate(api, sources, int(count), kinds, difficulty, focus, title,
                                   lambda fraction, text: bar.progress(fraction, text=text),
                                   cognitive_levels=cognitive_levels,
                                   prior_questions=prior_questions)
                session.notices.extend(warnings)
                try:
                    remember_questions(memory_file, session.questions)
                except (OSError, ValueError):
                    session.notices.append('The set was released, but Question Memory could not save this run.')
                activate(session)
                st.success(f'{FORGE_OVERSEER.name} released {len(session.questions)} questions. Return to Core and open Study.')
                st.caption(f'{api.calls} AI calls · {api.tokens:,} total tokens reported by the API.')
                for notice in session.notices:
                    st.warning(notice)
            except ForgeError as exc:
                st.error(str(exc))

elif page == 'Forge a guide':
    st.title('Forge a complete study guide.')
    st.markdown('<div class="forge-subtitle">Every PDF page → text + visual inventory → audited explanations → embedded course images.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="system-line">{FORGE_OVERSEER.name} coordinating {SCRIBE_AUTOMATON.name} + {STUDY_AUTOMATON.name} + {REVIEW_AUTOMATON.name}</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric('01 / SCRIBE', 'Read text + images')
    b.metric('02 / STUDY', 'Explain every item')
    c.metric('03 / REVIEW', 'Audit coverage')
    guide_files = st.file_uploader('Upload PDF course material', type=['pdf'],
        accept_multiple_files=True, key='guide-pdfs')
    total_bytes = sum(len(upload.getvalue()) for upload in guide_files)
    if guide_files:
        st.caption(f'{len(guide_files)} PDFs · {total_bytes / 1024 / 1024:.1f} MB combined')
    if total_bytes > 50 * 1024 * 1024:
        st.error('These PDFs exceed 50 MB combined. Split the study guide into volumes.')
    with st.form('generate-guide'):
        guide_title = st.text_input('Study guide name', value='Complete course study guide')
        guide_audience = st.selectbox('Study depth', [
            'First-year college / A&P I', 'Introductory college', 'Advanced high school'])
        expand_guide = st.checkbox('Expand underexplained material with trusted references', value=True)
        st.caption('High-detail visual reading and completeness auditing use multiple API calls. Large PDFs can take several minutes and cost more than a question set.')
        guide_submit = st.form_submit_button('📚 Forge complete study guide', type='primary')
    if guide_submit:
        if not key:
            st.error('Add your OpenAI API key in Settings first.')
        elif not guide_files or total_bytes > 50 * 1024 * 1024:
            st.error('Upload at least one PDF within the combined size limit.')
        else:
            progress_bar = st.progress(0, text=f'{SCRIBE_AUTOMATON.name}: preparing every PDF page…')
            api = API(key, model)
            try:
                guide = generate_study_guide(
                    api, [(upload.name, upload.getvalue()) for upload in guide_files],
                    guide_title, audience=guide_audience, expand=expand_guide,
                    progress=lambda fraction, text: progress_bar.progress(fraction, text=text))
                activate_guide(guide)
                st.success(f'{FORGE_OVERSEER.name} released {len(guide.entries)} audited guide entries. Open Study guide from the Core.')
                st.caption(f'{api.calls} AI calls · {api.tokens:,} total tokens reported by the API.')
                for notice in guide.notices:
                    if notice.startswith('Coverage check passed'):
                        st.success(notice)
                    else:
                        st.warning(notice)
            except (ForgeError, InputError) as exc:
                st.error(str(exc))

elif page == 'Study guide':
    guide = st.session_state.guide
    if not guide:
        st.title('No study guide loaded.')
        st.info('Forge a guide or open a saved guide first.')
    else:
        st.title(guide.title)
        st.markdown(f'<div class="system-line">{STUDY_AUTOMATON.name} + {REVIEW_AUTOMATON.name} / image-aware guide</div>', unsafe_allow_html=True)
        covered = {entry.inventory_id for entry in guide.entries}
        visual_sources = sum(source.modality == 'visual_analysis' for source in guide.sources)
        expanded = sum(bool(entry.expansion) for entry in guide.entries)
        a, b, c, d = st.columns(4)
        a.metric('Audited coverage', f'{len(covered)} / {len(guide.inventory)}')
        b.metric('Guide entries', len(guide.entries))
        c.metric('Visual pages read', visual_sources)
        d.metric('Expanded entries', expanded)
        st.caption('Course material is primary. “Expanded background” is outside explanation from the linked trusted reference. AI visual readings are labeled separately from original PDF text.')
        topics = list(dict.fromkeys(entry.topic for entry in guide.entries))
        selected_topic = st.selectbox('Jump to topic', topics)
        image_index = {image.id: image for image in guide.page_images}
        source_index = {source.id: source for source in guide.sources}
        shown_images = set()
        for entry in [entry for entry in guide.entries if entry.topic == selected_topic]:
            with st.container(border=True):
                st.subheader(entry.title)
                st.write(entry.explanation)
                if entry.key_points:
                    st.write('**Key points**')
                    for item in entry.key_points:
                        st.write('• ' + item)
                if entry.mechanisms:
                    with st.expander('Mechanisms and processes'):
                        for item in entry.mechanisms:
                            st.write('• ' + item)
                if entry.connections:
                    with st.expander('Connections'):
                        for item in entry.connections:
                            st.write('• ' + item)
                if entry.common_confusions:
                    with st.expander('Common confusions'):
                        for item in entry.common_confusions:
                            st.write('• ' + item)
                for visual_id in entry.visual_ids:
                    if visual_id in image_index and visual_id not in shown_images:
                        image = image_index[visual_id]
                        st.image(base64.b64decode(image.jpeg_base64),
                            caption=f'{image.source_name} · PDF page {image.page_number} · {image.caption}',
                            use_container_width=True)
                        shown_images.add(visual_id)
                if entry.expansion:
                    st.info('**Expanded background — outside the uploaded course material**\n\n' + entry.expansion)
                if entry.trusted_references:
                    st.write('**Trusted references**')
                    for reference in entry.trusted_references:
                        st.markdown(f'- [{reference.title}]({reference.url}) — {reference.supports}')
                with st.expander('Course evidence'):
                    for citation in entry.evidence:
                        source = source_index[citation.source_id]
                        label = 'AI visual reading' if source.modality == 'visual_analysis' else 'Course text'
                        st.caption(f'{label} · {source.name} · {source.location}')
                        st.write(citation.quote)
        for notice in guide.notices:
            if notice.startswith('Coverage check passed'):
                st.success(notice)
            else:
                st.warning(notice)
        st.subheader('Export the complete guide')
        st.download_button('Download guide backup (JSON)', guide.model_dump_json(indent=2),
            'hector-study-guide.json', 'application/json')
        left, right = st.columns(2)
        try:
            left.download_button('Download image-rich PDF', guide_pdf_bytes(guide),
                'hector-study-guide.pdf', 'application/pdf', use_container_width=True)
            right.download_button('Download editable Word guide', guide_docx_bytes(guide),
                'hector-study-guide.docx',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                use_container_width=True)
        except Exception:
            st.error('Guide export failed. Download the JSON backup to preserve it.')

elif page == 'Study':
    s = st.session_state.session
    if not s:
        st.title('Ready when you are.')
        st.markdown(f'<div class="system-line">{STUDY_AUTOMATON.name} / awaiting a study set</div>', unsafe_allow_html=True)
        st.info('Forge a set, open a saved set, or try the biology demo from the Core.')
    else:
        st.title(s.title)
        st.markdown(f'<div class="system-line">{STUDY_AUTOMATON.name} + {REVIEW_AUTOMATON.name}</div>', unsafe_allow_html=True)
        stats = score(s.results, s.questions)
        a, b, c, d = st.columns(4)
        a.metric('Resolved score', f"{stats['percent']}%" if stats['percent'] is not None else '—')
        b.metric('Resolved', f"{stats['resolved']} / {len(s.questions)}")
        c.metric('Needs review', stats['pending'])
        d.metric('Unanswered', stats['unanswered'])
        st.caption(f"Score includes only resolved answers; partial credit = ½. {stats['excluded']} excluded. Pending answers are not counted as wrong.")
        only_review = st.checkbox('Practice unresolved / missed questions only')
        pool = [q for q in s.questions if not only_review or q.id not in s.results or s.results[q.id].status in ('needs_review', 'incorrect', 'partial')]
        if not pool:
            st.success('All questions in this set are resolved correctly or excluded. Uncheck the filter to review them.')
        else:
            idx = min(st.session_state.position, len(pool)-1)
            q = pool[idx]
            epoch = st.session_state.epoch
            prefix = f'{s.id}-{q.id}-{epoch}'
            st.progress((idx+1)/len(pool), text=f'Question {idx+1} of {len(pool)} · {q.kind}')
            st.caption(f'{q.topic} / {q.concept} · {q.difficulty} / {q.cognitive_level}')
            st.subheader(q.prompt)
            prior = s.results.get(q.id)
            with st.form(f'answer-{prefix}'):
                if q.options:
                    opts = list(q.options)
                    random.Random(s.id + q.id).shuffle(opts)
                    answer = st.radio('Your answer', opts, index=opts.index(prior.answer) if prior and prior.answer in opts else None, key=f'input-{prefix}')
                else:
                    answer = st.text_area('Your answer', value=prior.answer if prior else '', key=f'input-{prefix}', placeholder='Explain it in your own words. Exact wording is not required.')
                check = st.form_submit_button('Check answer', type='primary')
            if check:
                if not answer or not answer.strip():
                    st.warning('Enter or select an answer first.')
                else:
                    s.results[q.id] = local_grade(q, answer)
                    persist()
                    st.rerun()
            result = s.results.get(q.id)
            if result:
                if result.status == 'correct':
                    st.success('Accepted · ' + result.feedback)
                elif result.status == 'needs_review':
                    st.warning('Needs review · ' + result.feedback)
                else:
                    st.info(f'{result.status.title()} · {result.feedback}')
                st.caption('Saved answer: ' + result.answer)
                if result.status == 'needs_review':
                    if st.button('Check the meaning with AI', key=f'ai-{prefix}', disabled=not bool(key)):
                        with st.spinner(f'{REVIEW_AUTOMATON.name}: comparing meaning and checking the source…'):
                            try:
                                s.results[q.id] = meaning_check(API(key, model), q, result.answer, s.sources)
                                persist()
                                st.rerun()
                            except ForgeError as exc:
                                st.error(str(exc))
                    if not key:
                        st.caption('Add an API key in Settings for meaning-based checks, or self-review below.')
                with st.expander('Answer, explanation & original evidence', expanded=result.status == 'needs_review'):
                    st.write('**Reference answer:** ' + q.answer)
                    st.write(q.explanation)
                    st.write('**Required ideas:**')
                    for item in q.rubric:
                        st.write('• ' + item)
                    if q.alternatives:
                        st.write('**Also accepted:** ' + '; '.join(q.alternatives))
                    source_map = {x.id: x for x in s.sources}
                    for citation in q.citations:
                        src = source_map[citation.source_id]
                        st.caption(f'{src.name} · {src.location}')
                        st.info(citation.quote)
                st.caption('You control the final grade. Exclude a flawed or ambiguous question; it will not affect your score.')
                with st.form(f'resolve-{prefix}'):
                    resolution = st.selectbox('After reviewing the evidence', ['My answer is correct', 'Partially correct (½ credit)', 'I need to learn this (incorrect)', 'Exclude this question'])
                    if st.form_submit_button('Apply my decision'):
                        status = {'My answer is correct':'correct', 'Partially correct (½ credit)':'partial', 'I need to learn this (incorrect)':'incorrect', 'Exclude this question':'excluded'}[resolution]
                        s.results[q.id] = Result(answer=result.answer, status=status,
                            feedback='Resolved by you after review.', method='self-review')
                        persist()
                        st.rerun()
            left, right = st.columns(2)
            if left.button('← Previous', disabled=idx == 0, use_container_width=True):
                st.session_state.position = idx-1
                st.rerun()
            if right.button('Next →', disabled=idx == len(pool)-1, use_container_width=True):
                st.session_state.position = idx+1
                st.rerun()
            jump = st.selectbox('Jump to question', range(len(pool)), index=idx,
                format_func=lambda i: f'{i+1}. {pool[i].concept}', key=f'jump-{prefix}-{only_review}')
            if jump != idx:
                st.session_state.position = jump
                st.rerun()
        with st.expander('Start a fresh attempt'):
            st.caption('Creates a new copy with no answers; this attempt stays saved.')
            if st.button('New attempt'):
                fresh = s.model_copy(deep=True)
                fresh.id = uuid.uuid4().hex
                fresh.results = {}
                from datetime import datetime, timezone
                fresh.created = datetime.now(timezone.utc).isoformat()
                activate(fresh)
                st.rerun()

elif page == 'Rapid fire · experimental':
    s = st.session_state.session
    st.title('Rapid fire')
    st.markdown(f'<div class="system-line">{STUDY_AUTOMATON.name} / experimental endless practice</div>', unsafe_allow_html=True)
    if not s:
        st.info('Load or forge a study set first. Rapid Fire uses its pre-generated questions without making new API calls.')
    else:
        if st.session_state.rapid_session_id != s.id:
            reset_rapid(s.id)
        if not st.session_state.rapid_deck:
            st.session_state.rapid_deck = build_rapid_deck(
                s.questions, s.results, seed=f'{s.id}-{st.session_state.rapid_round}')
        deck = st.session_state.rapid_deck
        index = min(st.session_state.rapid_index, len(deck) - 1)
        question_map = {question.id: question for question in s.questions}
        q = question_map[deck[index]]
        a, b, c = st.columns(3)
        a.metric('Round', st.session_state.rapid_round)
        b.metric('Answered', st.session_state.rapid_attempts)
        c.metric('Accepted', st.session_state.rapid_accepted)
        st.caption('The deck reshuffles forever, placing unresolved and unseen questions first. It uses the active set and makes no generation calls.')
        st.progress((index + 1) / len(deck), text=f'Round {st.session_state.rapid_round} · {index + 1} of {len(deck)} · {q.kind}')
        st.caption(f'{q.topic} / {q.concept} · {q.difficulty} / {q.cognitive_level}')
        st.subheader(q.prompt)
        rapid_key = f'rapid-{s.id}-{st.session_state.rapid_round}-{index}'
        if not st.session_state.rapid_answered:
            with st.form('answer-' + rapid_key):
                if q.options:
                    options = list(q.options)
                    random.Random(rapid_key).shuffle(options)
                    rapid_answer = st.radio('Your answer', options, index=None, key='input-' + rapid_key)
                else:
                    rapid_answer = st.text_area('Your answer', key='input-' + rapid_key,
                        placeholder='Answer from memory. Exact wording is not required.')
                rapid_check = st.form_submit_button('Check & reveal', type='primary')
            if rapid_check:
                if not rapid_answer or not rapid_answer.strip():
                    st.warning('Enter or select an answer first.')
                else:
                    result = local_grade(q, rapid_answer)
                    s.results[q.id] = result
                    st.session_state.rapid_result = result
                    st.session_state.rapid_answered = True
                    st.session_state.rapid_attempts += 1
                    if result.status == 'correct':
                        st.session_state.rapid_accepted += 1
                        st.session_state.rapid_counted = True
                    persist()
                    st.rerun()
        else:
            result = st.session_state.rapid_result
            if result.status == 'correct':
                st.success('Accepted · ' + result.feedback)
            else:
                st.warning('Needs review · This was not marked wrong and does not lower your score.')
            st.write('**Your answer:** ' + result.answer)
            st.write('**Reference answer:** ' + q.answer)
            st.write(q.explanation)
            with st.expander('Required ideas & source evidence'):
                for item in q.rubric:
                    st.write('• ' + item)
                source_map = {source.id: source for source in s.sources}
                for citation in q.citations:
                    source = source_map[citation.source_id]
                    st.caption(f'{source.name} · {source.location}')
                    st.info(citation.quote)
            if result.status == 'needs_review':
                if st.button('Count my answer as correct', use_container_width=True):
                    s.results[q.id] = Result(answer=result.answer, status='correct',
                        feedback='Resolved by you after rapid-fire review.', method='self-review')
                    if not st.session_state.rapid_counted:
                        st.session_state.rapid_accepted += 1
                        st.session_state.rapid_counted = True
                    persist()
                    st.rerun()
            if st.button('Next rapid question →', type='primary', use_container_width=True):
                previous_id = q.id
                st.session_state.rapid_index += 1
                if st.session_state.rapid_index >= len(deck):
                    st.session_state.rapid_round += 1
                    st.session_state.rapid_index = 0
                    st.session_state.rapid_deck = build_rapid_deck(
                        s.questions, s.results,
                        seed=f'{s.id}-{st.session_state.rapid_round}',
                        previous_id=previous_id)
                st.session_state.rapid_answered = False
                st.session_state.rapid_result = None
                st.session_state.rapid_counted = False
                st.rerun()

elif page == 'Coverage & edit':
    s = st.session_state.session
    st.title('See what you’re actually studying.')
    st.markdown(f'<div class="system-line">{REVIEW_AUTOMATON.name} / coverage, evidence and corrections</div>', unsafe_allow_html=True)
    if not s:
        st.info('Load or forge a set first.')
    else:
        coverage = coverage_summary(s)
        a, b, c, d = st.columns(4)
        a.metric('Released', f'{len(s.questions)} / {s.requested}')
        b.metric('Planned coverage', f"{coverage['percent']}%")
        c.metric('Concepts questioned', f"{coverage['questioned']} / {coverage['planned']}")
        d.metric('Mastered', coverage['mastered'])
        st.caption('Planned coverage compares released questions with the source-grounded concept inventory created for this set. It is not a claim that the Forge mapped every fact in your entire course.')
        st.subheader('Coverage by topic')
        st.dataframe(coverage['rows'], hide_index=True, use_container_width=True,
            column_config={'Coverage': st.column_config.ProgressColumn('Coverage', min_value=0, max_value=100, format='%d%%')})
        st.subheader('Coverage by source')
        st.dataframe(coverage['source_rows'], hide_index=True, use_container_width=True)
        st.subheader('Question mix')
        mix = Counter((q.difficulty, q.cognitive_level) for q in s.questions)
        st.dataframe([{'Difficulty': difficulty, 'Cognitive level': level, 'Questions': count}
            for (difficulty, level), count in sorted(mix.items())], hide_index=True, use_container_width=True)
        for notice in s.notices:
            st.warning(notice)
        released = {q.concept for q in s.questions}
        omitted = [o.concept for o in s.planned if o.concept not in released]
        if omitted:
            st.write('**Planned concepts not released:** ' + '; '.join(omitted))
        st.dataframe([{'#':i+1, 'Topic':q.topic, 'Concept':q.concept, 'Type':q.kind,
            'Difficulty':q.difficulty, 'Cognitive level':q.cognitive_level}
            for i,q in enumerate(s.questions)], hide_index=True, use_container_width=True)
        with st.expander('Edit a question or correct its answer key'):
            qi = st.selectbox('Question to edit', range(len(s.questions)), format_func=lambda i: f'{i+1}. {s.questions[i].concept}')
            q = s.questions[qi]
            with st.form(f'edit-{s.id}-{q.id}-{st.session_state.epoch}'):
                prompt = st.text_area('Question wording', q.prompt)
                if q.options:
                    options_text = st.text_area('Options — one per line', '\n'.join(q.options))
                    ans = st.text_input('Correct answer — must exactly match one option', q.answer)
                    alt = ''
                else:
                    options_text = ''
                    ans = st.text_area('Reference answer', q.answer)
                    alt = st.text_area('Other accepted answers — one per line', '\n'.join(q.alternatives))
                rubric = st.text_area('Required ideas — one per line', '\n'.join(q.rubric))
                explanation = st.text_area('Explanation', q.explanation)
                st.caption('Edits retain original evidence and clear the old grade for this question. Your changes are not automatically AI-audited.')
                if st.form_submit_button('Save correction'):
                    changed = q.model_copy(update={'prompt':prompt.strip(), 'answer':ans.strip(),
                        'options':[x.strip() for x in options_text.splitlines() if x.strip()],
                        'alternatives':[x.strip() for x in alt.splitlines() if x.strip()],
                        'rubric':[x.strip() for x in rubric.splitlines() if x.strip()], 'explanation':explanation.strip()})
                    errors = validate_question(changed, s.sources)
                    if errors:
                        st.error(' '.join(errors))
                    else:
                        s.questions[qi] = changed
                        s.results.pop(q.id, None)
                        s.notices.append(f'User edited {q.concept}; retained source evidence. Not re-audited.')
                        st.session_state.epoch += 1
                        persist()
                        st.success('Correction saved. The old grade was cleared.')
        st.subheader('Take your study set with you')
        st.download_button('Download study set + progress (JSON)', s.model_dump_json(indent=2), 'hector-study-set.json', 'application/json')
        include = st.checkbox('Include a separate answer key', value=True)
        a, b = st.columns(2)
        try:
            a.download_button('Download printable PDF', pdf_bytes(s, include), 'hector-study-set.pdf', 'application/pdf')
            b.download_button('Download editable Word file', docx_bytes(s, include), 'hector-study-set.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        except Exception:
            st.error('Document export failed. Download JSON to preserve the set.')

elif page == 'Saved sets':
    st.title('Pick up where you left off.')
    st.markdown(f'<div class="system-line">{ARCHIVIST_AUTOMATON.name} / saved attempts and portable backups</div>', unsafe_allow_html=True)
    st.caption('Study sets and submitted answers stay on this computer. JSON backups include your source text; keep them private if your notes are private.')
    imported = st.file_uploader('Restore a study set backup', type=['json'])
    if imported and st.button('Open imported set'):
        try:
            session = load_bytes(imported.getvalue())
            # Imported copies cannot silently replace a saved attempt.
            session.id = uuid.uuid4().hex
            activate(session)
            st.success('Restored as a new copy. Open Study from the Core.')
        except Exception:
            st.error('This is not a valid v0.1/v0.2/v0.3/v0.4 Study Lab backup, or its source references are invalid.')
    saved = []
    if DATA.exists():
        for p in sorted(DATA.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                saved.append(load_bytes(p.read_bytes()))
            except Exception:
                st.warning(f'Could not load saved file {p.name}. It has not been changed.')
    if not saved:
        st.info('Your first study set will appear here automatically.')
    for session in saved:
        with st.container(border=True):
            st.write('**' + session.title + '**')
            st.caption(f'{len(session.questions)} questions · {len(session.results)} submitted answers · {session.created[:16]} UTC')
            if st.button('Open set', key=f'open-{session.id}'):
                activate(session)
                st.success('Loaded. Return to Core and open Study.')

elif page == 'Saved guides':
    st.title('Your complete study guides.')
    st.markdown(f'<div class="system-line">{ARCHIVIST_AUTOMATON.name} / image-aware guide archive</div>', unsafe_allow_html=True)
    st.caption('Guides, embedded course-page images, source evidence and trusted links stay on this computer.')
    imported_guide = st.file_uploader('Restore a study-guide backup', type=['json'], key='restore-guide')
    if imported_guide and st.button('Open imported guide'):
        try:
            guide = load_guide_bytes(imported_guide.getvalue())
            guide.id = uuid.uuid4().hex
            activate_guide(guide)
            st.success('Restored as a new copy. Open Study guide.')
        except Exception:
            st.error('This is not a valid v0.4 Study Lab guide backup.')
    saved_guides = []
    if GUIDE_DATA.exists():
        for path in sorted(GUIDE_DATA.glob('*.guide.json'),
                           key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                saved_guides.append(load_guide_bytes(path.read_bytes()))
            except Exception:
                st.warning(f'Could not load saved guide {path.name}. It has not been changed.')
    if not saved_guides:
        st.info('Your first generated guide will appear here automatically.')
    for guide in saved_guides:
        with st.container(border=True):
            st.write('**' + guide.title + '**')
            st.caption(f'{len(guide.entries)} entries · {len(guide.page_images)} embedded pages · {guide.created[:16]} UTC')
            if st.button('Open guide', key=f'open-guide-{guide.id}'):
                activate_guide(guide)
                st.success('Loaded. Open Study guide from the Core.')
