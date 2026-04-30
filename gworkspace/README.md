# Google Workspace — Setup Guide

This folder makes the Deccan design system work in Google Workspace for an end-user with no admin access.

## What's here

- `gmail-signature.htm` — Gmail-optimized HTML email signature (under Gmail's 10 KB size limit)

The Slides / Docs / Sheets templates are reused from `office/templates/` — Google Workspace opens OOXML files natively and converts them to native Google formats, so we don't generate separate Slides/Docs/Sheets files.

## Slides / Docs / Sheets — upload and convert

1. Open https://drive.google.com
2. Upload these from the `office/templates/` folder at the project root:
   - `deccan.dotx` (Word template — opens as Google Docs)
   - `deccan.potx` (PowerPoint template — opens as Google Slides)
   - `deccan.xltx` (Excel template — opens as Google Sheets)
3. After each upload, right-click the file in Drive and choose **Open with → Google Docs / Slides / Sheets**
4. Google converts OOXML to its native format. The converted version is saved alongside the original — keep the converted version (delete the .dotx/.potx/.xltx originals if you don't want them cluttering Drive).
5. Star or move the converted versions into a folder you'll remember (e.g., `Drive / Templates / Deccan`).
6. To use one as a starting point: open it → **File → Make a copy** → work in the copy.

### Known fidelity caveats

- **Google Slides** (from `.potx`): generally good. Theme colors and IBM Plex Sans typography carry over. Custom layouts may simplify slightly.
- **Google Docs** (from `.dotx`): good for body styles and headings. The cover page may reflow when converted; the footer text may need to be re-applied via Insert → Headers & footers.
- **Google Sheets** (from `.xlsx`): banded data row fills carry over. Some cell formatting may simplify; merged cells and named ranges generally work.

If a specific template has unacceptable conversion loss for your use case, request **Plan 4-followup** to natively generate Google files via the Google Slides/Docs/Sheets APIs (more setup but higher fidelity).

## Gmail signature

1. Open `gmail-signature.htm` in a browser (double-click the file).
2. The browser displays the rendered signature.
3. Select all (Ctrl+A), copy (Ctrl+C).
4. In Gmail, click the **Settings** gear → **See all settings** → **General** tab.
5. Scroll to the **Signature** section, click **Create new**, name it "Deccan".
6. Click in the signature editor and paste (Ctrl+V).
7. In the **Signature defaults** dropdowns, set "Deccan" for both "FOR NEW EMAILS USE" and "ON REPLY/FORWARD USE".
8. Click **Save Changes** at the bottom of the page.
9. Compose a new email — the signature should appear with the Deccan logo and brand colors.
10. **Replace the placeholder fields** (`[Your Name]`, `[Your Role]`, `[Department]`, phone, email) with your actual details.

## Regenerating

If the Plan 1 palette or logo changes, re-run:

```powershell
python scripts\_10_emit_gworkspace.py
```

This regenerates `gmail-signature.htm` with the current palette + logo.
