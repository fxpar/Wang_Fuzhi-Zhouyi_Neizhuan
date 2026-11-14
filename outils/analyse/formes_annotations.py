"""Inventaire des formes d'annotation entre parentheses dans des fichiers Markdown.

Premiere etape du travail : mesurer a quel point la traduction est heterogene.
Chaque parenthese contenant du chinois est reduite a une forme abstraite :
  漢 = caracteres chinois, py = mots latins (pinyin ou francais),
  ⬢ = hexagramme, △ = trigramme, ⟪Q⟫ = titre 《…》, «S» = citation.
Exemple : "(Fúxī 伏羲)" -> "py 漢" ; "(革, gé)" -> "漢, py".

Usage : python -I outils/analyse/formes_annotations.py _archives/markdown-v1/1a.md [autres.md…]
Seules les formes et des extraits courts sont affiches.
"""
import re, sys, io, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HAN = '[㐀-鿿豈-﫿\U00020000-\U0002ffff]'
LAT = "[A-Za-zÀ-ÿĀ-ſǍ-ǜ'’\\-]+"


def shape(s):
    s = re.sub('[䷀-䷿]', '⬢', s)
    s = re.sub('[☰-☷]', '△', s)
    s = re.sub('《[^》]*》', '⟪Q⟫', s)
    s = re.sub(HAN + '+', '漢', s)
    s = re.sub('"[^"]*"|“[^”]*”', '«S»', s)
    s = re.sub(LAT + '(\\s+' + LAT + ')*', 'py', s)
    return s


for path in sys.argv[1:]:
    tot = collections.Counter()
    for line in open(path, encoding='utf-8'):
        if re.match(r'^\s*' + HAN, line):      # ligne de texte chinois original : ignoree
            continue
        for m in re.finditer(r'\(([^()]*' + HAN + r'[^()]*)\)', line):
            tot[shape(m.group(1))] += 1
    print('##', path, '-', len(tot), 'formes distinctes,', sum(tot.values()), 'annotations')
    for sh, n in tot.most_common(15):
        print('  %6d  %s' % (n, sh))
