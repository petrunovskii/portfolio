# Yurii Petrunovskii — portfolio and CV

Static bilingual portfolio hosted by the existing GitHub Pages setup. English lives at `/portfolio/`, Russian at `/portfolio/ru/`. Main content, contact links and case studies are present in HTML without JavaScript. JavaScript adds role filtering and opens linked case studies.

Source content:

- `data/site.json`: nine case studies, coverage, videos, education and experience.
- `data/profile.json`: public contacts and role-specific introductions. It contains no salary, citizenship or work-authorization data.
- `data/resumes.json`: editable source text for four CVs.
- `tools/build.py`: generates both language pages.
- `tools/build_resumes.py`: generates four one-page text PDFs and a SHA-256 manifest; `--bot ../claudevacancies` copies identical files to the private bot.
- `assets/`: CSS, progressively enhanced filtering, existing photos extracted unchanged from the previous embedded images.

Run `python tools/build.py` after editing page data. For PDF builds install the dependencies in `requirements-dev.txt` and Arial (Windows) or `fonts-liberation2` (Linux), then run `python tools/build_resumes.py --bot ../claudevacancies`. Keep the generated HTML/PDFs committed: Pages does not need a new hosting service or a JavaScript build toolchain.

The private bot's `candidate.yaml` is the source of contact/education facts. Its `tools/sync_profile.py --portfolio ../portfolio` exports only public fields. Rebuild HTML and PDFs after syncing. The bot refuses PDFs whose manifest or public profile fingerprint no longer matches.

Role links use `?role=pr`, `?role=pmm`, `?role=marcom` or `?role=pm`; a specific case can be shared as `?role=pmm#trisigma`. Legacy `#lang=...&role=...` role links continue to work. GitHub Pages should remain configured to deploy from the repository root.

Validation: `python -m pytest -q`; static content/contact/link metadata and all PDF hashes/page counts are checked on push/PR. Browser QA covers EN/RU, all role filters, direct case links and a 390px mobile viewport.
