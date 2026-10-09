# Core Chamber design revision — 2026-10-09

- New default Core Chamber with six functional module entrances.
- Animated multi-ring core, cyan/amber circuits, dimensional module panels.
- Return to Core navigation preserves study data, answers and position.
- Direct archive switching and active guide access.
- Responsive layout and reduced-motion support.
- API readout reports key configuration without claiming a verified connection.
- Existing v0.4 learning engine and data formats preserved.
- 67 automated tests passed; browser visual QA and live API requests unverified.

# Hector Study Lab changelog

## Experimental machine interface — 2026-10-09

- Renamed the visible product shell from Hector Study Forge to Hector Study Lab while preserving all six core system names and v0.4 data compatibility.
- Added an animated but restrained operator-console interface inspired by holographic engineering workstations and industrial control rooms.
- Added truthful live indicators for the local core, API-key link and archive state; none of the telemetry is fabricated activity.
- Added responsive machine-sector headers, control-panel navigation, illuminated progress rails, denser metrics and active-session modules.
- Isolated the entire theme in `forge/ui.py`, leaving generation, grading, storage and guide logic unchanged.
- Added reduced-motion support and a new Study Lab Windows launcher while retaining the old launcher as a compatibility shortcut.
- Expanded the regression suite to 65 passing tests, including an explicit check that the new shell preserves every workspace control.

## v0.4.0 — 2026-10-08

- Added image-aware PDF study-guide generation without changing the six core system names.
- Inspects every PDF page in high-detail visual batches and reports missing or low-confidence readings.
- Builds an atomic completeness inventory across extracted text and visual observations.
- Produces one detailed, evidence-backed guide entry per inventory item and independently audits each entry.
- Repairs audit failures once and names every remaining coverage gap rather than hiding omissions.
- Embeds up to 48 useful original PDF pages in the viewer and guide exports.
- Adds optional trusted expansion restricted to OpenStax, NIH/NCBI, NHGRI, MedlinePlus and CDC; outside material is labeled and linked.
- Adds image-aware guide viewing, local guide archives, JSON backups, image-rich PDF export and editable Word export.
- Preserves v0.1–v0.3 question-set compatibility and all v0.3 question/practice systems.
- Expanded the regression suite from 58 to 63 passing tests.

## v0.3.0 — 2026-10-05

- Added persistent, local, source-matched Question Memory to reduce repeats across separate generations.
- Added separate foundational/standard/challenging difficulty and recall/understanding/application/analysis controls.
- Stores the assigned difficulty and cognitive level on every new question; older backups receive safe defaults.
- Added planned-concept, per-topic, source-section and mastery coverage tracking with explicitly limited claims.
- Added experimental API-free Rapid Fire mode with endless reshuffled rounds and weak/unseen priority.
- Kept review protection active in Rapid Fire: unfamiliar answers remain unscored until the user resolves them.
- Added multiple true/false statement styles alongside the existing balanced truth targets.
- Added a Settings control to inspect or clear Question Memory without deleting saved study sets.
- Preserves v0.1 and v0.2 JSON backup compatibility.
- Expanded the regression suite from 51 to 58 passing tests.

## v0.2.0 — 2026-10-05

- Increased the supported set size from 50 to 100 questions.
- Plans reserve concepts so a few unusable drafts do not collapse the released set.
- Retains valid questions from every draft attempt and retries only failed assignments.
- Repairs common multiple-choice formatting such as `B`, `option C`, numbered keys, and labeled answer text.
- Fixes the v0.1 validator mismatch that rejected objective questions for omitting an unused written-answer rubric.
- Balances true/false assignments and validates the requested truth value, including source-grounded corrections for false statements.
- Splits large audits into bounded batches while checking them against earlier approved questions.
- Rewrites audit failures using the audit reason, then independently audits the replacement.
- Reports the released count for each selected question type.
- Preserves v0.1 JSON backup compatibility.
- Expanded the regression suite from 40 to 51 passing tests.
