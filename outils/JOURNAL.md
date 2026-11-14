# Journal : homogénéiser une traduction « vibe-translated »

*Étape réalisée le 14 novembre 2026, avec Claude Code (modèle Claude Opus 5.5), sur la traduction du* Zhōuyì Nèizhuàn *de Wang Fuzhi.*

## Le point de départ

La traduction avait été produite chapitre par chapitre avec plusieurs IA (DeepSeek, Gemini, Claude, Google Traduction…), au fil des conversations. Le résultat était lisible, mais chaque IA, et parfois chaque session, avait choisi sa propre manière de présenter le texte. La première liseuse, qui devait permettre d'afficher ou de masquer les caractères, le pinyin et les symboles, ne pouvait donc pas s'appuyer sur une structure fiable : il fallait deviner la forme de chaque passage.

L'objectif de cette étape : **ramener tous les chapitres à une seule syntaxe**, sans retoucher la traduction elle-même, puis écrire une liseuse simple qui lit cette syntaxe.

## 1. Mesurer l'hétérogénéité

Avant de transformer quoi que ce soit, on a mesuré. `analyse/formes_annotations.py` réduit chaque parenthèse contenant du chinois à une forme abstraite. Sur l'ensemble du corpus, une quinzaine de formes coexistaient :

| Chapitre | Forme dominante | Exemple |
| --- | --- | --- |
| 00, 1a | pinyin puis caractères | (Fúxī 伏羲) |
| 1b, 2a, 3a, 3b | caractères puis pinyin | (同人 tóng rén) |
| 2b, 4a | caractères, virgule, pinyin | (革, gé) |
| 3b | avec tiret et italique | (井 - _Jǐng_) |
| 1a | symbole, pinyin, glose | (䷀, Qián, "Le Créateur") |

La mise en page des passages variait tout autant : traduction en citation `>` (1a), étiquettes « **Texte original à traduire :** / **Prononciation :** / **Traduction :** » (1b), pinyin placé après la traduction (2a), chinois et traduction séparés par une ligne vide (2b), étiquettes de traits « Neuf au quatrième (九四…) : » intégrées à la traduction (4a)… `profil.py` et `analyse/etiquettes.py` décrivent ces structures sans afficher le texte.

## 2. Choisir une syntaxe

Décidée avec l'auteur, elle est décrite en détail dans [SYNTAXE.md](SYNTAXE.md) :

- chaque passage est un bloc `::: jing` (texte classique), `::: comm` (commentaire de Wang Fuzhi) ou `::: note` (français seul), avec une ligne par rôle : `zh:`, `py:` (facultative), `fr:` ;
- dans la traduction, une annotation devient `{zh:孚 | py:fú}`, champs toujours dans l'ordre `sy | zh | py | fr` (symbole, caractères, pinyin, glose) ;
- un terme qui fait partie de la phrase (nom d'hexagramme…) devient `{{sy:䷨ | zh:損 | py:Sǔn}}` : il ne disparaît jamais entièrement à l'affichage ;
- un passage traduit deux fois est encadré par `+++ variante Titre` … `+++` et s'affiche replié.

Le pinyin intégral par passage est conservé là où il existait ; rien n'a été généré automatiquement.

## 3. Convertir avec prudence

`homogeniser.py` a été mis au point sur un chapitre pilote (3b), validé par l'auteur, puis étendu aux autres en adaptant les règles à chaque variante. Les points délicats :

- **reconnaître le pinyin** : chaque mot est découpé en syllabes pinyin valides, sinon il est traité comme du français ;
- **les étiquettes** se rangent en trois familles : celles qui ouvrent un passage (« Texte original… », « Commentaire de Wang Fuzhi »), celles qui donnent un rôle à la ligne (« Prononciation », « Traduction »), et celles qui font partie de la traduction (4a), laissées dans le texte ;
- **les gloses** dans les parenthèses (« (革, la Mue/Révolution) ») vont dans le champ `fr:` au lieu d'être perdues ;
- **l'ordre des lignes** est rétabli (zh, py, fr), même quand la source plaçait le pinyin en dernier.

Après chaque modification, `controle.py` vérifie qu'**aucun caractère chinois ni symbole n'a été perdu** (comptage source/sortie), qu'il ne reste aucun caractère chinois non balisé dans les traductions, et que la syntaxe est bien formée. Les huit chapitres passent ces contrôles. Les cas à revoir à la main (pinyin sans ton, etc.) sont dans `rapports/`.

## 4. Les blocages de modération

C'est l'aspect le plus singulier de ce travail. Pendant la session, les filtres de sécurité automatiques de l'outil ont signalé plusieurs messages, alors que le texte est un commentaire philosophique du XVIIᵉ siècle. Ces signalements se produisaient quand la conversation touchait à certains passages du chapitre 3a, ceux que les IA de traduction avaient déjà eu du mal à traiter (marqués « CENSURE » ou « MODÉRATION » dans les fichiers). Nous n'avons pas pu savoir précisément ce qui les déclenchait.

La stratégie adoptée :

1. **ne plus faire remonter le texte dans la conversation** : les scripts n'affichent que des comptes, des formes abstraites (`漢 py`, `zpf`) et des numéros de ligne ;
2. **travailler d'abord sur d'autres chapitres**, puis traiter 3a « à l'aveugle », uniquement par les contrôles chiffrés ;
3. **détecter les doublons sans lire** : `analyse/marqueurs.sh` repère les traces de blocage, puis `analyse/doublons.py` compare les phrases chinoises des zones voisines.

| Zone | Recouvrement mesuré | Décision |
| --- | --- | --- |
| 3b, entre deux titres « CENSURE » | 23 phrases sur 27 déjà présentes | doublon, replié |
| 4a, « MODÉRATION » | 22 sur 23 déjà dans le 漸 d'origine | doublon, replié |
| 4a, « Jian par Claude » | 10 sur 35 | seconde version de ䷴ 漸, repliée |
| 3a, zones « CENSURE » | quasi nul | suite du texte sans caractères chinois, laissée visible |

Le chapitre 3a reste donc à relire à l'œil : il a été converti et contrôlé, mais personne ne l'a regardé pendant cette étape.

## 5. La nouvelle liseuse

`liseuse.html` (à la racine) lit directement `français/markdown/*.md` et le rend dans le navigateur. On peut y afficher ou masquer chaque type de ligne (chinois, pinyin, traduction) et chaque champ des termes (symbole, caractères, pinyin, glose), choisir un surlignage, n'afficher que le texte classique, et passer en mode jour ou nuit. Les doublons sont repliés dans des accordéons.

Les liens déjà publiés vers l'ancienne liseuse (`liseuse.html?post=…/html-balises/1atag.html`) restent valides : la nouvelle déduit le chapitre de l'adresse. L'ancienne liseuse et les textes d'origine sont dans `_archives/`.

Deux pièges de GitHub Pages (Jekyll) ont été corrigés : les dossiers commençant par `_` ne sont pas publiés sans `_config.yml`, et un fichier Markdown qui commence par `---` est pris pour un en-tête YAML et n'est plus servi tel quel.

## 6. Prononciation : pinyin à la sélection et voix chinoise

Ajoutée ensuite, pour apprendre un peu de chinois en lisant. Lire le pinyin d'un texte classique n'a pas grand sens philologique, mais c'est une porte d'entrée.

- **Pinyin à la sélection** : quand on sélectionne des caractères, une bulle affiche le pinyin de chacun. La table `donnees/pinyin.json` (48 Ko, 2 869 caractères, tous ceux du corpus) est extraite de la base Unihan d'Unicode par `generer_pinyin.py`. Elle est servie avec la liseuse : aucune donnée ne sort du navigateur. Pour les 1 339 caractères qui ont plusieurs lectures, toutes sont montrées, la plus courante en premier, sans choix automatique selon le contexte. Si la sélection correspond à un terme annoté dans la traduction, la bulle rappelle la lecture retenue par celle-ci.
- **Voix** : la synthèse vocale intégrée au navigateur lit la sélection ou un caractère seul. Seules les voix installées sur l'appareil sont proposées. Les voix « en ligne » de Chrome ou d'Edge, qui enverraient le texte à Google ou à Microsoft, sont écartées. Sous Windows, les voix Huihui, Kangkang et Yaoyao s'installent avec le chinois dans les paramètres de langue.

## Les scripts

| Script | Rôle |
| --- | --- |
| `tout_convertir.sh` | régénère et contrôle tous les chapitres ; déclare les zones repliées |
| `homogeniser.py` | convertisseur source → syntaxe homogène (`--variante`, `--saute`) |
| `controle.py` | contrôles chiffrés d'un chapitre converti |
| `profil.py` | structure d'un texte source, en codes abstraits |
| `analyse/formes_annotations.py` | inventaire des formes de parenthèses |
| `analyse/etiquettes.py` | inventaire des étiquettes en gras |
| `analyse/marqueurs.sh` | traces de blocage, par numéro de ligne |
| `analyse/doublons.py` | recouvrement entre zones, pour repérer les doublons |
| `generer_pinyin.py` | table de pinyin de la liseuse, à partir de la base Unihan |

Pour tout régénérer : `sh outils/tout_convertir.sh`. Prérequis : Python 3, sans bibliothèque externe.

## Ce qui reste à faire

- relire 3a à l'œil, et vérifier en particulier ses zones sans caractères chinois ;
- choisir entre les deux versions de ䷴ 漸 dans 4a ;
- 00 : la traduction est très libre et ses paragraphes ne correspondent pas un à un au chinois ;
- traduire et convertir les chapitres suivants (4b à 6b) ; le convertisseur devra probablement être adapté à leurs propres variantes.
