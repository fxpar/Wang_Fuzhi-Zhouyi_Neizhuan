# Bilan de l'homogénéisation

Sources : `_archives/markdown-v1/` (textes d'origine ; `2b.md` y a été ajouté depuis le dossier de production).
Pour chaque chapitre, `outils/rapports/<ch>.txt` détaille les compteurs et les cas à vérifier.

## Contrôles communs (outils/controle.py)

Pour les 8 chapitres (00, 1a, 1b, 2a, 2b, 3a, 3b, 4a) :
- tous les caractères chinois et tous les symboles ䷀ ☰ de la source sont présents dans la sortie ;
- aucune ligne hors passage, aucune ligne mal formée, aucune accolade déséquilibrée ;
- plus aucun caractère chinois nu dans les lignes `fr:` : tout est balisé.

## Ce que le convertisseur a dû absorber

| Ch. | Mise en page d'origine | Annotations |
| --- | --- | --- |
| 00 | paragraphes chinois puis paragraphes français, sans correspondance ligne à ligne | (pinyin 漢) |
| 1a | chinois, puis traduction en citation `>` | (pinyin 漢), notes « (Note : … se lit …) » laissées en texte |
| 1b | étiquettes « Texte original… / Prononciation / Traduction / Commentaire de Wang Fuzhi » | (漢 pinyin), beaucoup de (漢) seuls |
| 2a | classique : chinois / traduction / pinyin (ordre inversé) ; commentaire : chinois entre guillemets / traduction | (漢 pinyin), (漢 pinyin, glose) |
| 2b | chinois et traduction séparés par une ligne vide | (漢, pinyin) |
| 3b | chinois / pinyin / traduction en italique | (漢 pinyin), (井 - _Jǐng_) |
| 4a | chinois / pinyin / traduction ; étiquettes de traits « Neuf au quatrième (九四…) : » gardées dans la traduction | (漢, pinyin) |

## Doublons dus aux blocages de modération

Repérés en comparant les phrases chinoises (≥ 4 caractères) d'une zone avec celles du texte voisin :

| Zone source | Recouvrement | Traitement |
| --- | --- | --- |
| 3b l. 934–963 (entre deux titres « CENSURE ») | 23 phrases sur 27 déjà présentes juste avant | accordéon « Doublon » |
| 4a l. 1606–1668 (« MODÉRATION ») | 22 sur 23 déjà dans le 漸 d'origine | accordéon « Doublon » |
| 4a l. 1669–1846 (« Jian par Claude ») | 10 sur 35 en commun | accordéon « Seconde version de ䷴ 漸 » |
| 3a l. 1634–1819 (« CENSURE », fin de 家人 sans caractères) | quasi aucun recouvrement avec le français voisin | laissé visible : c'est la suite, pas un doublon |
| 3a l. 2507–2591 (balises « CENSURE », français seul) | idem | laissé visible |

Pour modifier ces choix : `outils/tout_convertir.sh`.

## Points à regarder toi-même

1. **3a** a été converti sans que son texte soit affiché pendant le travail : tous les contrôles chiffrés sont bons, mais une relecture visuelle reste à faire. 11 pinyins sans ton y sont listés.
2. **4a** : la « Reprise Deepseek » qui suit la seconde version de 漸 reste visible (c'est la suite du chapitre).
3. **00** : la traduction est très libre (formes comme « Fou Hisi », passages en anglais). Les paragraphes chinois et français ne se répondent pas un à un, d'où 40 passages chinois sans traduction et plus de 260 passages en français seul.
4. **1b** : le commentaire de Wang Fuzhi n'y existe qu'en français (166 passages `comm` sans chinois). Seul le texte classique a son original.
5. **Pinyin sans ton** : 8 cas en tout (00, 1b, 4a), listés dans les rapports.
6. **Passages « note »** : en 4a, 186 passages en français seul suivent des titres ou d'autres notes. C'est probablement de la traduction continue sans original en regard, à vérifier par sondage.

## Refaire la conversion

```
sh outils/tout_convertir.sh
```
Options de `outils/homogeniser.py` : `--variante début-fin:Titre`, `--saute début-fin`.
