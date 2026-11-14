"""Profil structurel d'un chapitre source : n'affiche que des formes abstraites, jamais le texte.
Usage : python -I profil.py source/1a.md
Codes : Z ligne chinoise, z chinoise en gras, P pinyin, F francais, f francais en italique/gras,
        Q citation '>', H titre, R separateur, L ligne 'Etiquette :' , _ ligne vide, M mixte (chinois+francais)
"""
import re, sys, io, collections, unicodedata
sys.path.insert(0, __file__.rsplit('\\', 1)[0].rsplit('/', 1)[0])
from homogeniser import is_pinyin, RE_HAN, unwrap

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
txt = unicodedata.normalize('NFC', open(sys.argv[1], encoding='utf-8').read()).replace('\r\n', '\n')
L = txt.split('\n')


def code(l):
    s = l.strip()
    if not s: return '_'
    if s.startswith('#'): return 'H'
    if re.fullmatch(r'[-_*]{3,}', s): return 'R'
    if s.startswith('>'): return 'Q'
    t, bold = unwrap(s)
    han = len(RE_HAN.findall(t)); lat = len(re.findall('[A-Za-zÀ-ÿ]', t))
    if re.match(r'^\*\*[^*]{2,30}:\s*\*\*|^\*\*[^*]{2,30}\s?:\*\*|^[A-Z][^:]{2,25} :\s*$', s): return 'L'
    if han and han >= lat: return 'z' if bold else 'Z'
    if han and lat > han and han > 5: return 'M'
    if is_pinyin(t, need_tone=True): return 'P'
    return 'f' if s[0] in '*_' else 'F'


cs = [code(l) for l in L]
print('lignes', len(L), dict(collections.Counter(cs)))
# motifs de groupes entre lignes vides
groups = collections.Counter()
cur = ''
for c in cs + ['_']:
    if c == '_':
        if cur: groups[cur if len(cur) < 12 else cur[:12] + '…'] += 1
        cur = ''
    else:
        cur += c
print('groupes', groups.most_common(18))
# etiquettes
labels = collections.Counter(re.sub(r'[\s*]', '', m) for m in re.findall(r'^\s*\*\*([^*\n]{2,30}?)\s?:\s?\*\*', txt, re.M))
print('etiquettes', labels.most_common(12))
print('guillemets « »', txt.count('«'), ' “ ”', txt.count('“'), ' 《》', txt.count('《'))
HAN = '[㐀-鿿]'
inl = collections.Counter()
for m in re.finditer(r'\(([^()]*' + HAN + r'[^()]*)\)', txt):
    c = m.group(1)
    c = re.sub(HAN + '+', '漢', c); c = re.sub('[䷀-䷿]', '⬢', c); c = re.sub('[☰-☷]', '△', c)
    c = re.sub("[A-Za-zÀ-ÿĀ-ſǍ-ǜ'’]+(\\s+[A-Za-zÀ-ÿĀ-ſǍ-ǜ'’]+)*", 'a', c)
    inl[c] += 1
print('parentheses', inl.most_common(10))
