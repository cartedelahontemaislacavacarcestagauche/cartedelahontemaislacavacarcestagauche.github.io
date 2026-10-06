# Carte de la honte… mais là ça va, c'est à gauche

Carte interactive sur le modèle de [cartedelahonte.github.io](https://cartedelahonte.github.io/) (consacrée au RN), appliquée à La France insoumise : candidat(e)s investi(e)s par LFI aux législatives (élu(e)s ou non, titulaires et suppléant(e)s), plus quelques responsables nationaux du mouvement.

Chaque fiche ne reprend que des faits publiés par la presse, avec ses sources, et précise la situation judiciaire (condamnation, appel en cours, mise en examen, enquête, classement). Une enquête ou une mise en examen n'est pas une condamnation : les personnes concernées sont présumées innocentes.

## Utilisation

`index.html` est autonome : il suffit de l'ouvrir dans un navigateur ou de le servir tel quel (GitHub Pages, etc.). Il charge Leaflet depuis cdnjs et le fond de carte Esri.

## Mettre à jour

1. Modifier `data/entries.json` (une entrée par personne : `dep`, `circo`, `name`, `role`, `cats`, `paras`, `sources`, `elu` ; `label` à la place de `dep`/`circo` pour les fiches hors circonscription).
2. Régénérer la page :

```bash
python3 src/build.py
```

Le script vérifie que chaque catégorie existe et que chaque fiche a au moins une source. Il régénère aussi `social-card.png`, l'image d'aperçu affichée par Telegram, WhatsApp ou X (nécessite Pillow et la police Avenir Next de macOS).

## Données

- Contours des circonscriptions : [data.gouv.fr – Contours géographiques des circonscriptions législatives](https://www.data.gouv.fr/datasets/contours-geographiques-des-circonscriptions-legislatives) (Licence Ouverte 2.0), simplifiés.
- Fond de carte : Esri (World Ocean Base, World Light Gray Base).
