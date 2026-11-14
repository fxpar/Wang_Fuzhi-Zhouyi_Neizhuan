#!/bin/sh
# Regenere le Markdown homogene (français/markdown) a partir des textes d'origine
# (_archives/markdown-v1), puis controle chaque chapitre.
# Les zones --variante sont des doublons dus aux blocages de moderation des IA,
# reperes par recouvrement des phrases chinoises (voir outils/rapports/BILAN.md).
# Usage, depuis n'importe ou :  sh outils/tout_convertir.sh
cd "$(dirname "$0")/.." || exit 1
SRC=_archives/markdown-v1
DST=français/markdown
RPT=outils/rapports
conv() {
  c=$1; shift
  echo "## $c"
  python -I outils/homogeniser.py "$SRC/$c.md" "$DST/$c.md" "$RPT/$c.txt" "$@" | tail -1
  python -I outils/controle.py "$SRC/$c.md" "$DST/$c.md" | head -1
}
for c in 00 1a 1b 2a 2b 3a; do conv $c; done
conv 3b --variante "934-963:Doublon (passage repris après un blocage)"
conv 4a --variante "1606-1668:Doublon (passage repris après un blocage)" \
        --variante "1669-1846:Seconde version de ䷴ 漸 (Claude)"
