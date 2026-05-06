# ProgramUtile

Ce repertoire réunit plusieurs petits programmes utiles de tous les jours :

- webpToconverter : Programme pour convertir les .webp (format inutile) en .jpeg ou en .png
- YoutubeDownloader+ : Programme pour télécharger des extraits de vidéo YouTube

## Installation

1. Placez-vous dans le répertoire `ProgramUtile`

2. Installez les dépendances depuis le fichier `requirements.txt`

OSx et Linux:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

- Pour lancer l'application principale :

```bash
python Main.py
```

ou

```bash
python3 Main.py
```

- `webpToconverter` : lancez le script correspondant, choisissez un fichier `.webp`, puis sélectionnez le format de sortie `.jpeg` ou `.png`
- `YoutubeDownloader+` : lancez le script correspondant, entrez l'URL de la vidéo YouTube et choisissez les options de téléchargement ou d'extrait
