"""Genere donnees/pinyin.json : lectures mandarin de chaque caractere present dans les textes.

Source : Unihan_Readings.txt de la base Unihan (Unicode, https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip,
licence : https://www.unicode.org/terms_of_use.html).

Ordre des lectures pour un caractere :
  1. kMandarin       lecture(s) la plus courante (Chine continentale, puis Taiwan si differente)
  2. kHanyuPinlu     lectures attestees dans un corpus, par frequence decroissante
  3. kXHC1983, kTGHZ2013, kHanyuPinyin   autres lectures des dictionnaires
On garde au plus 5 lectures, sans doublon.

Usage : python -I outils/generer_pinyin.py chemin/vers/Unihan_Readings.txt
(a lancer depuis la racine du depot ; lit français/markdown/*.md et _archives/markdown-v1/*.md)
"""
import re, sys, json, glob, os, collections

src = sys.argv[1]
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
HAN = re.compile('[㐀-䶿一-鿿豈-﫿𠀀-𱍏]')  # sans les hexagrammes U+4DC0-4DFF

# caracteres utilises dans le corpus
chars = set()
for f in glob.glob(os.path.join(root, 'français', 'markdown', '*.md')) + \
         glob.glob(os.path.join(root, '_archives', 'markdown-v1', '*.md')):
    chars |= set(HAN.findall(open(f, encoding='utf-8').read()))

fields = collections.defaultdict(dict)
for line in open(src, encoding='utf-8'):
    if line.startswith('#') or not line.strip():
        continue
    cp, key, val = line.rstrip('\n').split('\t')
    ch = chr(int(cp[2:], 16))
    if ch in chars:
        fields[ch][key] = val


def readings(f):
    out = []
    def add(r):
        r = r.strip()
        if r and r not in out:
            out.append(r)
    for r in f.get('kMandarin', '').split():
        add(r)
    pinlu = re.findall(r'([^\s(]+)\((\d+)\)', f.get('kHanyuPinlu', ''))
    for r, _ in sorted(pinlu, key=lambda x: -int(x[1])):
        add(r)
    for key in ('kXHC1983', 'kTGHZ2013', 'kHanyuPinyin'):
        for entry in f.get(key, '').split():
            for r in entry.split(':', 1)[-1].split(','):
                add(r)
    return out[:5]


table = {ch: ' '.join(readings(fields[ch])) for ch in sorted(chars) if fields.get(ch)}
missing = sorted(chars - set(table))
os.makedirs(os.path.join(root, 'donnees'), exist_ok=True)
dst = os.path.join(root, 'donnees', 'pinyin.json')
with open(dst, 'w', encoding='utf-8') as out:
    json.dump(table, out, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
multi = sum(1 for v in table.values() if ' ' in v)
print('caracteres du corpus :', len(chars))
print('avec lecture         :', len(table), '(dont', multi, 'a lectures multiples)')
print('sans lecture         :', len(missing))
print('taille', dst, ':', os.path.getsize(dst), 'octets')
