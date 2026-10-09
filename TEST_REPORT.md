# Core Chamber design verification — 2026-10-09

67 automated tests passed on Python 3.12.

Verified every Core entrance, archive switching, home navigation, settings retention,
study-position retention, answer persistence, resumed study, corrections, exports,
Rapid Fire and guide workspaces. Earlier engine, grading, source, guide, memory,
coverage and compatibility checks passed. Mock SDK checks ran with environment
proxy variables omitted because the environment SOCKS dependency is unavailable.
No production proxy configuration or API behavior was changed.

Browser visual QA, Windows execution and live OpenAI calls were not performed.

# Hector Study Lab v0.4 — verification

Date: 2026-10-08
Environment: Linux, Python 3.12; dependency versions pinned in requirements.txt.
Command: `python -m pytest -q`
Result: **65 passed**.

## Checks performed

- Correct short answers and explicitly accepted alternate wording pass.
- Unrecognized valid paraphrases, typos, contradictory answers and instruction-like student input stay unscored pending review.
- AI incorrect/partial/uncertain judgments cannot create an automatic failing grade.
- Low-confidence AI acceptance stays pending.
- Scientific case, units, exponents, signs and factorial punctuation are not fuzzily collapsed.
- Thirty shuffled option arrangements still grade by answer text.
- Blank answers cannot be submitted; pending/excluded answers do not lower the score.
- Fabricated source quotes, missing references, invalid answer keys and duplicate options fail validation.
- Duplicate concepts are rejected locally; audit rejections and missing audit records remove questions without padding.
- Valid questions from a partially failed batch survive while only the failed assignments are retried.
- Multiple-choice keys returned as letters, numbers, labeled choices, or equivalent option text are mapped to the exact existing option.
- Objective questions with an empty written-answer rubric receive a safe derived rubric instead of being discarded.
- True/false generation alternates truth targets and validates false statements against source-supported corrections.
- True/false assignments rotate four requested statement styles.
- Difficulty and cognitive-level targets rotate independently and are retained on released questions.
- Local Question Memory persists without duplicates, returns questions only for matching source sections, assigns collision-free memory IDs, and can be cleared independently of saved sets.
- Generation passes matching Question Memory into planning, drafting and auditing while retaining the selected difficulty and cognitive targets.
- Coverage reporting distinguishes planned concepts, questioned concepts, mastery, topic coverage and source-section use.
- Rapid Fire produces complete no-duplicate rounds, prioritizes unresolved material and avoids an immediate repeat across round boundaries.
- A first-pass audit failure receives a targeted rewrite and a second independent audit.
- Mixed generation preserves multiple choice, short answer, true/false and scenario questions in the requested rotation.
- v0.1, v0.2 and v0.3 JSON backups remain loadable in v0.4; missing newer question metadata receives safe defaults.
- The Streamlit interface exposes the full 5–100 question range, new controls, coverage dashboard and a tested Rapid Fire answer/advance flow.
- Full generation pipeline exercised with controlled planner, draft and audit fixtures.
- Real OpenAI SDK structured-output request and parsing exercised through mocked HTTP responses.
- API authentication errors produce a useful message without exposing raw server error content.
- PDF, PPTX, DOCX and text extraction exercised with generated fixtures, including an empty PDF page warning.
- PDF and DOCX exports reopened and checked for questions, answer keys and source references.
- JSON save/reload preserves progress; malformed imports, missing citations and path traversal IDs are rejected.
- Streamlit app tests exercise demo → answer → navigate → review → exclude → edit → save/reopen → new attempt, and rendering of exports.
- API key and model settings persist across page navigation.
- The canonical core-system registry contains the six approved names in a stable order with unique internal keys.
- A generated two-page PDF is split into correct page batches, analyzed through the visual schema, and rendered into a compressed guide image.
- The complete controlled guide pipeline builds an atomic inventory, drafts a source-quoted entry, independently audits it, verifies 100% inventory coverage and survives JSON save/reload.
- Image-rich guide PDF and Word exports reopen successfully and contain the expected explanation and evidence.
- High-detail PDF API requests use a base64 `input_file` with `detail=high` and parse structured visual output through the real SDK using mock HTTP transport.
- Required web-search requests preserve the trusted-domain filter while using structured guide output.
- Guide validation rejects external expansion from untrusted lookalike or unrelated domains.
- The Streamlit UI exposes Forge a guide, Saved guides and the image-aware Study guide viewer while preserving the existing question flow.
- The experimental machine shell renders through every tested workspace without changing existing widget labels or interaction paths.

## Not verified live

- Real API model generation, semantic judgment quality, account access or billing. No user API key was available here.
- Windows launcher execution (the build environment is Linux).
- Live image/diagram interpretation and hosted trusted web search. Their request shapes and downstream behavior are tested with controlled fixtures, but no user API key was available.
- Universal completeness or factual perfection. The app verifies coverage of its generated inventory, reports page-analysis failures and retains original selected images, but a vision/model error can still miss or misread source content.

Tests validate application behavior, not the universal factual correctness of AI-generated content. Review protection remains enabled in all sessions.
