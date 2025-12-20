#!/usr/bin/env python3
"""
BC Laws Scraper
Fetches all BC legislation from bclaws.gov.bc.ca and converts to markdown
"""

import requests
import xml.etree.ElementTree as ET
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class BCLawsScraper:
    BASE_URL = "https://www.bclaws.gov.bc.ca"
    METADATA_URL = f"{BASE_URL}/civix/content/complete/statreg"
    DOCUMENT_URL = f"{BASE_URL}/civix/document/id/complete/statreg"

    def __init__(self, output_dir: str = "laws"):
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'https://github.com/boshek/bclaws'
        })

    def clean_text(self, text: str) -> str:
        """Clean up text formatting and spacing"""
        # First, normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        # Fix spaces before punctuation (except quotes)
        text = re.sub(r'\s+([,;:.!?)])', r'\1', text)
        # Fix spaces after opening parenthesis
        text = re.sub(r'([(])\s+', r'\1', text)

        # Ensure space before opening quote if preceded by word (do this BEFORE cleaning inside)
        text = re.sub(r'(\w)"', r'\1 "', text)

        # Remove spaces inside quotes in one pass
        # Match: " (spaces) content (spaces) "
        # Replace with: "content"
        def fix_quoted_text(match):
            content = match.group(1).strip()
            return f'"{content}"'

        text = re.sub(r'"([^"]+)"', fix_quoted_text, text)

        # Ensure space after CLOSING quote if followed by word
        # Use lookahead/lookbehind to only match closing quotes (preceded by word char)
        text = re.sub(r'(\w)"(\w)', r'\1" \2', text)

        # Ensure space after comma
        text = re.sub(r',([^\s])', r', \1', text)

        return text.strip()

    def fetch_document_metadata(self, doc_id: str) -> Optional[Dict[str, str]]:
        """Fetch metadata for a document (returns title and full doc ID)"""
        url = f"{self.METADATA_URL}/{doc_id}"
        try:
            response = self.session.get(url, timeout=30)

            # Handle 404 - document doesn't exist (not an error)
            if response.status_code == 404:
                return None

            response.raise_for_status()

            # Parse XML to get document ID and title
            root = ET.fromstring(response.content)

            # Find the main document element
            for elem in root.findall('.//document'):
                full_id = elem.findtext('CIVIX_DOCUMENT_ID')
                title = elem.findtext('CIVIX_DOCUMENT_TITLE')
                if full_id and title:
                    return {
                        'id': full_id,
                        'title': title,
                        'base_id': doc_id
                    }

            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching metadata for {doc_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {doc_id}: {e}")
            return None

    def fetch_document_content(self, doc_id: str) -> Optional[str]:
        """Fetch the actual XHTML content of a document"""
        url = f"{self.DOCUMENT_URL}/{doc_id}"
        try:
            response = self.session.get(url, timeout=30)

            # Handle 404 - document doesn't exist (not an error)
            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching content for {doc_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching content for {doc_id}: {e}")
            return None

    def xhtml_to_markdown(self, xhtml: str, title: str) -> str:
        """Convert XHTML document to clean markdown"""
        soup = BeautifulSoup(xhtml, 'lxml')

        markdown = []
        markdown.append(f"# {title}\n")

        # Add required legal disclaimer
        markdown.append("---\n")
        markdown.append("**DISCLAIMER: THIS IS NOT AN OFFICIAL VERSION**\n")
        markdown.append("\nInformation derived from [BC Laws](https://www.bclaws.gov.bc.ca) ")
        markdown.append("under the [King's Printer License](https://www.bclaws.ca/standards/Licence.html). ")
        markdown.append("For official versions, visit [bclaws.gov.bc.ca](https://www.bclaws.gov.bc.ca).\n")

        # Extract act metadata (chapter info)
        act_title = soup.find('div', id='title')
        if act_title:
            h3 = act_title.find('h3')
            if h3:
                text = self.clean_text(h3.get_text(separator=' ', strip=True))
                markdown.append(f"*{text}*\n")

        markdown.append("\n---\n")

        # Extract main content sections (table of contents)
        contents_div = soup.find('div', id='contents')
        if contents_div:
            markdown.append("\n## Contents\n")
            # The contents are in a table with rows containing section number and title
            table = contents_div.find('table')
            if table:
                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        # Second cell has the number, third has the title
                        num = cells[1].get_text(strip=True)
                        title = cells[2].get_text(strip=True) if len(cells) > 2 else ''
                        if num and title:
                            markdown.append(f"- **{num}** {title}")
            markdown.append("\n---\n")

        # Extract all sections
        sections = soup.find_all('div', class_='section')
        for section in sections:
            # Section heading
            heading = section.find('h4')
            if heading:
                heading_text = heading.get_text(strip=True)
                markdown.append(f"\n## {heading_text}\n")

            # Section paragraphs
            for para in section.find_all(['p']):
                # Get section number
                secnum = para.find('span', class_='secnum')
                if secnum:
                    num_text = secnum.get_text(strip=True)
                    # Remove the number from the paragraph text
                    for span in secnum.find_all('span'):
                        span.decompose()
                    secnum.decompose()

                    para_text = self.clean_text(para.get_text(separator=' ', strip=True))
                    if para_text:
                        markdown.append(f"\n**{num_text}** {para_text}\n")
                else:
                    para_text = self.clean_text(para.get_text(separator=' ', strip=True))

                    if para_text and not para_text.startswith('Copyright'):
                        # Handle subsections/subparagraphs
                        if 'sub' in para.get('class', []):
                            markdown.append(f"  {para_text}\n")
                        elif 'para' in para.get('class', []):
                            markdown.append(f"  - {para_text}\n")
                        else:
                            markdown.append(f"{para_text}\n")

        return "\n".join(markdown)

    def get_output_path(self, title: str, doc_type: str = 'statute') -> Path:
        """Generate organized output path"""
        # Clean title for filename
        clean_title = re.sub(r'[^\w\s-]', '', title)
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        clean_title = clean_title[:100]  # Limit length

        # Get first letter for alphabetical organization
        first_letter = clean_title[0].upper() if clean_title else 'A'
        if not first_letter.isalpha():
            first_letter = '0-9'

        # Create path: laws/statutes/A/filename.md
        folder = self.output_dir / doc_type / first_letter
        folder.mkdir(parents=True, exist_ok=True)

        return folder / f"{clean_title}.md"

    def scrape_document(self, doc_id: str) -> tuple[bool, str]:
        """
        Scrape a single document by its base ID
        Returns: (success: bool, status: str) where status is 'success', 'not_found', or 'error'
        """
        # Step 1: Get metadata
        metadata = self.fetch_document_metadata(doc_id)
        if not metadata:
            return False, 'not_found'

        logger.info(f"Processing {doc_id}: {metadata['title']}")

        # Step 2: Fetch content
        content = self.fetch_document_content(metadata['id'])
        if not content:
            logger.warning(f"Failed to fetch content for {doc_id}")
            return False, 'error'

        # Step 3: Convert to markdown
        try:
            markdown = self.xhtml_to_markdown(content, metadata['title'])
        except Exception as e:
            logger.error(f"Error converting {doc_id} to markdown: {e}")
            return False, 'error'

        # Step 4: Save
        try:
            doc_type = 'statute' if doc_id.startswith(('96', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25')) else 'regulation'
            output_path = self.get_output_path(metadata['title'], doc_type)
            output_path.write_text(markdown, encoding='utf-8')
            logger.info(f"✓ Saved: {metadata['title']}")
            return True, 'success'
        except Exception as e:
            logger.error(f"Error saving {doc_id}: {e}")
            return False, 'error'

    def scrape_all(self, start_year: str = '96', end_num: int = 600):
        """Scrape multiple documents by iterating through ID patterns"""
        logger.info(f"Starting BC Laws scraper (pattern: {start_year}XXX)...")

        successful = 0
        not_found = 0
        errors = 0

        for num in range(1, end_num):
            doc_id = f"{start_year}{num:03d}"

            success, status = self.scrape_document(doc_id)

            if status == 'success':
                successful += 1
            elif status == 'not_found':
                not_found += 1
            else:  # error
                errors += 1

            # Rate limiting
            time.sleep(0.5)

            # Progress update every 50 documents
            if num % 50 == 0:
                logger.info(f"Progress: {num}/{end_num} tried | "
                          f"{successful} found | {not_found} not found | {errors} errors")

        logger.info(f"\n{'='*60}")
        logger.info(f"Scraping complete!")
        logger.info(f"  Successfully scraped: {successful} documents")
        logger.info(f"  Not found (expected): {not_found} documents")
        logger.info(f"  Errors (investigate): {errors} documents")
        logger.info(f"{'='*60}")


def main():
    scraper = BCLawsScraper(output_dir="laws")

    # Scrape all BC statutes
    scraper.scrape_all(start_year='96', end_num=600)


if __name__ == "__main__":
    main()
