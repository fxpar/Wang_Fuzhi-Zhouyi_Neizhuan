"""Detection de doublons entre zones d'un texte source, sans afficher le texte.

Quand une IA a ete bloquee par son moderateur en cours de traduction, le passage a
souvent ete redemande, parfois a un autre outil : le fichier contient alors deux
versions du meme passage. Pour le verifier sans relire (ni faire relire) le texte :

  - zones chinoises : on compare l'ensemble des phrases chinoises (>= 4 caracteres,
    decoupees sur la ponctuation) de chaque zone ;
  - zones sans chinois : on compare les trigrammes de mots francais.

Usage :
  python -I outils/analyse/doublons.py _archives/markdown-v1/4a.md 1432-1606 1606-1669 1669-1847
  python -I outils/analyse/doublons.py --fr _archives/markdown-v1/3a.md 1506-1634 1634-1820

Les zones sont des plages de lignes « debut-fin » (fin exclue). Resultat : taille de
chaque zone et nombre d'elements communs a chaque paire.
Lecture : 23 phrases sur 27 en commun = doublon ; presque rien en commun = suite du texte.
"""
import re, sys, io, itertools

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
H = re.compile('[㐀-鿿]')

args = sys.argv[1:]
fr = '--fr' in args
args = [a for a in args if a != '--fr']
path, zones = args[0], [tuple(map(int, z.split('-'))) for z in args[1:]]
L = open(path, encoding='utf-8').read().split('\n')


def zh_sentences(a, b):
    s = set()
    for l in L[a - 1:b - 1]:
        for p in re.split(r'[，。；：！？、“”「」《》\s]', l):
            p = ''.join(H.findall(p))
            if len(p) >= 4:
                s.add(p)
    return s


def fr_trigrams(a, b):
    w = re.findall("[a-zàâçéèêëîïôûùüÿœ']+", ' '.join(L[a - 1:b - 1]).lower())
    return set(zip(w, w[1:], w[2:]))


f = fr_trigrams if fr else zh_sentences
sets = {'%d-%d' % z: f(*z) for z in zones}
unit = 'trigrammes francais' if fr else 'phrases chinoises'
for k, v in sets.items():
    print('zone %-11s %5d %s' % (k, len(v), unit))
for a, b in itertools.combinations(sets, 2):
    print('  %s / %s : %d en commun' % (a, b, len(sets[a] & sets[b])))
