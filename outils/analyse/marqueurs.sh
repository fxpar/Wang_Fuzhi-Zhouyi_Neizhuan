#!/bin/sh
# Repere, par numero de ligne seulement, les traces laissees par les blocages des IA
# (CENSURE, MODÉRATION, « reprise », noms d'outils…) dans les textes d'origine.
# Les zones trouvees sont ensuite comparees avec outils/analyse/doublons.py.
# Usage : sh outils/analyse/marqueurs.sh [dossier]   (par defaut _archives/markdown-v1)
cd "$(dirname "$0")/../.." || exit 1
DIR=${1:-_archives/markdown-v1}
for f in "$DIR"/*.md; do
  grep -n -o -i -E 'censure|MOD.RATION|reprise|par claude|deepseek|gemini|chatgpt|mistral|qwen|\[!danger\]|\[!warning\]' "$f" \
    | sed "s|^|$(basename "$f"):|"
done
