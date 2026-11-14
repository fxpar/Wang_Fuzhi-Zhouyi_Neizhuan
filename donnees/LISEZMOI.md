# Données de prononciation

`pinyin.json` associe chaque caractère chinois présent dans les textes du dépôt à ses lectures en mandarin, la plus courante en premier, sous la forme `{"乾": "qián gān", …}`. La liseuse s'en sert pour afficher le pinyin des caractères sélectionnés, sans rien envoyer à un service extérieur.

## Source et licence

Les lectures sont extraites de la base **Unihan** (version 18.0) du Consortium Unicode, fichier `Unihan_Readings.txt` de <https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip>, champs `kMandarin`, `kHanyuPinlu`, `kXHC1983`, `kTGHZ2013` et `kHanyuPinyin`.

Copyright © 1991-2026 Unicode, Inc. Données distribuées selon les conditions d'utilisation d'Unicode : <https://www.unicode.org/terms_of_use.html> (licence Unicode v3).

## Régénérer

Après l'ajout de nouveaux chapitres, téléchargez `Unihan.zip`, extrayez `Unihan_Readings.txt`, puis lancez depuis la racine du dépôt :

```
python -I outils/generer_pinyin.py chemin/vers/Unihan_Readings.txt
```

## Limites

Les lectures sont celles du chinois moderne, caractère par caractère. Pour un caractère à plusieurs lectures (行 xíng / háng, 見 jiàn / xiàn…), la liseuse les affiche toutes, sans choisir selon le contexte. Pour un terme annoté dans la traduction, elle indique aussi la lecture retenue par celle-ci.
