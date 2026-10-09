# Hector Study Lab v0.4 — Core Chamber experimental design

A local study app that turns teaching material into varied questions and image-aware study guides.
Built for Hector. Quality comes before filling a question quota.

This package contains the experimental Study Lab visual shell: a dark industrial
Core Chamber with six connected workspaces, rotating reactor rings, cyan-and-amber
circuitry, truthful system-state readouts, responsive control panels, and the complete v0.4 learning engine underneath. It is a
visual evolution of Study Forge—not a loss of any existing feature or saved-data compatibility.

## Start on Windows

1. Extract the whole ZIP into a normal folder (for example, Documents\HectorStudyForge). Do not run it inside the ZIP.
2. Double-click **Start_Hector_Study_Lab.bat**. The first launch installs the required packages in a private environment. An internet connection is needed for installation. The older Study Forge launcher remains as a compatibility shortcut.
3. Your browser opens the app. Keep the launcher window open while studying.
4. Click **Try the biology demo** on the Core Chamber to try it without an API key.
5. Open **System settings** and paste your existing OpenAI API key. Do not send your key to anyone or put it into your notes. The key stays in this running browser session; it is not included in exports.
6. Enter **Create Questions** from the Core Chamber, upload your slides/notes, check the extracted-text preview, choose your topics and question types, and click **Forge my study set**.
7. For a complete image-aware guide, enter **Create Study Guide**, upload PDF material, choose the depth and whether trusted expansion is allowed, then generate it. Guide mode can take several minutes on large files.

Python 3.11 or newer is required; Python 3.12 was used for testing. If Windows says `py` is not recognized, install Python from https://www.python.org/downloads/windows/ with the Python launcher enabled. If Python is already installed but the launcher is unavailable, run these commands inside the extracted folder:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

On macOS/Linux, run `sh start.sh` in the extracted folder. You may need your OS's Python venv package.
If the browser does not open automatically, use the local URL displayed in the launcher.
Close the launcher or press Ctrl+C to stop the app.

## Reuse your existing key automatically

If `OPENAI_API_KEY` is already set on your computer, the app uses it. Otherwise, for a persistent local setup, copy `.env.example` to `.env` and fill it in:

```text
OPENAI_API_KEY=your_existing_key_here
OPENAI_MODEL=gpt-5.4
```

The default model is `gpt-5.4`; change it in Settings or `.env` if your API account uses another Responses API model with structured outputs, PDF vision and web-search support. Your key is reusable; it does not need to be a new key just for this app. Account access and billing still apply. Do not share `.env` or a folder containing it.

## What v0.4 includes

### Core systems

- **Forge Overseer** coordinates the complete pipeline and releases only sets that pass the existing safeguards.
- **Scribe Automaton** reads selected text sources for question sets and performs high-detail text-plus-image inspection of every PDF page in guide mode.
- **Exam Automaton** plans distinct concepts and builds source-grounded questions without repeat-padding.
- **Study Automaton** runs resumable practice sessions with stable choice shuffling.
- **Review Automaton** audits questions, protects equivalent answers and keeps uncertain judgments out of the score until you resolve them.
- **Archivist Automaton** autosaves attempts and handles restore, JSON, PDF and Word exports.

Study-set JSON remains compatible with v0.1, v0.2 and v0.3 backups.

### Image-aware study guides

- Multiple PDF uploads with every page sent through high-detail visual inspection in bounded batches.
- Reads diagrams, labels, arrows, micrographs, photographs, tables, charts, color keys, equations and spatial relationships while reporting low-confidence or missing page analyses.
- Builds an atomic inventory covering definitions, terms, structures, functions, mechanisms, steps, comparisons, exceptions, values, warnings, labels and visual relationships.
- Writes one source-validated guide entry for every inventory item, then independently audits accuracy, completeness and scientific qualifiers.
- Runs a second repair pass for rejected entries. Any remaining inventory gap is named explicitly in the app and exports; it is never silently hidden.
- Embeds up to 48 pedagogically useful original PDF pages in the guide, preserving the real course image beside its explanation. Additional useful visuals remain described and produce a visible limit notice.
- Optional expansion of underexplained material through web search restricted to OpenStax, NIH/NCBI, NHGRI, MedlinePlus and CDC. External explanation is labeled **Expanded background** and linked to its supporting source.
- Course wording and course-specific values override generic external references.
- Image-aware guide viewer with topic navigation, course evidence, visual-analysis labels, trusted links and coverage metrics.
- Separate local guide archive plus portable JSON, image-rich PDF and editable Word exports.

### Question sets and practice

- Multiple PDF, PPTX, DOCX, TXT and Markdown uploads, plus pasted notes.
- Choose which uploaded files to include and prioritize study outlines.
- Optional focus on a chapter, unit or topic; 5–100 questions, default 25.
- Independent difficulty controls: foundational, standard, challenging or mixed.
- Cognitive-level controls: recall, understanding, application and analysis, in any selected combination.
- Multiple choice, short answer, true/false and written scenarios.
- Concept-first coverage planning with reserve concepts, structural checks, exact source-quote verification, and an independent AI audit of ambiguity, answer keys and repeated concepts.
- Valid questions survive partial batch failures; only failed assignments are regenerated.
- Safe normalization maps answers such as `B`, `option C`, or `A. answer text` back to the existing multiple-choice option.
- Objective questions no longer fail for omitting a written-answer rubric; v0.2 derives a simple rubric from the selected option.
- True/false assignments alternate their requested truth value and require false statements to be corrected from the supplied source.
- True/false prompts rotate through direct facts, comparisons, cause/effect and condition/application styles when the material supports them.
- Audit failures receive targeted rewrites and a second independent audit before being omitted.
- Stable shuffled choice order: grading uses the selected answer text, never its on-screen position.
- Explanations, minimum required ideas and original source excerpts.
- Review protection, optional AI meaning checks, self-review, partial credit and question exclusion.
- Persistent local Question Memory compares new runs with earlier questions from matching source sections. It asks for different supported facts or angles and can be cleared in Settings.
- Planned-concept, topic and source-section coverage tracking, plus study mastery, question difficulty and cognitive-level reports.
- Experimental Rapid Fire mode reshuffles the active pre-generated set forever, prioritizes unresolved and unseen questions, and makes no generation API calls.
- Editable wording/answer keys and fresh attempts.
- Automatic local saving of sets and submitted answers; resume from Saved sets.
- Portable JSON backups, printable PDFs and editable Word files. Answer keys are optional and appear separately.
- An eight-question hand-authored biology demo that works without an API key. It is demonstration content, not material extracted from your course slides.

## How grading protects valid answers

There is deliberately no automatic failing grade:

1. A recognized accepted answer is marked correct locally. Minor natural-language case and punctuation differences are tolerated conservatively. Numbers, signs and case-sensitive scientific units are protected.
2. Other answers are **Needs review**, not wrong. They do not count in the score denominator.
3. **Check the meaning with AI** compares your answer against the question and source material. It is instructed to accept equivalent wording, concise correct answers, synonyms and minor typos. It can accept an answer; it cannot assign an automatic failing grade.
4. Review the original evidence and apply your own decision: correct, partial (half credit), incorrect, or exclude the question.
5. Correct a flawed question in Coverage & edit. Editing clears its old grade. Source evidence remains visible, and the set records that the edit was not re-audited.

AI can still produce a flawed question, answer key or feedback. An independent audit reduces that risk; it cannot eliminate it. This design prevents an uncertain AI judgment from automatically counting your answer wrong. It also means you must self-review some genuinely incorrect answers. The resolved score always displays the resolved count beside it; 100% on 2 resolved questions does not mean 100% mastery of a 25-question set.

## Coverage and limits

- The app plans distinct concepts before writing questions. It checks exact/near duplicates and uses a separate semantic audit across the complete set.
- Planned coverage is the percentage of the Forge's source-grounded concept inventory represented by released questions. It is not a claim that every fact in an entire course has been discovered.
- It may still return fewer than requested when the material genuinely lacks enough distinct supported concepts or a question remains unsafe after targeted repairs. It reports the remaining gap instead of padding the set with paraphrases.
- A file's source-section count measures sections cited, not percentage of chapter mastery. Uncited material may still be important. The entire course is not guaranteed to be covered in one set.
- **Question-set mode remains text-first.** Its PDF/PPTX/DOCX question generation does not interpret embedded images. Use Forge a guide when images, scans or diagrams matter.
- **Guide mode is image-aware for PDFs.** It can inspect scanned pages and diagrams, but vision models can still misread tiny labels, subtle colors, overlapping arrows, pathology images or ambiguous structures. Low-confidence readings and missing pages are reported, and original selected pages remain visible for your verification.
- “Complete” means every item found by the page-by-page inventory has an audited entry or a named coverage gap. It cannot honestly guarantee that an AI detected every possible implication in every image.
- Supported PowerPoint format is `.pptx`; convert legacy `.ppt` first. DOCX headers, footers and text boxes, PowerPoint speaker notes and diagram labels stored as images are not extracted.
- Maximum 25 MB per file and 180,000 extracted characters across a selected set. There is no silent truncation: split large material into chapters.
- Guide mode accepts up to 50 MB combined PDF data and the same 180,000-character text ceiling per volume. Split very large courses into volumes.
- Source references use PDF file page numbers, which may differ from printed page numbers. Long text sections use part numbers.
- Source quotation presence is checked automatically; whether the quote fully supports an answer is also evaluated by the AI audit, which can make mistakes.

## Saving and privacy

The app runs on your own computer and binds to `127.0.0.1`. It is intended for personal local use, not public hosting. Uploaded files are read locally. Generation and meaning checks send the selected readable material and relevant answers to the OpenAI API, with response storage disabled in the request. That flag does not promise zero provider retention; your API account's applicable data policies still apply.

Study sets autosave under `data/` beside the app, including extracted source text and submitted answers. Image-aware guides autosave under `data/guides/` and include selected compressed PDF-page images, evidence and trusted links. Question Memory stays locally under `data/_memory/`; it stores released questions and source-section identifiers, not your API key. Clear it in Settings without deleting saved sets. JSON backups never include the API key. Imported backups get a new ID so they do not silently replace an existing item.

If an autosave error appears, download the JSON backup before closing. To move computers, download the JSON and use Saved sets → Restore. To back up everything, copy the `data` folder. Keep backups private if your notes are private.

## AI requests and usage

The demo, local extraction, exact-answer checks, self-review, saving and exports need no API calls. Question generation uses one planning request, five-question drafting batches, bounded audits and targeted repairs. Guide generation is substantially heavier: approximately one vision request per 12 PDF pages, one inventory request per 10 extracted/visual sections, one writing request per six inventory items, plus audit and repair calls. Trusted expansions can also incur web-search tool charges. Do not repeatedly click Generate to troubleshoot billing limits.

The app shows token usage after successful generation. API costs depend on the chosen model and amount of source material. It does not display an estimated dollar amount because it does not fetch live pricing.

## Troubleshooting

- **API key rejected:** confirm your existing key in Settings or `.env`.
- **Rate or billing limit:** check your OpenAI API account and try later.
- **Model unavailable:** enter a model ID your account can access that supports the Responses API and structured outputs. Guide mode also requires PDF vision; trusted expansion requires web search.
- **No readable text:** export a text-bearing PDF or PPTX, use OCR elsewhere, or paste notes.
- **Fewer questions than requested:** read the notices for formatting or audit failures. v0.4 automatically retries them; a remaining gap means some concepts still could not be released safely or Question Memory has exhausted the distinct supported material found so far.
- **Guide coverage below 100%:** the named inventory items failed validation or audit after repair. Review the coverage-gap list; the app will not fill it with unsupported writing.
- **Trusted expansion unavailable:** the guide continues with course-only material for that batch and records a notice.
- **First install failed:** check internet access and launch again. The installer retries when it has not completed.
- **Port already in use:** close an older app window/process or run Streamlit with `--server.port 8502`.
- **Can't download a PDF:** use Word or JSON. Very unusual fonts/scripts may not render in the locally available PDF font.

## Verification and honest release status

**67 automated tests passed** on Python 3.12. New v0.4 tests exercise high-detail PDF file input, filtered web-search requests, page batching, visual observation, page-image rendering, exhaustive guide inventory, entry validation/audit, guide saving/reloading, image-rich PDF and Word exports, trusted-domain enforcement, explicit v0.3 backup compatibility, the new Streamlit guide workspaces, and all Core Chamber routes, archive switching, settings retention, and answer/position retention through Return to Core navigation. All earlier question, grading, memory, coverage, Rapid Fire, extraction, export and compatibility tests still pass. See TEST_REPORT.md.

**Live OpenAI generation, visual reading and web search were not tested in the build environment because no user API key was available.** The real SDK request shape for high-detail PDF input and structured parsing was tested through mock HTTP transport. The complete visual-analysis → inventory → guide → audit → save/export pipeline was tested with a generated two-page PDF and controlled fixtures. Model access, billing, live vision quality and hosted web-search availability must still be checked with your key on your computer. The Windows launcher was inspected but could not be executed in Linux.

For development:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Official API references used for implementation:
- https://developers.openai.com/api/docs/guides/structured-outputs
- https://developers.openai.com/api/docs/guides/file-inputs
- https://developers.openai.com/api/docs/guides/images-vision
- https://developers.openai.com/api/docs/guides/tools-web-search
- https://developers.openai.com/api/docs/models/gpt-5.4
