"""Convertit un chapitre markdown heterogene en markdown homogene.

Usage : python -I homogeniser.py source/3b.md markdown/3b.md rapports/3b.txt

Syntaxe produite (voir ../SYNTAXE.md) :
  segments   ::: jing | comm | note  ... :::   avec lignes  zh: / py: / fr:
  annotation {sy:... | zh:... | py:... | fr:...}   (parenthese, masquable)
  terme      {{sy:... | zh:... | py:...}}          (mot du texte, jamais vide)
"""
import re, sys, io, unicodedata

HAN = '㐀-鿿豈-﫿'
CJKP = '　-〿＀-￯…·《》“”'
HEXA = '䷀-䷿'
TRI = '☰-☷⚊-⚏⚀-⚃'
RE_HAN = re.compile('[' + HAN + ']')
SYMS = re.compile('[' + HEXA + TRI + ']')

# --- syllabes pinyin -------------------------------------------------------
FINALS = ('a o e ai ei ao ou an en ang eng ong i ia ie iao iu ian in iang ing iong '
          'u ua uo uai ui uan un uang ueng v ve van vn er').split()
INITIALS = ['', 'b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q', 'x',
            'zh', 'ch', 'sh', 'r', 'z', 'c', 's', 'y', 'w']
SYL = set()
for i in INITIALS:
    for f in FINALS:
        SYL.add(i + f)
SYL |= {'zhi', 'chi', 'shi', 'ri', 'zi', 'ci', 'si', 'yu', 'yue', 'yuan', 'yun', 'lve', 'nve'}
SYL -= {'bv', 'pv', 'mv', 'fv'}


def strip_tones(w):
    w = w.replace('ü', 'v').replace('Ü', 'v')
    w = ''.join(c for c in unicodedata.normalize('NFD', w) if unicodedata.category(c) != 'Mn')
    return w.lower().replace('u:', 'v')


def segmentable(w):
    w = strip_tones(w)
    if not w or not w.isalpha():
        return False
    ok = [True] + [False] * len(w)
    for i in range(len(w)):
        if ok[i]:
            for j in range(i + 1, min(len(w), i + 6) + 1):
                if w[i:j] in SYL:
                    ok[j] = True
    return ok[len(w)]


TONE = re.compile('[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜĀÁǍÀĒÉĚÈĪÍǏÌŌÓǑÒŪÚǓÙ]')
WORD = re.compile("[A-Za-zÀ-ÿĀ-ſǍ-ǜ]+")


def is_pinyin(s, need_tone=False):
    words = [w for w in WORD.findall(s.replace("'", ' ').replace('’', ' ').replace('-', ' '))]
    if not words:
        return False
    good = sum(segmentable(w) for w in words)
    if good / len(words) < 0.95:
        return False
    return bool(TONE.search(s)) or not need_tone


# --- champs d'annotation ---------------------------------------------------
def fields(content):
    """Decoupe le contenu d'une parenthese en champs sy/zh/py/fr."""
    c = content.replace('**', '').replace('_', '').replace('*', '').strip()
    out = {'sy': [], 'zh': [], 'py': [], 'fr': []}
    pieces = re.split(r'\s*[,;]\s+|\s+[-–—]\s+|\s*,(?=\S)', c)
    for p in pieces:
        p = p.strip()
        if not p:
            continue
        # symboles en tete
        m = re.match('([' + HEXA + TRI + r'\s]+)', p)
        if m and SYMS.search(m.group(1)):
            out['sy'].append(re.sub(r'\s+', '', m.group(1)))
            p = p[m.end():].strip()
        if not p:
            continue
        # pinyin puis caracteres (ordre des chapitres 00 et 1a)
        m = re.match(r"([^" + HAN + r"]+?)\s+([" + HAN + '][' + HAN + CJKP + r'\s]*)$', p)
        if m and not out['zh'] and is_pinyin(m.group(1)):
            out['py'].append(m.group(1).strip()); out['zh'].append(m.group(2).strip())
            continue
        m = re.match('([' + HAN + CJKP + r'\s.]*[' + HAN + '][' + HAN + CJKP + ']*)(.*)$', p)
        if m and not out['zh']:
            out['zh'].append(m.group(1).strip())
            rest = m.group(2).strip()
            if rest:
                if is_pinyin(rest) and not out['py']:
                    out['py'].append(rest)
                else:
                    out['fr'].append(rest)
            continue
        m = re.search('[' + HEXA + TRI + ']$', p)
        if m and is_pinyin(p[:-1]) and not out['py']:
            out['py'].append(p[:-1].strip()); out['sy'].append(m.group(0)); continue
        if not RE_HAN.search(p) and is_pinyin(p) and (not out['py'] or (TONE.search(p) and not out['fr'])):
            out['py'].append(p)
        else:
            out['fr'].append(p)
    return out


def fmt(f, double=False):
    parts = []
    for k in ('sy', 'zh', 'py', 'fr'):
        if f[k]:
            v = (' ' if k == 'sy' else ', ').join(x.replace('**', '').strip('_* ') for x in f[k])
            parts.append(k + ':' + v.replace('|', '/').replace('}', ')').replace('{', '('))
    body = ' | '.join(parts)
    return '{{' + body + '}}' if double else '{' + body + '}'


class Report:
    def __init__(self):
        self.n = {}
        self.items = []

    def count(self, k):
        self.n[k] = self.n.get(k, 0) + 1

    def flag(self, lineno, kind, text):
        self.items.append((lineno, kind, text))


# --- normalisation d'une ligne francaise ------------------------------------
PAREN = re.compile(r'\(([^()]*[' + HAN + HEXA + TRI + r'][^()]*)\)')
BARE_TERM = re.compile(
    '([' + HEXA + TRI + '])'                          # symbole
    r'(?:\s*([' + HAN + ']{1,4}))?'                   # caracteres optionnels
    r"(?:\s+((?:[A-ZĀÁǍÀĒÉĚÈĪÍǏÌŌÓǑÒŪÚǓÙ][a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]+)"
    r"(?:[\s-][A-ZĀÁǍÀĒÉĚÈĪÍǏÌŌÓǑÒŪÚǓÙ][a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]+)?))?")
PY_SYM = re.compile(r"([A-ZĀÁǍÀĒÉĚÈĪÍǏÌŌÓǑÒŪÚǓÙ][a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]+)\s+([" + HEXA + TRI + "])")
BARE_HAN = re.compile('([《「]?[' + HAN + '][' + HAN + CJKP + ']*)'
                      r"(?:(\s*,?\s+)([a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]+(?:\s[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]+){0,3}))?")


def protect(s, store):
    """Remplace les {...} deja produits par des jetons pour ne pas les retraiter."""

    def keep(m):
        store.append(m.group(0)); return '\x00%d\x00' % (len(store) - 1)
    return re.sub(r'\{\{.*?\}\}|\{[^{}]*\}', keep, s)


def restore(s, store):
    return re.sub('\x00(\\d+)\x00', lambda m: store[int(m.group(1))], s)


def parse_fields(body):
    f = {'sy': [], 'zh': [], 'py': [], 'fr': []}
    for part in body.split(' | '):
        k, _, v = part.partition(':')
        if k in f and v:
            f[k].append(v)
    return f


TERM = r'\{\{([^{}]*)\}\}'


def merge_terms(line, rep):
    # terme suivi de (Pinyin) seul
    def add_py(m):
        f = parse_fields(m.group(1))
        if f['py'] or not is_pinyin(m.group(2), need_tone=True):
            return m.group(0)
        f['py'].append(m.group(2)); rep.count('fusion_py')
        return fmt(f, True)
    line = re.sub(TERM + r"\s*\(([^()]{1,30})\)", add_py, line)

    # deux termes adjacents aux champs disjoints
    def join(m):
        a, b = parse_fields(m.group(1)), parse_fields(m.group(2))
        if any(a[k] and b[k] for k in a):
            return m.group(0)
        rep.count('fusion_termes')
        return fmt({k: a[k] + b[k] for k in a}, True)
    prev = None
    while prev != line:
        prev = line
        line = re.sub(TERM + r"\s+" + TERM, join, line, count=1)
    return line


def norm_fr(line, rep, lineno):
    # 1. parentheses contenant du chinois / des symboles
    def par(m):
        if re.match(r'\s*(Note|N\.B\.|cf\.)', m.group(1), re.I):
            return m.group(0)   # note du traducteur : les caracteres seront balises plus bas
        f = fields(m.group(1))
        if not f['zh'] and f['fr']:
            return m.group(0)   # texte francais avec symboles : traite plus bas
        rep.count('annotation')
        if f['fr']:
            rep.count('annotation_avec_glose')
        if f['py'] and not TONE.search(' '.join(f['py'])):
            rep.flag(lineno, 'pinyin sans ton', fmt(f))
        if not (f['zh'] or f['sy']):
            rep.flag(lineno, 'annotation sans chinois', m.group(0))
        return fmt(f)
    line = PAREN.sub(par, line)
    store = []
    line = protect(line, store)

    # 2a. pinyin suivi d'un symbole
    def py_sym(m):
        if not is_pinyin(m.group(1), need_tone=True):
            return m.group(0)
        rep.count('terme')
        return fmt({'sy': [m.group(2)], 'zh': [], 'py': [m.group(1)], 'fr': []}, True)
    line = PY_SYM.sub(py_sym, line)
    line = protect(line, store)

    # 2b. symbole nu (+ caracteres) (+ pinyin) = terme du texte
    def bare(m):
        f = {'sy': [m.group(1)], 'zh': [m.group(2)] if m.group(2) else [],
             'py': [], 'fr': []}
        py = m.group(3)
        if py and is_pinyin(py):
            f['py'].append(py)
        elif py:
            return fmt(f, True) + m.group(0)[m.group(0).index(py) - 1:]
        rep.count('terme')
        return fmt(f, True)
    line = BARE_TERM.sub(bare, line)

    line = protect(line, store)

    # 3. caracteres nus restants
    def han(m):
        f = {'sy': [], 'zh': [m.group(1)], 'py': [], 'fr': []}
        if m.group(3) and TONE.search(m.group(3)) and is_pinyin(m.group(3)):
            f['py'].append(m.group(3))
            rep.count('terme_zh_py')
            return fmt(f, True)
        rep.count('terme_zh')
        return fmt(f, True) + (m.group(2) or '') + (m.group(3) or '')
    line = BARE_HAN.sub(han, line)
    while chr(0) in line:
        line = restore(line, store)
    line = merge_terms(line, rep)
    # il ne doit plus rester de chinois hors accolades
    rest = re.sub(r'\{\{.*?\}\}|\{[^{}]*\}', '', line)
    if RE_HAN.search(rest) or SYMS.search(rest):
        rep.flag(lineno, 'chinois hors balise', '')
    return line


# --- classification des lignes ----------------------------------------------
def unwrap(s):
    s = s.strip()
    bold = False
    for w in ('**', '__', '*', '_'):
        if len(s) > 2 * len(w) and s.startswith(w) and s.endswith(w) and w not in s[len(w):-len(w)]:
            if len(w) == 2:
                bold = True
            s = s[len(w):-len(w)].strip()
    return s, bold


def is_zh_line(s):
    t, _ = unwrap(s)
    han = len(RE_HAN.findall(t))
    lat = len(re.findall('[A-Za-zÀ-ÿ]', t))
    return han > 0 and han >= lat


LABEL = re.compile(r'^\*\*([^*\n]{2,60}?)\s?:\s?\*\*\s*(.*)$')
LABELS = [  # (motif, action, valeur)
    (r'^Texte( original)?( à traduire| de l.hexagramme| du « ?Xiang ?».*)?$', 'open', 'jing'),
    (r'^Commentaire( de Wang Fuzhi)?$', 'open', 'comm'),
    (r'^Prononciation$', 'role', 'py'),
    (r'^Traduction( du « ?Xiang ?».*)?$', 'role', 'fr'),
]


def label_of(st):
    m = LABEL.match(st)
    if not m:
        return None
    for pat, act, val in LABELS:
        if re.match(pat, m.group(1).strip()):
            return act, val, m.group(2).strip(), m.group(1).strip()
    return None


def strip_quotes(t):
    t = t.strip()
    for a, b in (('"', '"'), ('“', '”'), ('「', '」')):
        if len(t) > 2 and t.startswith(a) and t.endswith(b) and a not in t[1:-1] and b not in t[1:-1]:
            return t[1:-1].strip()
    return t


def convert(src, dst, rpt, skip=None, variants=()):
    lines = unicodedata.normalize('NFC', open(src, encoding='utf-8').read()).replace('\r\n', '\n').split('\n')
    rep = Report()
    out = []
    seg = None          # {'kind', 'rows', 'open'}
    role = None         # role impose par une etiquette pour la prochaine ligne

    def flush():
        nonlocal seg
        if seg and seg['rows']:
            order = {'zh': 0, 'py': 1, 'fr': 2}
            rows = sorted(seg['rows'], key=lambda r: order[r[0]])   # zh, py, fr
            if seg['kind'] == 'note' and any(k == 'zh' for k, _ in rows):
                seg['kind'] = 'comm'
            out.append('::: ' + seg['kind'])
            out.extend(k + ': ' + v for k, v in rows)
            out.append(':::')
            out.append('')
            rep.count('segment_' + seg['kind'])
        seg = None

    def has(k):
        return seg is not None and any(r[0] == k for r in seg['rows'])

    var_end = None
    for i, raw in enumerate(lines, 1):
        if var_end is not None and i > var_end:
            flush(); out.append('+++'); out.append(''); var_end = None
        for a, b, title in variants:
            if i == a:
                flush(); out.append('+++ variante ' + title); out.append(''); var_end = b
                rep.count('variante')
        if skip and skip[0] <= i <= skip[1]:
            if i == skip[0]:
                flush(); out.append('<!-- passage %d-%d non converti -->' % skip); out.append('')
            continue
        st = raw.strip()
        if not st:
            if seg and has('fr'):
                flush()          # un passage complet se termine a la ligne vide
            continue
        if re.fullmatch(r'-{3,}|_{3,}|\*{3,}', st):
            flush(); role = None; out.append('---'); out.append(''); continue
        if st.startswith('#'):
            flush(); role = None
            m = re.match(r'(#+)\s*(.*)$', st)
            title, _ = unwrap(m.group(2))
            title = title.replace('**', '').strip()
            if is_zh_line(title) and not SYMS.search(title):
                out.append(m.group(1) + ' {{zh:' + title + '}}')
            else:
                out.append(m.group(1) + ' ' + norm_fr(title, rep, i))
            out.append('')
            continue
        if st.startswith('>'):
            st = re.sub(r'^(>\s?)+', '', st).strip()
            if st.startswith('[!'):
                flush(); out.append('> ' + st); out.append(''); continue
            if not st:
                continue
            role = role or 'fr'
        lab = label_of(st)
        if lab:
            act, val, rest, name = lab
            rep.count('etiquette_' + val)
            if act == 'open':
                flush(); role = None
                if RE_HAN.search(name):   # libelle contenant du chinois : garde comme intertitre
                    out.append('#### ' + norm_fr(name, rep, i)); out.append('')
                seg = {'kind': val, 'rows': []}
                if not rest:
                    continue
                st = rest
            else:
                if not rest:
                    role = val; continue
                st, role = rest, val
        bold = st.startswith('**')
        t, _ = unwrap(st)
        if role == 'py' or (role is None and is_zh_line(t) is False and not RE_HAN.search(t)
                            and seg is not None and not has('py') and is_pinyin(t, need_tone=True)):
            if seg is None:
                seg = {'kind': 'note', 'rows': []}
            seg['rows'].append(('py', t)); rep.count('ligne_py'); role = None; continue
        if role != 'fr' and is_zh_line(t):
            if seg is None or has('zh') or has('fr'):
                flush(); seg = {'kind': 'jing' if bold else 'comm', 'rows': []}
            elif bold:
                seg['kind'] = 'jing'
            seg['rows'].append(('zh', strip_quotes(t))); role = None
            continue
        if seg is None:
            seg = {'kind': 'note', 'rows': []}
        seg['rows'].append(('fr', norm_fr(t, rep, i))); rep.count('ligne_fr'); role = None
    flush()
    if var_end is not None:
        out.append('+++')

    # controles de structure
    blocks = '\n'.join(out).split(':::')
    for b in out:
        pass
    text = '\n'.join(out).rstrip() + '\n'
    text = re.sub(r'\n{3,}', '\n\n', text)
    open(dst, 'w', encoding='utf-8', newline='\n').write(text)

    with open(rpt, 'w', encoding='utf-8') as r:
        r.write('Source : %s\nSortie : %s\n\n' % (src, dst))
        for k in sorted(rep.n):
            r.write('%-26s %d\n' % (k, rep.n[k]))
        r.write('\nCas a verifier (%d)\n' % len(rep.items))
        for ln, kind, txt in rep.items:
            r.write('ligne %5d  %-24s %s\n' % (ln, kind, txt))
    return rep


if __name__ == '__main__':
    import argparse
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('dst'); ap.add_argument('rpt')
    ap.add_argument('--saute', help='debut-fin : lignes source ignorees')
    ap.add_argument('--variante', action='append', default=[],
                    help='debut-fin:Titre : lignes source repliees en accordeon')
    a = ap.parse_args()
    skip = tuple(map(int, a.saute.split('-'))) if a.saute else None
    variants = []
    for v in a.variante:
        rng, _, title = v.partition(':')
        x, y = map(int, rng.split('-'))
        variants.append((x, y, title.strip() or 'Autre version'))
    rep = convert(a.src, a.dst, a.rpt, skip, variants)
    for k in sorted(rep.n):
        print(k, rep.n[k])
    kinds = {}
    for _, k, _ in rep.items:
        kinds[k] = kinds.get(k, 0) + 1
    print('a verifier', kinds)
