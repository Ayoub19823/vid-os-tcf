# Tutoriel animé (méthode validée le 12/11/2026)

Vidéo de référence : « Examen blanc d'expression orale avec Ahlem et Emmanuel » (version 5).

## Fichiers
- `index.html` + `anim.js` : la page d'animation 1920×1080 (GSAP, timeline en pause, `window.seek(t)`). Une section par scène.
- `data.js` / `tl.json` : chronologie de la voix (`T0` = début de chaque scène, `W` = temps de chaque mot par segment, `TXT` = texte des segments) et positions mesurées des boutons (`R`).
- `cap.js`, `cap2.js` : captures du site avec Playwright (1600 px, deviceScaleFactor 2, fr-CA, America/Toronto) et mesure des boutons → `cap/R.json`, `cap/*.jpg`.
- `shots.js` : images de contrôle, `node shots.js 0.5,12,47`.
- `render.js` : rendu d'un MP4 par scène, `node render.js 0,1` (30 images/s, libx264 crf 18), à lancer en 4 processus puis concaténer (`ffmpeg -f concat -c copy`) et ajouter le son (`-c:v copy`).
- `voix_timeline.py` : découpe de la voix off en segments et assemblage (ancien moteur d'images ; seule la partie avant « ressources » sert encore).
- `clips/` : les deux démonstrations Higgsfield (muettes, 10 s). `anim.js` attend leurs images dans `fa/001.jpg…` et `fe/001.jpg…` :
  `ffmpeg -i clips/ahlem.mp4 -vf fps=30,scale=1280:720 -q:v 4 fa/%03d.jpg` (idem `emmanuel.mp4` → `fe/`).
- `voix/mix_v5.mp3` : piste audio finale de la version 5.
- `../v6/thumb_head.py` : miniature à titre libre, ex.
  `HEAD="EXAMEN BLANC" FACES=fa.jpg,fe.jpg BG="56,182,255,10,108,214" GLOW="50,40,0" python3 thumb_head.py EO 0 "Avec un examinateur" sortie.jpg "2 examens blancs|Feedback personnalisé" "TCF CANADA & TCF QUÉBEC"`

## À savoir
- `npm i` installe GSAP ; Playwright et Chromium doivent déjà être présents.
- Les scripts contiennent des chemins absolus de la session d'origine (`/home/claude/work/mg`, `/home/claude/work/exo`) : adaptez-les au dossier courant.
- Les temps des mots viennent d'une transcription horodatée de la voix (ElevenLabs Scribe). Ne les estimez pas.
- Les cadres rouges utilisent les positions de `cap/R.json` : refaites les captures si le site change.
