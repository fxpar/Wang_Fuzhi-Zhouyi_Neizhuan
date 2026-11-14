# Syntaxe du Markdown homogène

Un seul format pour tous les chapitres, pensé pour que la liseuse n'ait plus rien à deviner.

## 1. Segments

Chaque passage est un bloc encadré par `:::`. Le mot après `:::` donne la nature du passage :

| Type   | Contenu                                                        |
| ------ | -------------------------------------------------------------- |
| `jing` | texte classique du *Yijing* (en gras dans les anciens fichiers) |
| `comm` | commentaire de Wang Fuzhi                                       |
| `note` | texte français seul (introduction, remarque du traducteur)     |

À l'intérieur, une ligne = un rôle, toujours dans cet ordre :

```
::: comm
zh: texte chinois original (une ligne)
py: pinyin intégral du passage (optionnel)
fr: traduction (une ou plusieurs lignes fr:)
:::
```

## 2. Termes dans la traduction

Deux formes, avec les mêmes champs, toujours dans l'ordre `sy | zh | py | fr` :

| Champ | Contenu                                  |
| ----- | ---------------------------------------- |
| `sy`  | symbole : hexagramme ䷀–䷿, trigramme ☰–☷ |
| `zh`  | caractères chinois                       |
| `py`  | pinyin                                   |
| `fr`  | glose française complémentaire           |

- **Annotation** `{zh:孚 | py:fú}` : remplace l'ancienne parenthèse. Elle s'affiche entre parenthèses et disparaît entièrement si on masque tous ses champs.
- **Terme** `{{sy:䷨ | zh:損 | py:Sǔn}}` : le mot fait partie de la phrase (nom d'hexagramme, de trigramme…). Il n'est jamais vide : si tout est masqué, la liseuse garde le pinyin.

Exemple :

```
fr: … avec la sincérité {zh:孚 | py:fú}, … du Paix {zh:泰 | py:Tài} …
## {{sy:䷨ | zh:損 | py:Sǔn}} « Le Dommage »
```

## 3. Le reste

Titres `#` (une étiquette d'origine qui contenait du chinois devient un intertitre `####`), séparateurs `---`, gras et italique du Markdown sont conservés. Une ligne `<!-- … -->` signale un passage laissé de côté.

## 4. Variantes (doublons)

Quand un passage existe en deux versions (reprise après un blocage du modérateur d'une IA), la seconde est encadrée ainsi et s'affiche repliée dans un accordéon :

```
+++ variante Seconde version de ䷴ 漸 (Claude)
… titres et passages ::: habituels …
+++
```

## 5. Outils (dossier `outils/`)

- `sh outils/tout_convertir.sh` : régénère `français/markdown/` à partir de `_archives/markdown-v1/` et contrôle chaque chapitre. C'est là que sont déclarées les variantes.
- `outils/homogeniser.py` : `python -I outils/homogeniser.py source.md sortie.md rapport.txt [--variante début-fin:Titre] [--saute début-fin]` (numéros de ligne de la source).
- `outils/controle.py` : vérifie qu'aucun caractère chinois ni symbole n'a été perdu et que la syntaxe est bien formée.
- `outils/profil.py` : décrit la mise en page d'un texte source, sans en afficher le contenu.
- `outils/rapports/` : compteurs, cas à vérifier, bilan des doublons.
- `liseuse.html` (racine) : lit directement `français/markdown/*.md`.
