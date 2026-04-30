# Plan 4: Google Workspace Setup — Spec + Implementation Plan

**Date:** 2026-04-30
**Approach (locked):** Lightweight — reuse Plan 3 OOXML templates (Google opens natively), add Gmail signature, write setup guide.
**Predecessors:** Plan 1 (v0.1.0), Plan 2 (v0.2.0), Plan 3 (v0.3.0)
**Mandate from user:** "do not ask follow-up questions. Make the best practice choices."

---

## Spec

### Goal
Make the Deccan design system work in Google Workspace for an end-user with no admin access.

### Deliverables
1. `gworkspace/gmail-signature.htm` — Gmail-optimized HTML signature, **under 10 KB** (Gmail's signature size limit)
2. `gworkspace/README.md` — setup guide covering OOXML upload + conversion + signature install
3. `scripts/lib/gmail_signature.py` — generator that downsamples the logo to fit Gmail's size budget
4. `scripts/_10_emit_gworkspace.py` — orchestrator (calls the gmail_signature emitter)
5. `tests/test_gworkspace.py` — validates signature is under 10 KB and contains brand markers

### Out of scope
- Native Google Slides/Docs/Sheets API generation (deferred)
- Org-wide template gallery (requires admin)
- Calendar / Sites / Apps Script

### Best-practice choices made internally (no further questions)
- Logo downsampled to **120×40** (visually identical at signature size; ~3-4 KB base64 vs ~13 KB at full res)
- PNG kept (not JPG) — preserves transparency for the leaf icon
- Same HTML structure as Outlook signature, dimensions adjusted
- Signature uses inline styles only (Gmail strips `<style>` blocks)
- README documents both upload-and-convert (Slides/Docs/Sheets) and copy-paste (Gmail signature) flows

---

## Implementation Plan

### Task 1: Implement gmail_signature emitter + orchestrator + signature output

Files:
- Create: `scripts/lib/gmail_signature.py`
- Create: `scripts/_10_emit_gworkspace.py`
- Create: `gworkspace/gmail-signature.htm` (generated)

Steps:
1. Implement `gmail_signature.py` — reads `data/logo.png`, downsamples to 120×40 with Pillow, base64-encodes, builds HTML signature with inline styles (mirroring Plan 3's structure with smaller dimensions).
2. Implement `_10_emit_gworkspace.py` orchestrator that calls it.
3. Run; verify output exists and is < 10 KB.
4. Commit.

### Task 2: Tests

File:
- Create: `tests/test_gworkspace.py`

Asserts:
- Signature exists
- Size < 10 KB (Gmail limit, with safety margin)
- Contains `data:image/png;base64,`
- Contains `#164999` (Deccan Blue)
- Contains `IBM Plex Sans` reference
- Contains `deccanchemicals.com`

Run pytest, verify pass, commit.

### Task 3: Setup guide

File:
- Create: `gworkspace/README.md`

Content sections:
1. What's in this folder
2. Step-by-step Slides/Docs/Sheets upload + convert procedure
3. Step-by-step Gmail signature install
4. Known fidelity caveats per app (Slides good, Docs good, Sheets some loss)
5. Pointer to Plan 3 office/ folder for the source OOXML templates
6. When to consider Plan 4-followup (native API generation)

Commit.

### Task 4: Update top-level README + tag v0.4.0

- Add Plan 4 complete section
- Update Roadmap (mark Plan 4 done)
- Annotated tag v0.4.0
- Push tags

---

## Self-Review

Spec coverage: all 5 deliverables map to tasks. Tests cover the size constraint (the one real risk). Best-practice choices flagged so the implementer doesn't re-raise them.

No placeholders. Type consistency: `emit_gmail_signature()` returns `Path`, called from orchestrator. Tests reference exact path `gworkspace/gmail-signature.htm`.

Scope: tight (~1 day). Single subsystem. One plan, no decomposition needed.
