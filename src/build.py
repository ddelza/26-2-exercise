# content.py로 index.html, ox.html, concepts.html을 만든다.
# 실행: python -I src/build.py  (레포 폴더에서)
import html, importlib.util, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('content', os.path.join(ROOT, 'src', 'content.py'))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
UNITS = C.UNITS

WS = r"C:\Users\user\Downloads\별과우주 학습지\build"
IMG = os.path.join(ROOT, 'img')


def copy_assets():
    """학습지 그림과 사진을 img/로 가져온다. 이미 있으면 건너뛴다."""
    try:
        from PIL import Image
    except ImportError:
        return
    need = set()
    for u in UNITS:
        for c in u['concepts']:
            for f, _, _ in c.get('img', []):
                if not f.startswith('g_'):
                    need.add(f)
    for f in sorted(need):
        dst = os.path.join(IMG, f)
        if os.path.exists(dst):
            continue
        src = None
        for d in os.listdir(WS):
            p = os.path.join(WS, d, f)
            if os.path.exists(p):
                src = p
        if not src:
            sys.exit('그림 없음: ' + f)
        im = Image.open(src)
        if f.endswith('.png'):
            im = im.convert('RGBA')
            bg = Image.new('RGBA', im.size, 'white')
            bg.alpha_composite(im)
            im = bg.convert('RGB')
            if im.width > 1300:
                im = im.resize((1300, round(im.height * 1300 / im.width)), Image.LANCZOS)
            im = im.quantize(256, dither=Image.Dither.NONE)
            im.save(dst, optimize=True)
        else:
            shutil.copy(src, dst)


def number():
    n = 0
    for u in UNITS:
        u['n'] = 0
        for c in u['concepts']:
            c['nums'] = []
            for q in c['q']:
                n += 1
                c['nums'].append(n)
                u['n'] += 1
    return n


def head(title, desc):
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="style.css?v=4">
</head>
'''


def nav(active):
    items = [('index.html', '처음으로'), ('ox.html', 'OX 100문제'), ('concepts.html', '기본 개념')]
    links = ''.join(f'<a href="{h}"{" aria-current=page" if h == active else ""}>{t}</a>' for h, t in items)
    online = '<span class="online" id="online" hidden><i aria-hidden="true"></i>지금 <b id="onlineN">0</b>명<span class="olt"> 사용 중</span></span>'
    return f'<header class="top"><div class="wrap topin"><a class="brand" href="index.html">3학년 과학 개념 확인</a>{online}<nav>{links}</nav></div></header>'


def groups():
    """대단원 > 중단원 > 소단원"""
    out = []
    for u in UNITS:
        if not out or out[-1]['big'] != u['big']:
            out.append({'big': u['big'], 'key': u['key'], 'mids': []})
        g = out[-1]
        if not g['mids'] or g['mids'][-1]['mid'] != u['mid']:
            g['mids'].append({'mid': u['mid'], 'units': []})
        g['mids'][-1]['units'].append(u)
    return out


def build_index(total):
    rows = ''
    for g in groups():
        cnt = sum(u['n'] for m in g['mids'] for u in m['units'])
        ccnt = sum(len(u['concepts']) for m in g['mids'] for u in m['units'])
        rows += f'<tr class="grp {g["key"]}"><th colspan="2" scope="colgroup">{g["big"]}</th><td>{ccnt}</td><td>{cnt}</td></tr>'
        for m in g['mids']:
            for u in m['units']:
                first = u['concepts'][0]['nums'][0]
                last = u['concepts'][-1]['nums'][-1]
                rng = f'{first}~{last}번' if first != last else f'{first}번'
                rows += (f'<tr><td class="mid">{m["mid"]}</td><td><a href="ox.html#{u["id"]}">{u["title"]}</a></td>'
                         f'<td>{len(u["concepts"])}</td><td>{u["n"]}<span class="rng">{rng}</span></td></tr>')
    allc = sum(len(u['concepts']) for u in UNITS)
    body = f'''<body>
<div class="stick" id="stick">{nav('index.html')}</div>
<main class="wrap">
<section class="hero">
<h1>기말고사 범위 개념 확인</h1>
<p>생식과 유전, 별과 우주의 핵심 개념을 OX 문제로 확인하고, 헷갈리는 내용은 그림과 함께 다시 봅니다.</p>
<div class="cta">
<a class="big" href="ox.html"><b>OX 100문제 풀기</b><span>누르면 바로 정답과 풀이가 나옵니다</span></a>
<a class="big alt" href="concepts.html"><b>기본 개념 보기</b><span>소단원별 핵심 개념 {allc}개</span></a>
</div>
</section>
<section>
<h2>문항 구성</h2>
<p class="lead">핵심 개념마다 1~3문제를 냈고, 자주 헷갈리는 개념은 문제를 더 넣었습니다. 소단원 이름을 누르면 그 문제로 이동합니다.</p>
<div class="tablewrap"><table class="plan">
<thead><tr><th scope="col">단원</th><th scope="col">소단원</th><th scope="col">핵심 개념</th><th scope="col">문항</th></tr></thead>
<tbody>{rows}
<tr class="sum"><th colspan="2" scope="row">합계</th><td>{allc}</td><td>{total}</td></tr></tbody>
</table></div>
</section>
</main>
<footer class="wrap foot">광수중학교 3학년 과학 · 교과서 쪽수는 2015 개정 과학 3 기준입니다. 사용 중인 인원은 이름 없는 임의 번호로만 셉니다.</footer>
<script src="app.js?v=2"></script>
</body></html>
'''
    write('index.html', head('3학년 과학 개념 확인', '생식과 유전, 별과 우주 개념 확인 OX 100문제와 기본 개념') + body)


def build_ox(total):
    jump = ''
    sec = ''
    for g in groups():
        jump += f'<div class="jg {g["key"]}"><b>{g["big"]}</b>'
        for m in g['mids']:
            for u in m['units']:
                jump += f'<a href="#{u["id"]}">{u["title"]}<span data-prog="{u["id"]}">{u["n"]}문제</span></a>'
        jump += '</div>'
    for u in UNITS:
        sec += f'<section class="unit {u["key"]}" id="{u["id"]}" data-unit="{u["id"]}">'
        sec += f'<p class="crumb">{u["big"]} · {u["mid"]}</p><h2>{u["title"]}</h2>'
        for c in u['concepts']:
            for n, (st, a, sol) in zip(c['nums'], c['q']):
                qid = f'q{n:03d}'
                sec += f'''<article class="q" id="{qid}" data-a="{a}" data-unit="{u["id"]}">
<div class="qrow"><span class="qn">{n}</span><p class="st">{html.escape(st)}</p>
<div class="btns" role="group" aria-label="{n}번 답 고르기"><button type="button" class="o" data-v="O" aria-label="O, 맞다">O</button><button type="button" class="x" data-v="X" aria-label="X, 틀리다">X</button></div></div>
<div class="sol" hidden><p class="res"></p><p class="exp"><b>풀이</b> {html.escape(sol)}</p>
<p class="solfoot"><a class="go" href="concepts.html?from={qid}#{c["id"]}">개념 보기: {html.escape(c["title"])}</a><button type="button" class="again">다시 풀기</button></p></div>
</article>
'''
        sec += '</section>'
    body = f'''<body class="oxpage">
<div class="stick" id="stick">{nav('ox.html')}
<div class="bar"><div class="wrap barin">
<div class="score" aria-live="polite"><b id="done">0</b>/{total} 풀이 · 맞힘 <b id="right">0</b></div>
<div class="filters" role="group" aria-label="문제 거르기">
<button type="button" data-f="all" aria-pressed="true">전체</button>
<button type="button" data-f="todo" aria-pressed="false">안 푼 문제</button>
<button type="button" data-f="wrong" aria-pressed="false">틀린 문제</button>
</div>
<div class="tools"><button type="button" id="showall" aria-pressed="false">풀이 모두 보기</button><button type="button" id="reset">기록 지우기</button></div>
</div><div class="meter"><i id="meter"></i></div></div></div>
<main class="wrap">
<h1>개념 확인 OX 100문제</h1>
<p class="lead">문장이 맞으면 O, 틀리면 X를 누르세요. 푼 기록은 지금 쓰는 기기의 브라우저에만 저장됩니다.</p>
<details class="jump"><summary>소단원 바로가기</summary><div class="jgs">{jump}</div></details>
<p class="empty" id="empty" hidden>조건에 맞는 문제가 없습니다.</p>
{sec}
</main>
<footer class="wrap foot">광수중학교 3학년 과학</footer>
<script src="app.js?v=2"></script>
</body></html>
'''
    write('ox.html', head('개념 확인 OX 100문제', '생식과 유전, 별과 우주 개념 확인 OX 문제') + body)


def size(f):
    """그림 자리를 미리 잡아 개념 링크로 이동한 뒤 화면이 밀리지 않게 한다."""
    p = os.path.join(IMG, f)
    if f.endswith('.svg'):
        m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', open(p, encoding='utf8').read())
        return round(float(m[1])), round(float(m[2]))
    from PIL import Image
    return Image.open(p).size


def figure(items):
    photos = all(f.endswith('.jpg') for f, _, _ in items)
    s = f'<div class="figs{" photos" if photos else ""}">'
    for f, alt, cap in items:
        s += (f'<figure class="{"ph" if f.endswith(".jpg") else ""}"><a href="img/{f}" target="_blank" rel="noopener" title="크게 보기">'
              f'<img src="img/{f}" alt="{html.escape(alt)}" width="{size(f)[0]}" height="{size(f)[1]}" loading="lazy"></a><figcaption>{html.escape(cap)}</figcaption></figure>')
    return s + '</div>'


def build_concepts():
    toc = ''
    main = ''
    for g in groups():
        toc += f'<div class="tg {g["key"]}"><b>{g["big"]}</b>'
        for m in g['mids']:
            toc += f'<p class="tm">{m["mid"]}</p>'
            for u in m['units']:
                toc += f'<a href="#k{u["id"]}">{u["title"]}</a>'
        toc += '</div>'
    for u in UNITS:
        main += f'<section class="kunit {u["key"]}" id="k{u["id"]}"><p class="crumb">{u["big"]} · {u["mid"]} · 교과서 {u["page"]}쪽</p><h2>{u["title"]}</h2>'
        for c in u['concepts']:
            nums = ' '.join(f'<a href="ox.html#q{n:03d}">{n}번</a>' for n in c['nums'])
            main += f'<article class="concept" id="{c["id"]}"><h3>{c["title"]}<span class="pg">교과서 {c["page"]}쪽</span></h3>'
            if c.get('points'):
                main += '<ul>' + ''.join(f'<li>{p}</li>' for p in c['points']) + '</ul>'
            if c.get('table'):
                t = c['table']
                main += '<div class="tablewrap"><table class="cmp"><thead><tr>' + ''.join(f'<th scope="col">{h}</th>' for h in t['head']) + '</tr></thead><tbody>'
                for r in t['rows']:
                    main += f'<tr><th scope="row">{r[0]}</th>' + ''.join(f'<td>{x}</td>' for x in r[1:]) + '</tr>'
                main += '</tbody></table></div>'
            if c.get('img'):
                main += figure(c['img'])
            if c.get('warn'):
                main += f'<p class="warn"><b>헷갈리지 말기</b> {c["warn"]}</p>'
            if c.get('note'):
                main += f'<p class="note"><b>더 보기</b> {c["note"]}</p>'
            main += f'<p class="rel">이 개념의 OX 문제: {nums}</p></article>'
        main += '</section>'
    body = f'''<body class="kpage">
<div class="stick" id="stick">{nav('concepts.html')}</div>
<div class="wrap klayout">
<aside class="toc"><details open><summary>목차</summary>{toc}</details></aside>
<main>
<h1>기본 개념</h1>
<p class="lead">교과서 내용을 소단원별로 간단히 정리했습니다. 그림을 누르면 크게 볼 수 있습니다.</p>
{main}
<p class="credit">{C.CREDITS}</p>
</main>
</div>
<a class="back" id="back" href="ox.html" hidden>문제로 돌아가기</a>
<script src="app.js?v=2"></script>
</body></html>
'''
    write('concepts.html', head('기본 개념', '생식과 유전, 별과 우주 교과서 기본 개념 정리') + body)


def write(name, s):
    with open(os.path.join(ROOT, name), 'w', encoding='utf8', newline='\n') as f:
        f.write(s)


def check(total):
    ids = [c['id'] for u in UNITS for c in u['concepts']]
    assert len(ids) == len(set(ids))
    answers = [q[1] for u in UNITS for c in u['concepts'] for q in c['q']]
    print('문항', total, 'O', answers.count('O'), 'X', answers.count('X'), '개념', len(ids))
    run = best = 0
    prev = None
    for a in answers:
        run = run + 1 if a == prev else 1
        prev = a
        best = max(best, run)
    print('같은 답 최대 연속', best)
    for u in UNITS:
        print(f'{u["id"]} {u["title"]}: 개념 {len(u["concepts"])} 문항 {u["n"]}')


if __name__ == '__main__':
    copy_assets()
    total = number()
    check(total)
    build_index(total)
    build_ox(total)
    build_concepts()
