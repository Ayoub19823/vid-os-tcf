# Vidéo quotidienne — simulation TCF Canada, expression orale (procédure)

Objectif : chaque jour, une vidéo publiée sur YouTube à **19 h 00, heure de Casablanca** (fuseau Metricool `Africa/Casablanca`),
sur un sujet d'actualité **tiré au hasard** parmi ceux qui n'ont pas encore de vidéo, puis reliée à son sujet sur le site.
Langue de travail : français. On s'adresse à Ayoub (fondateur de formation-tcfcanada.com, « PACK AYOUB »).

## 0. Installation (environnement neuf)
1. Attacher le dépôt `Ayoub19823/vid-os-tcf` (accès push), le cloner dans `/home/claude/vid-os-tcf`, puis `bash pipeline/setup.sh`.
2. Vérifier dans Metricool (brand `7353654`, `getScheduledPosts` sur la journée, fuseau `Africa/Casablanca`) qu'il n'y a pas
   **déjà** une vidéo YouTube prévue à 19 h aujourd'hui. Si oui : ne rien produire, juste faire le compte rendu.

## 1. Choisir le sujet
- `cd /home/claude/pipe && MOIS="<mois-courant>,<mois-précédent>" node pick.js > sujets.json`
  (ex. `MOIS="novembre-2026,octobre-2026"`). Le mois courant d'abord : n'utiliser le mois précédent que si tout le mois courant a déjà sa vidéo.
- Exclure `video: true` et les sujets déjà présents dans `pipeline/historique.csv`. Tirer au hasard (Tâche 2 ou 3).

## 2. Écrire le scénario — `/home/claude/v24/scen_<AAAAMMJJ>.py`
Modèle complet : `pipeline/v24/scen_daily.py` (`rodrigue` = Tâche 3, `yannick` = Tâche 2). Copier la structure à l'identique.
- **Tâche 3** (point de vue, chrono 4 min 30) : `E=_E(sujet, relance1, relance2, relance3, relance4)` (7 répliques),
  `CA` = 19 phrases de monologue, `CB` = 8 (4 réponses à la relance 1, 2 à la relance 2, 2 de conclusion), `CC` = 6 (3 + 3 pour les relances 3 et 4).
  `themes` (8 étiquettes courtes ≤ 14 caractères), `args`, `conn` (chaque mot doit figurer EXACTEMENT dans la phrase indiquée), `feed`, `bilan` (+ `STRUCT`).
- **Tâche 2** (interaction, chrono 3 min 30) : `E` = 17 répliques (E[0] = consigne + `END`, E[14] contient « Il nous reste trente secondes »,
  E[16] = « Avec plaisir. L'épreuve est terminée. »), `C` = 16 questions/réactions, `reg` (« tu » entre amis, « vous » sinon), `feed`, `themes`, `bilan`.
- Règles validées par Ayoub : **beaucoup d'hésitations naturelles** (« euh… », mots répétés « c'est… c'est », « comment dire… », reprises),
  langue naturelle (pas de niveau soutenu), 2 petites erreurs corrigées dans `feed` (type `fix`), candidats variés d'Afrique francophone
  (Cameroun, Côte d'Ivoire, Bénin, Sénégal, Maroc, Algérie, Togo, Mali…), lien avec le Canada / l'immigration quand c'est naturel.
- Longueur visée : T3 ≈ 2 650 caractères pour `CA`, ≈ 1 950 pour `CB+CC` ; T2 ≈ 2 000 pour `E`, ≈ 1 700 pour `C`.
- Voix ElevenLabs (modèle `eleven_v4`) — examinatrices : Claire `NEjemlRxgWmL5ZGJetsB`, Lucie `YxrwjAKoUKULGd0g8K9Y`,
  Marine `6FXyooAOTqUK8m2HWm32`, Émilie `d3AXX0BlgJHYFCuH9X88` ; candidats hommes : `MQxizY3GzlfoDug4EXRt`, `kRnE5e47lbU8Zg2MPQPm`,
  `4NXnXTAwm3xM0tMCOn0r`, `dbXZnF5pfQqN00XGwlRF`, `HbDa7eEZNGkUODgNzru6` ; femmes : `C5sH6vPhsC46AKaQmXXJ` (Maghreb),
  `cYITNPiqwVi5OklXGv3H`, `hzuja6LJVafBxphAzQRB`, `hxakRxllsjiR8LZPUfMd` ; narrateur Corentin : `IHngRooVccHyPqB4uQkG`.

## 3. Voix
Répliques jointes par ` [long pause] [long pause] `, une génération par bloc (garder le nombre de prises par défaut) :
- T3 : `e` (7 répliques E), `ca` (CA), `cb` (CB puis CC à la suite) ; T2 : `e` (17), `c` (16).
- `spec` (Corentin) : « On ouvre la partie <n en lettres> du mois de <mois>, puis la tâche <deux|trois>. » + pause + `theme_narr`.
Après `creative_get_flow_run_status`, télécharger : `python3 /home/claude/v24/dl_sess.py '{"<session>":"/home/claude/work/<cle>/e", ...}'`.
Vérifier le découpage (`robust` dans `/home/claude/t3/segs.py`) ; si une prise ne se découpe pas, prendre l'autre prise.

## 4. Fabrication
`cd /home/claude/v24 && SCEN=scen_<AAAAMMJJ> TEMPO=1.0 ./make_video.sh <cle> <2|3> <partie> <n° sujet> <mois-slug> <SORTIE> "<LIGNE1|LIGNE2>"`
- Nom de sortie : `TCF_ExpressionOrale_T<t>_<Mois>_P<p>_<Prénom>_<Sujet>` ; miniature : 2 lignes courtes en MAJUSCULES.
- T3 : si `t3build` affiche « E3 at elapsed » > 245 s, ajouter `SIMS[cle]['drop'] = [('E', 6), ('C', 30), ('C', 31), ('C', 32)]` et relancer.
- Contrôler 6 à 9 images de la vidéo finale (intro, site avec le bon sujet encadré, examen, bilan) et la miniature.

## 5. Publication
1. Copier mp4 + miniature dans `videos/`, commit, `git fetch origin main` puis push.
2. Metricool `createScheduledPost` (blogId `7353654`) à **AAAA-MM-JJT19:00:00, timezone Africa/Casablanca**, réseau YouTube,
   `media` = `https://raw.githubusercontent.com/Ayoub19823/vid-os-tcf/main/videos/<SORTIE>.mp4`, `videoThumbnailUrl` = …`_miniature.jpg`.
   - Titre (**100 caractères maximum**, toujours avec « Expression orale ») :
     `TCF Canada Expression orale Tâche <t> : « <titre court> » — Sujet <mois> <année>`
   - Texte : « EXPRESSION ORALE — TCF Canada, Tâche <t>. Sujet réel de <mois> <année> (Partie <p>, sujet n° <n>) : « <sujet> » » +
     paragraphe simulation (prénom, registre, hésitations, chronomètre, corrections, bilan) +
     « 🎯 Entraînez-vous sur ce sujet et consultez sa correction sur https://formation-tcfcanada.com — notre seule plateforme officielle, opérée par PACK AYOUB. »
     + `#TCFCanada #ExpressionOrale #TCF #Immigration #Canada`
   - youtubeData : privacy public, category EDUCATION, madeForKids false, isAiGeneratedContent true,
     tags [TCF Canada, expression orale, tâche <t>, simulation TCF, sujets <mois> <année>, PACK AYOUB, immigration Canada].
   - Limite YouTube/Metricool : 20 publications / 24 h glissantes (une publication en erreur compte aussi).
3. Ajouter une ligne à `pipeline/historique.csv` (lie_site = non), commit + push.

## 6. Liaison sur le site (tâche séparée, sur l'ordinateur d'Ayoub)
Après 19 h (Casablanca) : récupérer l'URL YouTube dans Metricool, puis dans Chrome (Claude in Chrome)
`https://www.formation-tcfcanada.com/admin/oral-topics/videos` → carte du sujet → champ « https://www.youtube.com/watch?v=… » →
Enregistrer → attendre « Vidéo liée à N apparitions ». Mettre `lie_site = oui` et l'URL dans `historique.csv`.

## 7. Compte rendu à Ayoub
Sujet choisi, candidat, heure de publication, lien de la vidéo (ou heure prévue), miniature ; signaler tout problème.
