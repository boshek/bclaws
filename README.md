# BC Laws Archive

Automated archive of British Columbia legislation in markdown format, sourced from [bclaws.gov.bc.ca](https://www.bclaws.gov.bc.ca).

## Overview

This repository contains a complete mirror of BC statutes and regulations, automatically updated weekly via GitHub Actions. The legislation is converted from XML to markdown for easy reading and version tracking.

## Structure

```
laws/
├── statutes/
│   ├── A/
│   ├── B/
│   └── ...
└── regulations/
    ├── A/
    ├── B/
    └── ...
```

Documents are organized alphabetically by title within statute and regulation folders.

## Usage

### Running the Scraper Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the scraper:
```bash
python bc_laws_scraper.py
```

This will fetch all BC legislation and save it to the `laws/` directory.

### Automated Updates

The GitHub Actions workflow runs weekly (every Sunday at 2 AM UTC) and automatically:
- Fetches the latest legislation
- Commits only changed files
- Pushes updates to the repository

You can also trigger the workflow manually from the Actions tab.

## Data Source

All content is sourced from the [BC Laws API](https://www.bclaws.gov.bc.ca/civix/content/complete/statreg/) under the [King's Printer Licence](https://www2.gov.bc.ca/gov/content/home/copyright).

## Important Legal Notice

**THIS IS NOT AN OFFICIAL VERSION**

These materials contain information that has been derived from information originally made available by the Province of British Columbia at: [www.bclaws.gov.bc.ca](https://www.bclaws.gov.bc.ca)

This is an unofficial archive for educational and research purposes only. **For official legal documents, always refer to [bclaws.gov.bc.ca](https://www.bclaws.gov.bc.ca).**

## License

This repository uses a dual licensing structure:

### Code (Scraper)
The scraper code and scripts in this repository are licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Data (BC Laws)
All BC legislation content in the `laws/` directory is subject to the [King's Printer License – British Columbia](https://www.bclaws.ca/standards/Licence.html) and belongs to the Province of British Columbia.

The content is provided "as is" without warranty. The Province of British Columbia disclaims all liability for errors, omissions, or damages resulting from use of this information.

## Contributing

Issues and improvements to the scraper are welcome. Note that the legislation content itself should not be manually edited as it will be overwritten on the next automated run.
