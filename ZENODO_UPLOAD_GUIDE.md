# Zenodo Uploader — User Guide

**Script:** `zenodo_upload.py`  
**Purpose:** Upload Imscribing Grammar publications to Zenodo (sandbox or production) with interactive metadata collection, draft support, and deposit management.

---

## Quick Start

```bash
# 1. Set API tokens (one-time setup)
export ZENODO_SANDBOX_TOKEN="your-sandbox-token"
export ZENODO_TOKEN="your-production-token"

# 2. Test on sandbox (safe — no real DOIs)
python3 zenodo_upload.py paper.pdf

# 3. When ready, publish for real
python3 zenodo_upload.py --live paper.pdf

# 4. List existing deposits
python3 zenodo_upload.py --list
```

---

## Table of Contents

1. [Prerequisites & Token Setup](#prerequisites--token-setup)
2. [Modes: Sandbox vs Production](#modes-sandbox-vs-production)
3. [Commands](#commands)
   - [Upload Files (New Deposit)](#upload-files-new-deposit)
   - [Update an Existing Deposit](#update-an-existing-deposit)
   - [List Deposits](#list-deposits)
   - [Save as Draft](#save-as-draft)
4. [Interactive Metadata Walkthrough](#interactive-metadata-walkthrough)
5. [All Command-Line Options](#all-command-line-options)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)
8. [Configuration Reference](#configuration-reference)

---

## Prerequisites & Token Setup

### Requirements

- **Python 3.8+**
- **`requests` library** — install it with:
  ```bash
  uv pip install requests
  ```
  (If you see `ImportError: requests not installed`, that's the fix.)

### Get Your API Tokens

You need a **personal access token** for each Zenodo environment. Tokens are scoped per-user and must include `deposit:write` and `deposit:actions`.

1. **Sandbox** (for testing):  
   Visit [sandbox.zenodo.org/account/settings/applications](https://sandbox.zenodo.org/account/settings/applications)  
   → *Personal access tokens* → *Generate new token* → select scopes `deposit:write` and `deposit:actions`.

2. **Production** (for real publications):  
   Visit [zenodo.org/account/settings/applications](https://zenodo.org/account/settings/applications)  
   → *Personal access tokens* → *Generate new token* → same scopes.
### Set the Environment Variables

```bash
# For sandbox testing:
export ZENODO_SANDBOX_TOKEN="eyJhbGciOiJIUzI1NiIs..."   # your sandbox token

# For production:
export ZENODO_TOKEN="eyJhbGciOiJIUzI1NiIs..."            # your live token
```

Add these to your `~/.bashrc`, `~/.zshrc`, or `.env` file so you don't need to type them every time. If a token env var is not set, the script will prompt you to paste it interactively.

> **⚠️ Security:** Treat these tokens like passwords. Anyone with your token can create, modify, and publish deposits under your account. Never commit them to version control.

---

## Modes: Sandbox vs Production

|              | Sandbox (`default`)                 | Production (`--live`)              |
| ------------ | ----------------------------------- | ---------------------------------- |
| **Domain**   | sandbox.zenodo.org                  | zenodo.org                         |
| **Token env** | `ZENODO_SANDBOX_TOKEN`            | `ZENODO_TOKEN`                     |
| **DOIs**     | Fake (cannot be resolved)           | Real, citable DOIs                 |
| **Purpose**  | Testing, drafts, previews           | Final publication                  |
| **Safety**   | Safe to experiment                  | Real publication — use with care   |

When you run without `--live`, everything goes to the sandbox. The script prints clear warnings before any production action.

---

## Commands

### Upload Files (New Deposit)

**Basic usage:**

```bash
python3 zenodo_upload.py <file1> [file2 ...]
```

This will:
1. Check each file exists
2. Prompt for your Zenodo token (if not set via env var)
3. Run an interactive metadata collection session
4. Show a summary for confirmation
5. Create a new deposit, upload the files, save metadata, and publish

**Example:**
```bash
python3 zenodo_upload.py manuscripts/AS_ABOVE.pdf
```

This uploads `AS_ABOVE.pdf` to the **sandbox** with interactively collected metadata, then publishes it (fake DOI).

### Update an Existing Deposit

```bash
python3 zenodo_upload.py --update <DEPOSIT_ID> <file1> [file2 ...]
```

- Fetches the existing deposit by its numeric ID
- Uploads the specified files to the same bucket
- Prompts for metadata (overwrites the existing metadata)
- Does **not** change the deposit state by default
- Combine with `--draft` or publish normally

**Find a deposit's ID:**
```bash
python3 zenodo_upload.py --list
python3 zenodo_upload.py --list --live
```

The ID is the first column in the listing output.
### List Deposits

```bash
python3 zenodo_upload.py --list          # sandbox deposits
python3 zenodo_upload.py --list --live    # production deposits
```

Displays a table like:

```
ID           State        DOI                  Title
───────────────────────────────────────────────────────────────────────
12345        published    10.5281/zenodo.…     Imscribing Grammar:…
12346        unpublished  —                     Draft Title Here
```

**States you may see:**
- `unsubmitted` — draft, not yet published
- `inprogress` — being processed
- `published` — live and citable
- `editing` — published but locked for editing

### Save as Draft (Skip Publishing)

```bash
python3 zenodo_upload.py --draft paper.pdf
```

Processes everything (create, upload, set metadata) but does **not** publish. The deposit stays in `unsubmitted` state. You can later publish it manually via the Zenodo web interface, or use the update workflow to add files before publishing.

---

## Interactive Metadata Walkthrough

When you run an upload command, the script guides you through metadata collection. Here's what it asks:

### Title
- **Prompt:** `Title [<auto-guess>]:`
- **Default:** Auto-guessed from the first filename (underscores/hyphens become spaces, words are title-cased)
- **Example:** For `manuscripts/as_above_so_below.pdf`, the default would be `As Above So Below`

### Description
- **Prompt:** `Description (1–3 sentences):`
- No default — you must provide a short summary

### Upload Type
- **Options:**
  1. `Publication (preprint, article, report, thesis…)`
  2. `Dataset`
  3. `Software`
  4. `Other`
- **Default:** `Publication`

### Publication Subtype (if "Publication" selected)
- **Options:**
  1. `Preprint`
  2. `Journal article`
  3. `Technical report`
  4. `Working paper`
  5. `Other`
- **Default:** `Preprint`

### Creator
- **Default:** `Mills, Lando` (ORCID: 0000-0003-0003-0552)
- Press Enter to accept the default, or type a different name in `Family, Given` format
- For multiple authors, you'd need to edit the script or submit a feature request

### Confirmation Summary
After all prompts, a summary is displayed. Type `Y` or press Enter to proceed, anything else to abort.

> **Note:** Access rights are always `open` and the license is always `cc-zero` (the closest Zenodo equivalent to the Unlicense used by IG publications). These are hardcoded defaults.
---

## All Command-Line Options

```
usage: zenodo_upload.py [-h] [--live] [--draft] [--update ID] [--list] [files ...]

Upload Imscribing Grammar publications to Zenodo.

positional arguments:
  files           Files to upload

optional arguments:
  -h, --help      Show this help message and exit
  --live          Publish to zenodo.org (default: sandbox)
  --draft         Save as draft instead of publishing immediately
  --update ID     Add files to an existing deposit (by Zenodo ID)
  --list          List your existing deposits and exit
```

---

## Examples

| Goal | Command |
| ---- | ------- |
| **Test upload on sandbox** | `python3 zenodo_upload.py paper.pdf` |
| **Publish a single paper** | `python3 zenodo_upload.py --live AS_ABOVE.pdf` |
| **Upload multiple files** | `python3 zenodo_upload.py --live paper.pdf appendix.pdf` |
| **Save as sandbox draft** | `python3 zenodo_upload.py --draft draft.pdf` |
| **Add a file to an existing deposit** | `python3 zenodo_upload.py --update 12345 corrected_fig.pdf` |
| **List sandbox deposits** | `python3 zenodo_upload.py --list` |
| **List production deposits** | `python3 zenodo_upload.py --list --live` |
| **Token prompt fallback** | `unset ZENODO_TOKEN ; python3 zenodo_upload.py --live paper.pdf` (will ask interactively) |

---

## Troubleshooting

### "requests not installed"

```text
Error: requests not installed — run: uv pip install requests
```

The `requests` library is missing. Install it:

```bash
uv pip install requests
# or, if not using uv:
pip install requests
```

### "File not found: ..."

```text
File not found: nonexistent.pdf
```

The file path is wrong. Check that the file exists at the path you provided. Use absolute or relative paths correctly.

### "Error 401" or "Error 403" during API calls

Your token is likely invalid, expired, or missing required scopes. Re-generate it at the Zenodo tokens page (see [Token Setup](#get-your-api-tokens)) and ensure you selected `deposit:write` and `deposit:actions`.

### "Error 400" with field-level errors

Zenodo rejected some metadata. The error message will show which field is problematic (e.g., a too-long title or invalid publication type). Adjust and rerun.

### Sandbox DOI is fake

That's expected. Sandbox DOIs like `10.5072/zenodo.123456` cannot be resolved. They only become real when you publish with `--live`.

### Production confirmation prompt

When you use `--live`, the script shows:

```
  *** PRODUCTION MODE — this will publish to zenodo.org ***
  Continue? [y/N]
```

You must explicitly type `y` or `yes` to proceed. Anything else aborts.
### Deposit stuck in "unsubmitted"

That's a draft. Either publish it manually at the Zenodo web interface, or run the upload again without `--draft`.

### "Error 500" from Zenodo

A temporary server error. Wait a moment and retry. If it persists, check [Zenodo's status page](https://status.zenodo.org/).

---

## Configuration Reference

These constants are defined at the top of `zenodo_upload.py` and can be customized if needed:

| Constant | Default | Notes |
| -------- | ------- | ----- |
| `DEFAULT_CREATOR` | `{"name": "Mills, Lando", "orcid": "0000-0003-0003-0552"}` | Default first author |
| `DEFAULT_LICENSE` | `"cc-zero"` | Creative Commons Zero — matches IG Unlicense ethos |
| `DEFAULT_UPLOAD_TYPE` | `"publication"` | Override if you always upload datasets or software |
| `DEFAULT_PUB_SUBTYPE` | `"preprint"` | Publication subtype when type is "publication" |
| `DEFAULT_ACCESS` | `"open"` | All IG publications are open access |
| `BASE["sandbox"]` | `"https://sandbox.zenodo.org/api"` | Sandbox API endpoint |
| `BASE["live"]` | `"https://zenodo.org/api"` | Production API endpoint |

---

## How It Works (for Developers)

The script follows Zenodo's [deposition API workflow](https://developers.zenodo.org/#deposition):

1. **Create** — `POST /api/deposit/depositions` → get a fresh deposition with a unique bucket URL
2. **Upload** — `PUT <bucket_url>/<filename>` with raw binary data (no JSON Content-Type)
3. **Set metadata** — `PUT /api/deposit/depositions/{id}` with JSON metadata payload
4. **Publish** — `POST /api/deposit/depositions/{id}/actions/publish` → get a DOI and record URL
5. **List** — `GET /api/deposit/depositions?size=25&sort=mostrecent`

File uploads bypass the session's JSON Content-Type header (since they're raw binary PUTs), then restore it for subsequent metadata calls.

---

*Generated for the Imscribing Grammar toolchain. For questions, contact Lando Mills.*
