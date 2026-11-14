"""Controle d'un chapitre homogeneise (chiffres seulement).
Usage : python -I controle.py source/1a.md markdown/1a.md
"""
import re, sys, io, collections, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
src = unicodedata.normalize('NFC', open(sys.argv[1], encoding='utf-8').read())
dst = open(sys.argv[2], encoding='utf-8').read()
H = '[㐀-鿿]'
r = {}
r['car_source'] = len(re.findall(H, src))
r['car_sortie'] = len(re.findall(H, dst))
r['symboles_source'] = len(re.findall('[䷀-䷿☰-☷]', src))
r['symboles_sortie'] = len(re.findall('[䷀-䷿☰-☷]', dst))
shapes = collections.Counter()
for kind, body in re.findall(r'^::: (\w+)\n(.*?)\n:::$', dst, re.S | re.M):
    shapes[kind + ':' + ''.join(l[0] for l in body.split('\n'))] += 1
# lignes hors segments qui ne sont ni titre, ni separateur, ni commentaire
inside = False; stray = 0; bad_rows = 0
for l in dst.split('\n'):
    if l.startswith(':::'):
        inside = not inside if l.strip() == ':::' or not inside else inside
        if l.strip() != ':::':
            inside = True
        continue
    if inside:
        if not re.match(r'^(zh|py|fr): ', l):
            bad_rows += 1
    elif l.strip() and not re.match(r'^(#|---|<!--|> |\+\+\+)', l):
        stray += 1
r['lignes_hors_segment'] = stray
r['lignes_mal_formees'] = bad_rows
# chinois hors balise dans les lignes fr
out_fr = 0
for l in re.findall(r'^fr: (.*)$', dst, re.M):
    rest = re.sub(r'\{\{.*?\}\}|\{[^{}]*\}', '', l)
    if re.search(H, rest):
        out_fr += 1
r['fr_avec_chinois_nu'] = out_fr
r['accolades_desequilibrees'] = sum(1 for l in dst.split('\n') if l.count('{') != l.count('}'))
print(' '.join('%s=%s' % kv for kv in r.items()))
print('formes', shapes.most_common(10))
