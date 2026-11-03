"""Build static English/Russian pages. Source content stays readable in data/site.json."""
from pathlib import Path
import html
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/site.json').read_text(encoding='utf-8'))
PROFILE = json.loads((ROOT / 'data/profile.json').read_text(encoding='utf-8'))


def e(text):
    return html.escape(str(text), quote=True)


def link(text, url):
    return f'<a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(text)}</a>'


def paragraphs(items):
    return ''.join('<p>' + e(x) + '</p>' for x in items)


def build(lang):
    ru = lang == 'ru'
    t = DATA['T'][lang]
    prefix = '../' if ru else './'
    public = 'https://petrunovskii.github.io/portfolio/'
    page_url = public + ('ru/' if ru else '')
    name = 'Юрий Петруновский' if ru else PROFILE['full_name']
    words = {
        'work': 'Кейсы' if ru else 'Case studies', 'contact': 'Связаться' if ru else 'Get in touch',
        'cv': 'Скачать резюме' if ru else 'Download CV', 'share': 'Ссылка на кейс' if ru else 'Link to this case',
        'all': 'Все проекты' if ru else 'All projects', 'press': 'Публикации' if ru else 'Coverage',
        'background': 'Опыт' if ru else 'Experience',
    }
    roles = PROFILE['roles'][lang]
    case_html = []
    for case in DATA['CASES']:
        d = case[lang]
        labels = t['labels']
        detail = []
        for field, title in [('context','context'),('task','task'),('role','role')]:
            detail.append(f'<h4>{e(labels[title])}</h4><p>{e(d[field])}</p>')
        for field, title in [('did','did'),('results','results')]:
            detail.append(f'<h4>{e(labels[title])}</h4><ul>' + ''.join('<li>'+e(x)+'</li>' for x in d[field]) + '</ul>')
        if case.get('photos'):
            detail.append('<div class="photos">'+''.join(f'<img src="{prefix+DATA["assets"][k]}" loading="lazy" alt="{e(d["title"])}">' for k in ['bb2','bb1','cup'])+'</div>')
        detail.append(f'<h4>{e(labels["note"])}</h4><p>{e(d["note"])}</p>')
        if case['links']:
            detail.append('<p class="sources">' + ' · '.join(link(title,url) for title,url in case['links']) + '</p>')
        detail.append(f'<a class="case-link" href="#{case["id"]}">{words["share"]} ↗</a>')
        case_html.append(f'''<article class="case" id="{case['id']}" data-roles="{' '.join(case['roles'])}">
          <p class="eyebrow">{e(d['meta'])}</p><h3>{e(d['title'])}</h3><p class="case-lead">{e(d['lead'])}</p>
          <details><summary>{e(t['open'])}</summary><div class="case-body">{''.join(detail)}</div></details></article>''')
    coverage = ''.join(f'<li><span>{e(p[0])}</span>{link(p[1] if ru else p[2],p[3])}</li>' for p in DATA['PRESS'])
    commentary = ''.join(f'<li><span>{e(c["outlet_ru"] if ru else c["outlet"])}</span>' +
                         (link(c['ru'] if ru else c['en'],c['url']) if c['url'] else '<span>'+e(c['ru'] if ru else c['en'])+'</span>') + '</li>' for c in DATA['COMM'])
    videos = ''.join(f'<a class="video" href="https://www.youtube.com/watch?v={v["id"]}" target="_blank" rel="noopener noreferrer"><img src="https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg" loading="lazy" alt="" width="480" height="270"><strong>{e(v[lang])}</strong><span>{e(v["mru"] if ru else v["men"])}</span></a>' for v in DATA['VIDEO'])
    background = ''.join(f'<div class="job"><h3>{e(r[0])}</h3><p>{e(r[1])}</p><p class="eyebrow">{e(r[2])}</p></div>' for r in DATA['BG'][lang])
    filters = ''.join(f'<button type="button" data-role="{r}" aria-pressed="{str(r=="all").lower()}">{e(t["filter"][r])}</button>' for r in DATA['ROLES'])
    cv = prefix + DATA['CV']['pr']
    safe_data = json.dumps({'roles':roles,'cv':DATA['CV'],'prefix':prefix,'order':DATA['ORDER']},ensure_ascii=False).replace('<','\\u003c')
    title = name + '. ' + roles['pr']['title']
    text = f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(roles['pr']['lead'])}">
<link rel="canonical" href="{page_url}"><link rel="alternate" hreflang="en" href="{public}"><link rel="alternate" hreflang="ru" href="{public}ru/">
<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(roles['pr']['lead'])}"><meta property="og:url" content="{page_url}"><meta property="og:image" content="{public}assets/me.jpg"><meta name="twitter:card" content="summary">
<link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/site.js" defer></script></head>
<body><a class="skip" href="#main">{'К содержанию' if ru else 'Skip to content'}</a>
<div class="wrap"><nav class="top" aria-label="{'Навигация' if ru else 'Navigation'}"><a class="brand" href="{prefix}">{e(name)}</a><div class="nav-links"><a href="#work">{words['work']}</a><a href="#contact">{words['contact']}</a></div><div class="languages"><a href="{prefix}" lang="en" {'aria-current="page"' if not ru else ''}>EN</a><a href="{prefix}ru/" lang="ru" {'aria-current="page"' if ru else ''}>RU</a></div></nav>
<header class="hero"><img class="portrait" src="{prefix+DATA['assets']['me']}" width="180" height="180" alt="{e(name)}"><p class="eyebrow">{'Тбилиси · Готов к переезду' if ru else 'Tbilisi, Georgia · Open to relocation'}</p><h1>{e(name)}</h1><p class="hero-role" id="role">{e(roles['pr']['title'])}</p><p class="hero-lead" id="lead">{e(roles['pr']['lead'])}</p><div class="actions"><a class="primary" id="cv" href="{cv}" target="_blank" rel="noopener">{words['cv']} ↗</a><a href="mailto:{e(PROFILE['email'])}">{e(PROFILE['email'])}</a>{link('Telegram',PROFILE['telegram'])}{link('LinkedIn',PROFILE['linkedin'])}</div><p class="language-note">{e(' · '.join(DATA['LANGS'][lang]))}</p></header>
<main id="main"><section id="work"><div class="section-heading"><h2>{words['work']}</h2><span class="count" id="case-count">9</span></div><p class="section-note">{e(t['workNote'])}</p><div class="filter" id="filter" role="group" aria-label="{'Роль' if ru else 'Role'}">{filters}</div><div id="cases">{''.join(case_html)}</div></section>
<section id="press"><h2>{words['press']}</h2><p class="section-note">{e(t['pressNote'])}</p><ul class="press">{coverage}</ul><h3 class="subhead">{e(t['commH'])}</h3><p class="section-note">{e(t['commNote'])}</p><ul class="press">{commentary}</ul></section>
<section id="video"><h2>{e(t['videoH'])}</h2><p class="section-note">{e(t['videoNote'])}</p><div class="videos">{videos}</div></section>
<section id="background"><h2>{words['background']}</h2>{background}<div class="two"><div><h3>{e(t['eduH'])}</h3>{paragraphs(DATA['EDU'][lang])}</div><div><h3>{e(t['langH'])}</h3>{paragraphs(DATA['LANGS'][lang])}</div></div></section></main>
<footer id="contact"><p class="footer-lead">{e(t['footBig'])}</p><div class="actions"><a href="mailto:{e(PROFILE['email'])}">{e(PROFILE['email'])}</a>{link('Telegram',PROFILE['telegram'])}{link('LinkedIn',PROFILE['linkedin'])}</div></footer></div><script type="application/json" id="site-data">{safe_data}</script></body></html>'''
    dest = ROOT / ('ru/index.html' if ru else 'index.html')
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(text,encoding='utf-8')


if __name__ == '__main__':
    for lang in ('en','ru'):
        build(lang)
    print('Built static EN/RU pages')
