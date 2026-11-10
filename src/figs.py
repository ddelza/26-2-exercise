# 생식과 유전 개념 그림(SVG) 생성기. 교과서 그림을 복사하지 않고 직접 그린다.
# 실행: python -I figs.py <img 폴더>
import math, os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
FONT = "'Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','Apple SD Gothic Neo',sans-serif"
INK = '#1f2a37'
MUTE = '#5b6776'
B = '#2f6fd0'   # 긴 상동 염색체 쌍 (쌍끼리 같은 색)
R = '#e0762b'   # 짧은 상동 염색체 쌍 (쌍끼리 같은 색)
CELL = '#fdf6e3'
CELLS = '#c9b98c'
PANEL = '#f6f8fb'
LINE = '#d6dde6'


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'font-family="{FONT}"><rect width="{w}" height="{h}" fill="#fff"/>{body}</svg>')


def t(x, y, s, size=16, fill=INK, anchor='middle', weight='400'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{s}</text>'


def bar(x, y, h, color, angle=0, w=8):
    """염색 분체 한 가닥(복제 전 염색체 한 개)"""
    return (f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="{w/2}" fill="{color}" '
            f'transform="rotate({angle} {x} {y})"/>')


def arm(cx, y, half, w, color, ang, top):
    y0 = y - half if top else y
    return (f'<rect x="{cx-w/2:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{half:.1f}" rx="{w/2:.1f}" fill="{color}" '
            f'stroke="{INK}" stroke-width="0.8" transform="rotate({ang} {cx:.1f} {y})"/>')


def xch(x, y, h, color, w=None, t=13):
    """두 가닥의 염색 분체가 가운데에서 붙은 X자 염색체"""
    w = w or max(6.5, h * 0.2)
    half, d = h / 2, w * 0.46
    return (arm(x - d, y, half, w, color, -t, True) + arm(x - d, y, half, w, color, t, False)
            + arm(x + d, y, half, w, color, t, True) + arm(x + d, y, half, w, color, -t, False))


def chromatid(x, y, h, color, side, w=None, t=20):
    """분리되어 이동하는 염색 분체 한 가닥. side -1은 왼쪽, 1은 오른쪽으로 이동"""
    w = w or max(6, h * 0.2)
    return arm(x, y, h / 2, w, color, -side * t, True) + arm(x, y, h / 2, w, color, side * t, False)


def cell(x, y, rx, ry=None, dashed=False):
    ry = ry or rx
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{CELL}" stroke="{CELLS}" stroke-width="2.5"/>'


def nucleus(x, y, r, dashed=False):
    d = ' stroke-dasharray="5 5"' if dashed else ''
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f3e6c4" stroke="#a8956a" stroke-width="1.6"{d}/>'


def threads(x, y, r):
    s = ''
    for i, c in enumerate([B, R, B, R]):
        pts = []
        for k in range(9):
            a = k / 8 * math.pi * 2 + i * 1.5
            rr = r * (0.25 + 0.55 * ((k * 37 + i * 13) % 10) / 10)
            pts.append(f'{x + rr * math.cos(a):.1f},{y + rr * math.sin(a):.1f}')
        s += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round"/>'
    return s


def panel(x, y, w, h, title, note=''):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{PANEL}" stroke="{LINE}"/>'
    s += t(x + w / 2, y + 26, title, 17, INK, weight='700')
    for i, line in enumerate(note.split('|') if note else []):
        s += t(x + w / 2, y + h - 34 + i * 20, line, 14.5, MUTE)
    return s


def arrow(x1, y1, x2, y2, color=MUTE, w=2.4):
    ang = math.atan2(y2 - y1, x2 - x1)
    a1, a2 = ang + 2.6, ang - 2.6
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}"/>'
            f'<polygon points="{x2},{y2} {x2 + 11 * math.cos(a1):.1f},{y2 + 11 * math.sin(a1):.1f} '
            f'{x2 + 11 * math.cos(a2):.1f},{y2 + 11 * math.sin(a2):.1f}" fill="{color}"/>')


# ---- 1. 우무 조각 -----------------------------------------------------------
def box3d(x, y, w, h, d, fill='#f5c9c0', edge='#c0604f'):
    dx, dy = d * 0.6, d * 0.45
    return (f'<polygon points="{x},{y} {x+w},{y} {x+w},{y+h} {x},{y+h}" fill="{fill}" stroke="{edge}" stroke-width="2"/>'
            f'<polygon points="{x},{y} {x+dx},{y-dy} {x+w+dx},{y-dy} {x+w},{y}" fill="#f9dcd5" stroke="{edge}" stroke-width="2"/>'
            f'<polygon points="{x+w},{y} {x+w+dx},{y-dy} {x+w+dx},{y+h-dy} {x+w},{y+h}" fill="#eeb5a9" stroke="{edge}" stroke-width="2"/>')


def fig_agar():
    b = panel(10, 10, 305, 300, '자르기 전: 큰 조각 1개')
    b += box3d(60, 95, 160, 80, 80)
    b += t(140, 200, '가로 4 cm · 세로 2 cm · 높이 2 cm', 14.5, MUTE)
    b += t(162, 236, '부피 16 cm³ · 표면적 40 cm²', 16)
    b += t(162, 270, '표면적 ÷ 부피 = 2.5', 18, B, weight='700')
    b += panel(345, 10, 305, 300, '자른 뒤: 작은 조각 2개')
    b += box3d(372, 95, 80, 80, 80) + box3d(498, 95, 80, 80, 80)
    b += t(497, 200, '한 변 2 cm 정육면체 2개', 14.5, MUTE)
    b += t(497, 236, '부피 16 cm³ · 표면적 48 cm²', 16)
    b += t(497, 270, '표면적 ÷ 부피 = 3', 18, R, weight='700')
    b += t(330, 345, '전체 부피는 같아도, 작게 나누면 바깥과 닿는 면이 넓어져 물질 교환에 유리하다.', 16, INK, weight='700')
    return svg(660, 362, b)


# ---- 2. 세포 → 염색체 → DNA·유전자 ----------------------------------------
def fig_chromosome():
    b = panel(10, 10, 190, 280, '세포와 핵', '핵 속에|유전 물질이 있다')
    b += cell(105, 130, 72, 68) + nucleus(105, 130, 36) + threads(105, 130, 32)
    b += arrow(205, 150, 236, 150)
    b += panel(240, 10, 190, 280, '분열할 때의 염색체', '두 가닥의|염색 분체')
    b += xch(335, 130, 150, B, 24)
    b += t(278, 88, '염색', 14, MUTE) + t(278, 105, '분체', 14, MUTE)
    b += t(394, 88, '염색', 14, MUTE) + t(394, 105, '분체', 14, MUTE)
    b += arrow(435, 150, 466, 150)
    b += panel(470, 10, 190, 280, 'DNA와 유전자', 'DNA의 각 유전 정보가|유전자')
    # 이중 나선 느낌의 띠
    for k in range(0, 13):
        y = 56 + k * 14
        off = 26 * math.sin(k * 0.72)
        col = '#9fb4cc'
        b += f'<line x1="{565-off:.1f}" y1="{y}" x2="{565+off:.1f}" y2="{y}" stroke="{col}" stroke-width="2.4"/>'
    p1 = ' '.join(f'{565 + 26 * math.sin(k * 0.24):.1f},{56 + k * 14 / 3:.1f}' for k in range(0, 37))
    p2 = ' '.join(f'{565 - 26 * math.sin(k * 0.24):.1f},{56 + k * 14 / 3:.1f}' for k in range(0, 37))
    b += f'<polyline points="{p1}" fill="none" stroke="#2f6fd0" stroke-width="3"/>'
    b += f'<polyline points="{p2}" fill="none" stroke="#17a398" stroke-width="3"/>'
    b += f'<rect x="530" y="96" width="70" height="46" fill="none" stroke="{R}" stroke-width="2.5" stroke-dasharray="6 4"/>'
    b += t(633, 124, '유전자', 14.5, R, weight='700')
    return svg(670, 300, b)


# ---- 3. 체세포 분열 ---------------------------------------------------------
def fig_mitosis():
    W, H = 212, 244
    names = [('① 간기(분열 전)', 'DNA가 복제된다|(염색체는 실처럼 풀어짐)'),
             ('② 전기', '핵막이 사라지고|막대 모양 염색체가 나타남'),
             ('③ 중기', '염색체가 세포|가운데에 배열'),
             ('④ 후기', '염색 분체가 분리되어|양쪽 끝으로 이동'),
             ('⑤ 말기·세포질 분열', '핵막이 나타나고|세포질이 나누어짐'),
             ('⑥ 딸세포 2개', '모세포와 염색체 수와|유전 정보가 같음')]
    b = ''
    for i, (n, note) in enumerate(names):
        x = 10 + (i % 3) * (W + 12)
        y = 10 + (i // 3) * (H + 12)
        b += panel(x, y, W, H, n, note)
        cx, cy = x + W / 2, y + 108
        if i == 0:
            b += cell(cx, cy, 68) + nucleus(cx, cy, 36) + threads(cx, cy, 32)
        elif i == 1:
            b += cell(cx, cy, 68) + nucleus(cx, cy, 46, True)
            b += xch(cx - 21, cy - 14, 36, B) + xch(cx + 21, cy - 14, 36, B)
            b += xch(cx - 16, cy + 23, 24, R) + xch(cx + 16, cy + 23, 24, R)
        elif i == 2:
            b += cell(cx, cy, 68)
            b += f'<line x1="{cx}" y1="{cy-62}" x2="{cx}" y2="{cy+62}" stroke="{LINE}" stroke-width="2" stroke-dasharray="5 5"/>'
            for dy, h, c in [(-42, 28, B), (-12, 28, B), (17, 20, R), (41, 20, R)]:
                b += xch(cx, cy + dy, h, c)
        elif i == 3:
            b += cell(cx, cy, 78, 64)
            for dy, h, c in [(-42, 28, B), (-12, 28, B), (17, 20, R), (41, 20, R)]:
                b += chromatid(cx - 36, cy + dy, h, c, -1) + chromatid(cx + 36, cy + dy, h, c, 1)
            b += arrow(cx - 8, cy, cx - 22, cy, MUTE, 2) + arrow(cx + 8, cy, cx + 22, cy, MUTE, 2)
        elif i == 4:
            b += (f'<path d="M{cx-4},{cy-48} C{cx-40},{cy-72} {cx-92},{cy-48} {cx-92},{cy} '
                  f'C{cx-92},{cy+48} {cx-40},{cy+72} {cx-4},{cy+48} C{cx-10},{cy+20} {cx-10},{cy-20} {cx-4},{cy-48}Z" '
                  f'fill="{CELL}" stroke="{CELLS}" stroke-width="2.5"/>')
            b += (f'<path d="M{cx+4},{cy-48} C{cx+40},{cy-72} {cx+92},{cy-48} {cx+92},{cy} '
                  f'C{cx+92},{cy+48} {cx+40},{cy+72} {cx+4},{cy+48} C{cx+10},{cy+20} {cx+10},{cy-20} {cx+4},{cy-48}Z" '
                  f'fill="{CELL}" stroke="{CELLS}" stroke-width="2.5"/>')
            for sx in (-1, 1):
                nx = cx + sx * 50
                b += nucleus(nx, cy, 30)
                b += bar(nx - 11, cy - 4, 26, B, 10, 6) + bar(nx + 11, cy - 4, 26, B, -10, 6)
                b += bar(nx - 6, cy + 13, 16, R, 70, 6) + bar(nx + 8, cy + 14, 16, R, -60, 6)
        else:
            for sx in (-1, 1):
                nx = cx + sx * 50
                b += cell(nx, cy, 46) + nucleus(nx, cy, 28)
                b += bar(nx - 10, cy - 4, 26, B, 10, 6) + bar(nx + 10, cy - 4, 26, B, -10, 6)
                b += bar(nx - 6, cy + 13, 16, R, 70, 6) + bar(nx + 8, cy + 14, 16, R, -60, 6)
    return svg(10 + 3 * (W + 12), 2 * (H + 12) + 10, b)


# ---- 4. 상동 염색체 --------------------------------------------------------
def fig_homolog():
    b = panel(10, 10, 300, 260, '상동 염색체 한 쌍', '모양과 크기가 같고|부모에게서 하나씩 받음')
    b += xch(95, 112, 110, B, 18) + xch(225, 112, 110, B, 18)
    b += t(95, 192, '아버지에게서', 14.5, INK, weight='700') + t(225, 192, '어머니에게서', 14.5, INK, weight='700')
    b += panel(330, 10, 300, 260, '같은 위치의 대립유전자', '상동 염색체의 같은 위치에|같은 형질의 유전자가 있음')
    b += bar(430, 120, 130, B, 0, 18) + bar(530, 120, 130, B, 0, 18)
    b += f'<rect x="418" y="86" width="24" height="16" fill="#fff" stroke="{INK}"/>'
    b += f'<rect x="518" y="86" width="24" height="16" fill="#fff" stroke="{INK}"/>'
    b += t(430, 99, 'A', 14, INK, weight='700') + t(530, 99, 'a', 14, INK, weight='700')
    b += t(480, 84, '같은 위치', 14, MUTE)
    b += t(480, 104, '대립유전자', 14, MUTE)
    return svg(640, 280, b)


def band(x, y, w, ang=0):
    return f'<rect x="{x-w/2:.1f}" y="{y-3:.1f}" width="{w:.1f}" height="6" fill="#222" transform="rotate({ang} {x:.1f} {y})"/>'


def tagged_x(x, y, h, w, color, genes, t_=13):
    """X자 염색체의 두 가닥 같은 높이에 유전자를 표시한다. genes: [(높이, 글자)]"""
    s = xch(x, y, h, color, w, t_)
    d = w * 0.46
    tan = math.tan(math.radians(t_))
    for dy, g in genes:
        off = d + abs(dy) * tan
        ang = t_ if dy < 0 else -t_
        s += band(x - off, y + dy, w * 1.02, ang) + band(x + off, y + dy, w * 1.02, -ang)
        s += t(x - off - w - 3, y + dy + 7, g, 20, INK, weight='700')
        s += t(x + off + w + 3, y + dy + 7, g, 20, INK, weight='700')
    return s


def fig_pair():
    """한 쌍의 상동 염색체와 대립유전자 A, a"""
    b = tagged_x(120, 112, 170, 22, B, [(-40, 'A')])
    b += tagged_x(300, 112, 170, 22, B, [(-40, 'a')])
    b += t(120, 226, '(가)', 19, INK, weight='700') + t(300, 226, '(나)', 19, INK, weight='700')
    return svg(420, 240, b)


def fig_sister():
    """간기 복제와 상동 염색체의 유전자 구성"""
    def half(ox, title, genes):
        s = panel(ox, 10, 335, 268, title)
        cx, cy = ox + 62, 150
        s += bar(cx, cy, 170, B, 0, 22)
        for dy, g in genes:
            s += band(cx, cy + dy, 22)
            s += t(cx - 26, cy + dy + 7, g, 20, INK, weight='700')
        s += arrow(ox + 100, cy, ox + 160, cy)
        s += t(ox + 128, cy - 26, '간기', 15, INK, weight='700') + t(ox + 128, cy - 8, 'DNA 복제', 13.5, MUTE)
        s += tagged_x(ox + 246, cy, 190, 22, B, genes)
        return s
    b = half(10, '아버지에게서 받은 염색체', [(-58, 'A'), (-26, 'B'), (52, 'd')])
    b += half(355, '어머니에게서 받은 염색체', [(-58, 'a'), (-26, 'B'), (52, 'D')])
    b += t(350, 306, '염색 분체끼리: 복제로 생겨서 유전자 구성이 완전히 같다.', 16, INK, weight='700')
    b += t(350, 332, '상동 염색체끼리: 같은 위치에 같은 형질의 유전자가 있지만, A와 a처럼 다를 수 있다.', 16, INK, weight='700')
    return svg(700, 346, b)


# ---- 5. 감수 분열 -----------------------------------------------------------
def fig_meiosis():
    b = f'<rect x="10" y="10" width="760" height="262" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
    b += t(30, 38, '감수 1분열: 상동 염색체가 결합했다가 분리된다', 18, INK, 'start', '700')
    cols = [95, 270, 450, 655]
    labels = [('전기', '상동 염색체가 결합'), ('중기', '결합한 상동 염색체가|가운데에 배열'), ('후기', '상동 염색체가|양쪽으로 분리'), ('결과', '딸세포 2개|염색체 수 절반')]
    cy = 144
    x = cols[0]
    b += cell(x, cy, 66) + xch(x - 26, cy - 14, 40, B) + xch(x - 2, cy - 14, 40, B)
    b += xch(x + 14, cy + 26, 26, R) + xch(x + 32, cy + 26, 26, R)
    x = cols[1]
    b += cell(x, cy, 66)
    b += f'<line x1="{x}" y1="{cy-60}" x2="{x}" y2="{cy+60}" stroke="{LINE}" stroke-width="2" stroke-dasharray="5 5"/>'
    b += xch(x - 13, cy - 24, 40, B) + xch(x + 13, cy - 24, 40, B)
    b += xch(x - 10, cy + 26, 26, R) + xch(x + 10, cy + 26, 26, R)
    x = cols[2]
    b += cell(x, cy, 72, 62)
    b += xch(x - 40, cy - 24, 40, B) + xch(x + 40, cy - 24, 40, B)
    b += xch(x - 40, cy + 26, 26, R) + xch(x + 40, cy + 26, 26, R)
    b += arrow(x - 8, cy, x - 22, cy, MUTE, 2) + arrow(x + 8, cy, x + 22, cy, MUTE, 2)
    x = cols[3]
    for nx in (x - 46, x + 46):
        b += cell(nx, cy, 42) + xch(nx - 11, cy, 40, B) + xch(nx + 14, cy, 26, R)
    for c, (n, note) in zip(cols, labels):
        b += t(c, 66, n, 16, INK, weight='700')
        for i, line in enumerate(note.split('|')):
            b += t(c, 232 + i * 20, line, 14.5, MUTE)
    b += arrow(167, cy, 198, cy) + arrow(342, cy, 372, cy) + arrow(528, cy, 561, cy)
    y0 = 284
    b += f'<rect x="10" y="{y0}" width="760" height="262" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
    b += t(30, y0 + 28, '감수 2분열: DNA 복제 없이 염색 분체가 분리된다', 18, INK, 'start', '700')
    cy = y0 + 118
    for nx in (70, 150):
        b += cell(nx, cy, 37)
        b += f'<line x1="{nx}" y1="{cy-33}" x2="{nx}" y2="{cy+33}" stroke="{LINE}" stroke-width="2" stroke-dasharray="4 4"/>'
        b += xch(nx, cy - 12, 30, B) + xch(nx, cy + 17, 20, R)
    for nx in (300, 388):
        b += cell(nx, cy, 42, 40)
        b += chromatid(nx - 19, cy - 12, 28, B, -1) + chromatid(nx + 19, cy - 12, 28, B, 1)
        b += chromatid(nx - 16, cy + 17, 18, R, -1) + chromatid(nx + 16, cy + 17, 18, R, 1)
    for nx in (540, 602, 664, 726):
        b += cell(nx, cy, 28)
        b += bar(nx - 7, cy - 2, 26, B, 8, 6) + bar(nx + 9, cy + 3, 16, R, -8, 6)
    b += t(110, y0 + 54, '중기', 16, INK, weight='700')
    b += t(344, y0 + 54, '후기', 16, INK, weight='700')
    b += t(633, y0 + 54, '딸세포 4개', 16, INK, weight='700')
    b += t(110, y0 + 204, '염색체가', 14.5, MUTE) + t(110, y0 + 224, '가운데에 배열', 14.5, MUTE)
    b += t(344, y0 + 204, '각 염색체의 염색 분체가', 14.5, MUTE) + t(344, y0 + 224, '양쪽으로 분리', 14.5, MUTE)
    b += t(633, y0 + 204, '염색체 수가 모세포의 절반인', 14.5, MUTE) + t(633, y0 + 224, '생식세포(정자 또는 난자)가 된다', 14.5, MUTE)
    b += arrow(194, cy, 250, cy) + arrow(436, cy, 502, cy)
    return svg(780, 556, b)


# ---- 6. 발생 ---------------------------------------------------------------
def egg(x, y, r, n):
    s = f'<circle cx="{x}" cy="{y}" r="{r}" fill="{CELL}" stroke="{CELLS}" stroke-width="2.5"/>'
    if n == 2:
        s += f'<line x1="{x}" y1="{y-r}" x2="{x}" y2="{y+r}" stroke="{CELLS}" stroke-width="2"/>'
    elif n == 4:
        s += f'<line x1="{x}" y1="{y-r}" x2="{x}" y2="{y+r}" stroke="{CELLS}" stroke-width="2"/>'
        s += f'<line x1="{x-r}" y1="{y}" x2="{x+r}" y2="{y}" stroke="{CELLS}" stroke-width="2"/>'
    elif n > 4:
        for gy in range(-3, 4):
            for gx in range(-3, 4):
                px, py = x + gx * r / 3.4, y + gy * r / 3.4
                if (px - x) ** 2 + (py - y) ** 2 < (r * 0.88) ** 2:
                    s += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r/7.5:.1f}" fill="#f3e6c4" stroke="{CELLS}" stroke-width="1.2"/>'
    return s


def fig_development():
    b = f'<rect x="10" y="10" width="760" height="230" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
    # 정자+난자
    b += f'<circle cx="82" cy="108" r="36" fill="#fbe3d3" stroke="{R}" stroke-width="2.5"/>'
    b += f'<circle cx="32" cy="70" r="7" fill="{B}"/><path d="M26,66 q-6,-10 -2,-20" fill="none" stroke="{B}" stroke-width="2.4"/>'
    b += arrow(40, 76, 54, 88, B, 2)
    b += t(82, 172, '난자 + 정자', 15, INK, weight='700') + t(82, 192, '각각 23개', 14.5, MUTE)
    b += arrow(124, 108, 158, 108)
    xs = [(208, 40, 1, '수정란', '46개'), (320, 40, 2, '2세포', ''), (428, 40, 4, '4세포', ''), (540, 40, 9, '세포 수 증가', '세포는 작아짐')]
    for x, r, n, a, c in xs:
        b += egg(x, 108, r, n)
        b += t(x, 172, a, 15, INK, weight='700')
        if c:
            b += t(x, 192, c, 14.5, MUTE)
    for (a, _, _, _, _), (c, _, _, _, _) in zip(xs, xs[1:]):
        b += arrow(a + 46, 108, c - 46, 108)
    b += f'<line x1="264" y1="216" x2="590" y2="216" stroke="{B}" stroke-width="3"/>'
    b += t(427, 232, '난할: 딸세포가 자라지 않고 빠르게 분열', 15, B, weight='700')
    b += arrow(586, 108, 628, 108)
    # 개체(사람 실루엣 대신 단순 기호)
    b += f'<circle cx="692" cy="66" r="20" fill="{CELL}" stroke="{CELLS}" stroke-width="2.5"/>'
    b += f'<rect x="668" y="90" width="48" height="56" rx="20" fill="{CELL}" stroke="{CELLS}" stroke-width="2.5"/>'
    b += t(692, 172, '개체', 15, INK, weight='700') + t(692, 192, '조직·기관 형성', 14.5, MUTE)
    return svg(780, 250, b)


# ---- 7. 한 가지 형질 --------------------------------------------------------
def pea(x, y, color, r=17, wrinkled=False):
    fill = {'y': '#f2c81e', 'g': '#6fae3d'}[color]
    edge = {'y': '#b08f00', 'g': '#3f7a1d'}[color]
    if wrinkled:
        pts = []
        for k in range(24):
            a = k / 24 * 2 * math.pi
            rr = r * (1 + 0.14 * (1 if k % 2 else -1))
            pts.append(f'{x + rr * math.cos(a):.1f},{y + rr * math.sin(a):.1f}')
        return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{edge}" stroke-width="1.6"/>'
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{edge}" stroke-width="1.6"/>'


def fig_monohybrid():
    b = f'<rect x="10" y="10" width="330" height="420" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
    b += t(30, 40, '어버이', 16, INK, 'start', '700')
    b += pea(120, 74, 'y') + t(120, 112, 'YY', 16, INK, weight='700')
    b += pea(240, 74, 'g') + t(240, 112, 'yy', 16, INK, weight='700')
    b += t(180, 80, '×', 22)
    b += t(120, 134, '생식세포 Y', 14.5, MUTE) + t(240, 134, '생식세포 y', 14.5, MUTE)
    b += arrow(180, 144, 180, 176)
    b += t(30, 208, '자손 1대', 16, INK, 'start', '700')
    b += pea(180, 214, 'y') + t(180, 254, 'Yy (모두 노란색)', 16, INK, weight='700')
    b += t(180, 276, '초록색은 나타나지 않음 → 노란색이 우성', 14.5, MUTE)
    b += arrow(180, 288, 180, 320)
    b += t(180, 340, '자가 수분', 14.5, MUTE)
    b += t(30, 372, '자손 2대', 16, INK, 'start', '700')
    b += t(180, 394, '노란색 : 초록색 ≈ 3 : 1', 17, INK, weight='700')
    b += t(180, 416, 'YY : Yy : yy = 1 : 2 : 1', 15.5, MUTE)
    # 펀넷
    x0, y0, s = 420, 120, 96
    b += f'<rect x="352" y="10" width="298" height="420" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
    b += t(500, 40, 'Yy × Yy 의 결과', 16, INK, weight='700')
    b += t(500, 64, '쌍이 분리되어 Y, y 가 1 : 1로 만들어진다', 13.5, MUTE)
    b += t(x0 + s / 2, y0 - 12, 'Y', 18, INK, weight='700') + t(x0 + s * 1.5, y0 - 12, 'y', 18, INK, weight='700')
    b += t(x0 - 22, y0 + s / 2 + 6, 'Y', 18, INK, weight='700') + t(x0 - 22, y0 + s * 1.5 + 6, 'y', 18, INK, weight='700')
    cells = [('YY', 'y'), ('Yy', 'y'), ('Yy', 'y'), ('yy', 'g')]
    for k, (g, c) in enumerate(cells):
        cx, cy = x0 + (k % 2) * s, y0 + (k // 2) * s
        b += f'<rect x="{cx}" y="{cy}" width="{s}" height="{s}" fill="#fff" stroke="{MUTE}" stroke-width="1.5"/>'
        b += pea(cx + s / 2, cy + 36, c, 18) + t(cx + s / 2, cy + 80, g, 17, INK, weight='700')
    b += t(500, 336, '왼쪽 Y·y: 한쪽 어버이의 생식세포', 13.5, MUTE)
    b += t(500, 356, '위쪽 Y·y: 다른 쪽 어버이의 생식세포', 13.5, MUTE)
    b += t(500, 392, '노란색 3칸 : 초록색 1칸', 16, INK, weight='700')
    return svg(660, 440, b)


# ---- 8. 두 가지 형질 --------------------------------------------------------
def fig_dihybrid():
    gam = ['RY', 'Ry', 'rY', 'ry']
    x0, y0, s = 74, 92, 104
    b = t(290, 28, 'RrYy 끼리 자가 수분했을 때 (자손 2대)', 18, INK, weight='700')
    b += t(290, 52, '생식세포 4종류가 1 : 1 : 1 : 1로 만들어져 16칸이 나온다', 14.5, MUTE)
    for i, g in enumerate(gam):
        b += t(x0 + i * s + s / 2, y0 - 12, g, 17, INK, weight='700')
        b += t(x0 - 30, y0 + i * s + s / 2 + 6, g, 17, INK, weight='700')
    for r_, a in enumerate(gam):
        for c_, c in enumerate(gam):
            g = a + c
            rr = ''.join(sorted([a[0], c[0]]))     # 대문자 먼저
            yy = ''.join(sorted([a[1], c[1]]))
            round_ = 'R' in rr
            yellow = 'Y' in yy
            bg = {(True, True): '#fff7d6', (True, False): '#e6f3da', (False, True): '#fde7cf', (False, False): '#e2e8f0'}[(round_, yellow)]
            cx, cy = x0 + c_ * s, y0 + r_ * s
            b += f'<rect x="{cx}" y="{cy}" width="{s}" height="{s}" fill="{bg}" stroke="{MUTE}" stroke-width="1.2"/>'
            b += pea(cx + s / 2, cy + 38, 'y' if yellow else 'g', 19, not round_)
            b += t(cx + s / 2, cy + 86, rr + yy, 15.5, INK, weight='600')
    y = y0 + 4 * s + 34
    items = [('#fff7d6', '둥글고 노란색 9'), ('#e6f3da', '둥글고 초록색 3'), ('#fde7cf', '주름지고 노란색 3'), ('#e2e8f0', '주름지고 초록색 1')]
    for i, (c, s_) in enumerate(items):
        x = 20 + (i % 2) * 280
        yy = y + (i // 2) * 30
        b += f'<rect x="{x}" y="{yy-16}" width="20" height="20" fill="{c}" stroke="{MUTE}"/>' + t(x + 28, yy, s_, 16, INK, 'start', '600')
    b += t(290, y + 66, '모양만 보면 둥근 12 : 주름진 4 = 3 : 1, 색만 보면 노란 12 : 초록 4 = 3 : 1', 14.5, B, weight='700')
    return svg(520 + 60, y + 82, b)


# ---- 9. 가계도 --------------------------------------------------------------
def person(x, y, sex, on, label='', s=38):
    fill = '#39485a' if on else '#fff'
    if sex == 'm':
        shape = f'<rect x="{x-s/2}" y="{y-s/2}" width="{s}" height="{s}" fill="{fill}" stroke="{INK}" stroke-width="2.2"/>'
    else:
        shape = f'<circle cx="{x}" cy="{y}" r="{s/2}" fill="{fill}" stroke="{INK}" stroke-width="2.2"/>'
    return shape + (t(x, y + s / 2 + 20, label, 15, B, weight='700') if label else '')


def ln(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="2"/>'


def fig_pedigree():
    b = f'<rect x="10" y="10" width="430" height="320" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
    # 1세대
    b += ln(150, 70, 300, 70) + ln(225, 70, 225, 128)
    b += person(150, 70, 'm', False, 'Tt') + person(300, 70, 'f', False, 'Tt')
    # 2세대
    b += ln(110, 128, 340, 128)
    for x in (110, 225, 340):
        b += ln(x, 128, x, 150)
    b += person(110, 168, 'm', False, 'TT 또는 Tt') + person(225, 168, 'f', True, 'tt') + person(340, 168, 'm', False, 'TT 또는 Tt')
    b += ln(225, 168, 310, 168) if False else ''
    b += t(225, 262, '부모에게 없던 형질(■●)이 자녀에게 나타남', 15, INK, weight='700')
    b += t(225, 284, '→ 그 형질이 열성, 부모의 형질이 우성', 15, INK, weight='700')
    b += t(225, 308, '열성인 자녀(tt)가 있으므로 부모는 모두 Tt', 14.5, MUTE)
    # 범례
    b += f'<rect x="456" y="10" width="194" height="320" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
    b += t(553, 40, '가계도 읽는 법', 16, INK, weight='700')
    b += person(492, 80, 'm', False, s=26) + t(516, 86, '남자', 15, INK, 'start')
    b += person(492, 122, 'f', False, s=26) + t(516, 128, '여자', 15, INK, 'start')
    b += person(492, 164, 'm', True, s=26) + person(530, 164, 'f', True, s=26) + t(554, 170, '다른 형질', 15, INK, 'start')
    b += ln(476, 208, 530, 208) + t(540, 214, '부부', 15, INK, 'start')
    b += ln(503, 240, 503, 272) + t(516, 262, '자녀', 15, INK, 'start')
    b += t(553, 304, '같은 줄 = 같은 세대', 14, MUTE)
    return svg(660, 340, b)


# ---- 10. 1란성 쌍둥이 -------------------------------------------------------
def fig_twin():
    b = f'<rect x="10" y="10" width="640" height="210" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
    b += egg(80, 110, 40, 1) + t(80, 176, '수정란 1개', 15, INK, weight='700')
    b += arrow(126, 110, 164, 110)
    b += egg(216, 110, 40, 4) + t(216, 176, '난할 중', 15, INK, weight='700')
    b += arrow(258, 96, 312, 66) + arrow(258, 124, 312, 154)
    b += t(285, 118, '나뉨', 14.5, MUTE, 'start')
    b += egg(358, 62, 30, 4) + egg(358, 158, 30, 4)
    b += arrow(394, 62, 436, 62) + arrow(394, 158, 436, 158)
    b += t(540, 56, '유전자 구성이 같다', 16, INK, weight='700')
    b += t(540, 80, '→ 같은 유전자에서 시작', 14.5, MUTE)
    b += t(540, 140, '차이가 크면 환경의 영향', 16, R, weight='700')
    b += t(540, 164, '비슷하면 유전의 영향이 큼', 16, B, weight='700')
    return svg(660, 230, b)


# ---- 11. 동전 모의 활동 -----------------------------------------------------
def coin(x, y, g, c):
    return (f'<circle cx="{x}" cy="{y}" r="34" fill="#fbe9a9" stroke="#b08f00" stroke-width="3"/>'
            + t(x, y + 9, g, 26, c, weight='700'))


def fig_coin():
    b = f'<rect x="10" y="10" width="640" height="220" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
    b += t(120, 42, '아버지 동전', 15.5, B, weight='700') + t(120, 62, '양면에 A, a', 14.5, MUTE)
    b += coin(120, 110, 'A', B)
    b += t(330, 42, '어머니 동전', 15.5, R, weight='700') + t(330, 62, '양면에 A, a', 14.5, MUTE)
    b += coin(330, 110, 'a', R)
    b += t(225, 118, '+', 28)
    b += arrow(380, 110, 440, 110)
    b += t(535, 92, '자녀의 유전자형', 15.5, INK, weight='700')
    b += t(535, 128, 'Aa', 30, INK, weight='700')
    b += t(225, 178, '동전의 위쪽 면 = 생식세포에 들어간 대립유전자', 15, INK, weight='700')
    b += t(225, 202, '두 동전을 합치는 것 = 수정', 15, INK, weight='700')
    b += t(535, 190, '던질 때마다 달라질 수 있다', 14.5, MUTE)
    return svg(660, 240, b)


# ---- 12. 가계도 확률 (Tt × Tt) ---------------------------------------------
def fig_prob():
    b = f'<rect x="10" y="10" width="640" height="330" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
    b += t(330, 40, '혀를 말 수 있는 부모(Tt × Tt)에게서 태어날 자녀', 17, INK, weight='700')
    x0, y0, s = 96, 92, 96
    b += t(x0 + s, y0 - 30, '어머니의 생식세포', 13.5, R, weight='700')
    b += t(x0 + s / 2, y0 - 10, 'T', 18, R, weight='700') + t(x0 + s * 1.5, y0 - 10, 't', 18, R, weight='700')
    b += t(x0 - 46, y0 + s, '아버지', 13.5, B, weight='700')
    b += t(x0 - 18, y0 + s / 2 + 6, 'T', 18, B, weight='700') + t(x0 - 18, y0 + s * 1.5 + 6, 't', 18, B, weight='700')
    for k, (g, on) in enumerate([('TT', False), ('Tt', False), ('Tt', False), ('tt', True)]):
        cx, cy = x0 + (k % 2) * s, y0 + (k // 2) * s
        b += f'<rect x="{cx}" y="{cy}" width="{s}" height="{s}" fill="{"#e2e8f0" if on else "#fff"}" stroke="{MUTE}" stroke-width="1.5"/>'
        b += person(cx + s / 2, cy + 36, 'm' if k % 2 == 0 else 'f', on, s=30) + t(cx + s / 2, cy + 82, g, 17, INK, weight='700')
    x = 330
    b += t(x, 112, '유전자형  TT : Tt : tt = 1 : 2 : 1', 16, INK, 'start', '700')
    b += t(x, 150, '혀를 말 수 있음(우성) 3칸', 15.5, INK, 'start') + t(620, 150, '→ 3/4', 17, B, 'end', '700')
    b += t(x, 184, '혀를 말 수 없음(열성) 1칸', 15.5, INK, 'start') + t(620, 184, '→ 1/4', 17, R, 'end', '700')
    b += t(x, 232, '아이를 낳을 때마다 확률은 같다.', 15, INK, 'start', '700')
    b += t(x, 256, '첫째가 열성(tt)이어도 둘째가', 14.5, MUTE, 'start')
    b += t(x, 278, '열성일 확률은 그대로 1/4이다.', 14.5, MUTE, 'start')
    b += t(330, 324, '■ ● : 혀를 말 수 없음(열성)   □ ○ : 혀를 말 수 있음(우성)', 13.5, MUTE)
    return svg(660, 350, b)


# ---- 13. 열성 순종과의 교배 (RrYy × rryy) -----------------------------------
def fig_testcross():
    gam = [('RY', 'y', False), ('Ry', 'g', False), ('rY', 'y', True), ('ry', 'g', True)]
    b = f'<rect x="10" y="10" width="640" height="372" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
    b += t(330, 40, 'RrYy × rryy 의 결과', 17, INK, weight='700')
    b += t(330, 64, 'RrYy는 생식세포 4종류(1 : 1 : 1 : 1), rryy는 ry 한 종류만 만든다', 14, MUTE)
    x0, y0, s = 150, 112, 112
    b += t(x0 - 70, y0 - 12, 'RrYy →', 15, INK, 'start', '700')
    b += t(x0 - 70, y0 + 60, 'rryy', 15, INK, 'start', '700') + t(x0 - 70, y0 + 80, '↓ ry', 15, INK, 'start', '700')
    for i, (g, c, w) in enumerate(gam):
        cx = x0 + i * s
        b += t(cx + s / 2, y0 - 12, g, 17, INK, weight='700')
        child = g[0] + 'r' + g[1] + 'y'
        child = ''.join(sorted(child[:2])) + ''.join(sorted(child[2:]))
        b += f'<rect x="{cx}" y="{y0}" width="{s}" height="{s}" fill="#fff" stroke="{MUTE}" stroke-width="1.5"/>'
        b += pea(cx + s / 2, y0 + 40, c, 20, w) + t(cx + s / 2, y0 + 88, child, 16, INK, weight='700')
    names = ['둥글고 노란색', '둥글고 초록색', '주름지고 노란색', '주름지고 초록색']
    for i, n in enumerate(names):
        b += t(x0 + i * s + s / 2, y0 + s + 24, n, 13, MUTE)
    b += t(330, 284, '표현형의 비 = 1 : 1 : 1 : 1  (각각 1/4)', 17, INK, weight='700')
    b += t(330, 314, '모양만: Rr × rr → 둥근 : 주름진 = 1 : 1', 14.5, B, weight='700')
    b += t(330, 338, '색만: Yy × yy → 노란색 : 초록색 = 1 : 1', 14.5, B, weight='700')
    b += t(330, 364, '1/2 × 1/2 = 1/4 이므로 네 가지가 같은 비율로 나온다', 14, MUTE)
    return svg(660, 392, b)


FIGS = {
    'agar': fig_agar, 'chromosome': fig_chromosome, 'mitosis': fig_mitosis, 'homolog': fig_homolog,
    'meiosis': fig_meiosis, 'pair': fig_pair, 'sister': fig_sister, 'development': fig_development, 'monohybrid': fig_monohybrid,
    'dihybrid': fig_dihybrid, 'pedigree': fig_pedigree, 'twin': fig_twin, 'coin': fig_coin,
    'prob': fig_prob, 'testcross': fig_testcross,
}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for k, f in FIGS.items():
        with open(os.path.join(OUT, f'g_{k}.svg'), 'w', encoding='utf8') as fp:
            fp.write(f())
    print(len(FIGS), 'figures')
