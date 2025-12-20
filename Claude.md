# BC Laws Scraper - Development Notes

## Project Goal
Scrape all BC legislation from bclaws.gov.bc.ca, convert to markdown, store in GitHub repo, and automate updates on a schedule.

## Important Context
- This does NOT need to be a CLI tool - just a simple Python script that can be run
- Target: All BC statutes and regulations
- Output format: Markdown
- Automation: GitHub Actions running weekly
- **Always use `uv` for package management** (not pip)
- **Use local .venv**: `uv pip install -r requirements.txt --python .venv/bin/python`

## Current Status

### What We've Built
1. `bc_laws_scraper.py` - Main scraper class
2. `test_single.py` - Single law test script
3. GitHub Actions workflow for automation
4. Requirements.txt, README, .gitignore

### API Discovery - SOLVED ✓

**Test case**: Age of Majority Act (ID: 96007)

**API Structure Found**:
1. **Metadata endpoint**: `https://www.bclaws.gov.bc.ca/civix/content/complete/statreg/96007`
   - Returns document info, ID (96007_01), title
   - ~2.6 KB XML

2. **Content endpoint**: `https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/96007_01`
   - Returns full law as XHTML
   - ~11.8 KB
   - Has proper sections, subsections, paragraphs
   - Content-Type: text/html;charset=utf-8

**Key Findings**:
- Two-step process: Get metadata first, then fetch content with full ID
- Content is XHTML, not plain XML
- Structure uses div.section, proper heading tags
- Includes table of contents, section numbers, text

## Known Good
- Table of contents formatting
- Quote handling (no spaces inside quotes)
- Proper spacing and punctuation
- Section numbering and formatting

## Legal Compliance

**King's Printer License Requirements:**
- ✓ Attribution to Province of BC in README
- ✓ "NOT AN OFFICIAL VERSION" disclaimer in README and each law file
- ✓ Links to official source (bclaws.gov.bc.ca)
- ✓ Reference to King's Printer License
- ✓ License URL: https://www.bclaws.ca/standards/Licence.html

**What we can do:**
- Use, copy, publish, distribute (royalty-free, perpetual)
- Convert format (XML to Markdown)
- Educational/research purposes

**What we cannot do:**
- Claim official status
- Remove disclaimers
- Imply government endorsement

## Current Configuration

**Scraper mode:** Full scrape (96XXX series, up to 600 documents)
**Rate limiting:** 0.5s between requests
**Output:** laws/statute/ and laws/regulation/ directories
**GitHub Actions:** Runs weekly (Sundays 2 AM UTC) with write permissions
