# Archive du prototype d'origine

`simulation_thread_2026-08.py` conserve le prototype `pygame` tel qu'il figure dans le fil
de travail du 14 août 2026. **Il n'a pas été corrigé** — c'est l'intérêt de l'archive.

Son modèle est réimplémenté proprement dans [`src/ide/abm/`](../src/ide/abm), avec des
tests et sans couche graphique.

## Avertissement sur la transcription

Le fil source est une impression Gmail **rasterisée**, sans couche de texte : le code a
été relu à l'écran, caractère par caractère. Une erreur de transcription ponctuelle n'est
donc pas exclue. Cette archive vaut comme témoignage de la structure du prototype, pas
comme source exécutable de référence.

En particulier, **l'indentation du corps de `main()` et du garde final a été perdue à
l'impression** : le fichier ne s'exécute pas en l'état. C'est reproduit à l'identique
plutôt que reconstitué, parce que deviner l'indentation d'origine reviendrait à réécrire
le code — et l'archive n'aurait alors plus de raison d'être.

## Les cinq défauts du prototype

Développés dans [`docs/limites.md`, point 14](../docs/limites.md).

| # | Défaut | Conséquence | Correction dans `ide.abm` |
|---|---|---|---|
| 1 | **aucune température sociale** | le conformisme est une force purement contractante ; la population s'effondre sur un point unique et l'IDE tombe à zéro quels que soient les autres réglages | paramètre `social_temperature`, appliqué par `Citizen.agitate()` |
| 2 | **contamination par téléportation** — `self.opinion.x = 1.0 if … else -1.0` | l'individu est instantanément placé dans un coin ; toute dynamique ultérieure disparaît | radicalisation progressive dans `Citizen.infect()` |
| 3 | **vérification infaillible** | tout individu à portée est soigné avec certitude, ce que la littérature sur l'hystérésis des croyances contredit | `FactChecker.efficacy`, probabiliste |
| 4 | **bords absorbants** — `max(-1.0, min(1.0, …))` | les individus agités s'accumulent sur les bords et y restent piégés ; l'IDE chute à haute température pour une raison numérique | réflexion sur les bords, `_reflect()` |
| 5 | **indentation perdue** | le script ne s'exécute pas | sans objet : le modèle est réécrit |

Le défaut 1 est le plus lourd, et le plus instructif : le paramètre central de toute la
théorie — la température sociale — était absent de sa seule implémentation. Le prototype
ne pouvait donc représenter aucun des régimes que la note décrivait, ni le débat fluide,
ni l'effet du bruit thermique qu'elle recommandait d'injecter.

## Ce que le prototype faisait bien

L'archive n'est pas là seulement pour lister des erreurs. Trois choix du prototype ont été
conservés tels quels dans la réimplémentation :

* **le compas politique à deux axes** plutôt qu'un spin binaire, qui répond à l'une des
  limites que le fil identifiait lui-même ;
* **le seuil de censure** comme paramètre pilotable, qui s'avère être exactement le levier
  que l'algorithme de recommandation contrôle — c'est devenu le `bubble_threshold` du
  modèle et la variable centrale du [notebook 08](../notebooks/08_abm_compas_politique.ipynb) ;
* **l'export CSV horodaté**, qui traduisait déjà le souci de produire des données
  analysables plutôt qu'une simple animation.
