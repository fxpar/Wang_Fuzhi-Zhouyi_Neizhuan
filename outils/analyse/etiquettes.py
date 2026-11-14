"""Profil des etiquettes en gras du type « **Traduction :** » dans un texte source.

Pour chaque etiquette : combien de fois elle apparait, ce qui la suit sur la meme ligne
(vide / zh / py / fr) et la nature de la ligne suivante. C'est ce qui a permis de
classer les etiquettes en trois familles (ouvrir un passage, donner un role, faire
partie de la traduction) dans outils/homogeniser.py.

Usage : python -I outils/analyse/etiquettes.py _archives/markdown-v1/1b.md [autres.md…]
Le texte lui-meme n'est jamais affiche, seulement les libelles (parentheses masquees).
"""
import re, sys, io, os, collections, unicodedata

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from homogeniser import is_pinyin, RE_HAN  # noqa: E402

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
LAB = re.compile(r'^\s*\*\*([^*\n]{2,60}?)\s?:\s?\*\*\s*(.*)$')


def nature(t):
    if not t.strip():
        return 'vide'
    h = len(RE_HAN.findall(t)); l = len(re.findall('[A-Za-zÀ-ÿ]', t))
    if h and h >= l:
        return 'zh'
    if is_pinyin(t.strip('*_ '), True):
        return 'py'
    return 'fr'


for path in sys.argv[1:]:
    L = unicodedata.normalize('NFC', open(path, encoding='utf-8').read()).split('\n')
    res = collections.Counter()
    for i, l in enumerate(L):
        m = LAB.match(l)
        if not m:
            continue
        lab = re.sub(r'\(.*?\)', '(…)', m.group(1))[:40]
        nxt = next((x for x in L[i + 1:] if x.strip()), '')
        res[(lab, nature(m.group(2)), nature(nxt))] += 1
    print('##', path)
    for (lab, meme, suite), n in res.most_common(20):
        print('  %5d  %-42s meme ligne: %-4s  ligne suivante: %s' % (n, lab, meme, suite))
