"""Reproducible, text-first one-page PDFs, plus the bot's identical verified copies."""
from pathlib import Path
import argparse,hashlib,json,shutil
from html import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]


def register_fonts():
    # CI uses Liberation Sans, metrically compatible with Arial.
    options=[(Path('C:/Windows/Fonts/arial.ttf'),Path('C:/Windows/Fonts/arialbd.ttf')),
             (Path('/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'),Path('/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf'))]
    for regular,bold in options:
        if regular.exists() and bold.exists():
            pdfmetrics.registerFont(TTFont('CV',str(regular)))
            pdfmetrics.registerFont(TTFont('CV-Bold',str(bold)))
            pdfmetrics.registerFontFamily('CV',normal='CV',bold='CV-Bold')
            return
    raise RuntimeError('Install Arial or fonts-liberation2')


def build(bot=None):
    register_fonts()
    profile=json.loads((ROOT/'data/profile.json').read_text(encoding='utf-8'))
    sources=json.loads((ROOT/'data/resumes.json').read_text(encoding='utf-8'))
    out=ROOT/'cv';out.mkdir(exist_ok=True)
    keys=('full_name','email','phone','linkedin','website','education')
    digest=hashlib.sha256(json.dumps({k:profile[k] for k in keys},ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    manifest={'version':profile['version'],'email':profile['email'],'profile_hash':digest,'files':{}}
    for role,source in sources.items():
        target=out/source['filename']
        for size in (10.1,9.8,9.5):
            base=ParagraphStyle('body',fontName='CV',fontSize=size,leading=size*1.23,textColor=colors.HexColor('#202736'),spaceAfter=2)
            heading=ParagraphStyle('section',parent=base,fontName='CV-Bold',fontSize=9.3,spaceBefore=6,spaceAfter=3,textColor=colors.HexColor('#294b65'))
            job=ParagraphStyle('job',parent=base,fontName='CV-Bold',spaceBefore=3)
            bullet=ParagraphStyle('bullet',parent=base,leftIndent=9,firstLineIndent=-7,spaceAfter=2)
            name=ParagraphStyle('name',parent=base,fontName='CV-Bold',fontSize=22,leading=25,spaceAfter=4)
            title=ParagraphStyle('title',parent=base,fontSize=12,leading=15,spaceAfter=7)
            tiny=ParagraphStyle('contact',parent=base,fontSize=9,leading=12,spaceAfter=2)
            story=[Paragraph(escape(profile['full_name']),name),Paragraph(escape(source['title']),title),
                   Paragraph('Tbilisi, Georgia | Open to relocation | '+escape(profile['phone']),tiny),
                   Paragraph(f'<link href="mailto:{escape(profile["email"])}">{escape(profile["email"])}</link> | <link href="{profile["telegram"]}">Telegram @petrunovskii</link>',tiny),
                   Paragraph(f'<link href="{profile["website"]}">petrunovskii.github.io/portfolio</link> | <link href="{profile["linkedin"]}">linkedin.com/in/yurii-petrunovskiy</link>',tiny)]
            for section in source['sections']:
                entries=section['entries']
                for i,item in enumerate(entries):
                    style=bullet if item['kind']=='bullet' else job if item['kind']=='title' else base
                    content=('• ' if item['kind']=='bullet' else '')+escape(item['text'])
                    para=Paragraph(content,style)
                    if i==0:story.append(KeepTogether([Paragraph(section['title'],heading),para]))
                    else:story.append(para)
            doc=SimpleDocTemplate(str(target),pagesize=A4,leftMargin=32,rightMargin=32,topMargin=27,bottomMargin=25,
                                  title=source['title']+' — '+profile['full_name'],author=profile['full_name'])
            doc.build(story)
            reader=PdfReader(target)
            if len(reader.pages)==1:break
        else:raise RuntimeError('Resume exceeds one page: '+role)
        text=reader.pages[0].extract_text()
        if profile['email'] not in text or 'github.io/portfolio' not in text:raise RuntimeError('Missing contacts')
        manifest['files'][role]={'filename':source['filename'],'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    if bot:
        dest=Path(bot)/'resumes';dest.mkdir(exist_ok=True)
        for p in out.iterdir():
            if p.suffix in ('.pdf','.json'):shutil.copy2(p,dest/p.name)
    print('Built and verified four one-page resumes')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bot',type=Path);args=p.parse_args();build(args.bot)
