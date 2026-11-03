from pathlib import Path
import hashlib,json
from bs4 import BeautifulSoup
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]


def test_static_content_and_contacts():
    for name in ('index.html','ru/index.html'):
        soup=BeautifulSoup((ROOT/name).read_text(encoding='utf-8'),'html.parser')
        assert len(soup.select('article.case'))==9
        assert soup.select_one('h1').get_text().strip()
        assert soup.select_one('#lead').get_text().strip()
        assert soup.select_one('#cv')['href'].endswith('.pdf')
        assert soup.select_one('meta[property="og:image"]')
        assert 'petrunovskii.work@gmail.com' in soup.get_text()
        assert 'yuripetrunovsky@gmail.com' not in soup.get_text()
        assert len(soup.select('link[hreflang]'))==2


def test_pdfs_match_manifest_and_one_page():
    manifest=json.loads((ROOT/'cv/manifest.json').read_text())
    for entry in manifest['files'].values():
        path=ROOT/'cv'/entry['filename']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256']
        pdf=PdfReader(path)
        assert len(pdf.pages)==1
        text=pdf.pages[0].extract_text()
        assert 'petrunovskii.work@gmail.com' in text
        assert 'petrunovskii.github.io/portfolio' in text
        assert '25K subscribers' not in text
