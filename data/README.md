# Données de Jeu - Bataille Navale

Ce dossier contient les données générées par le jeu de bataille navale.

## Format des Données

### game_data.csv

Ce fichier contient l'historique de toutes les parties jouées, avec les informations suivantes :

- `game_id` : Identifiant unique de la partie (format: YYYYMMDDHHmmSS)
- `turn` : Numéro du tour dans la partie
- `player` : Joueur ayant effectué l'action ('player' pour le joueur humain, 'ai' pour l'IA)
- `position` : Position du tir (format: "x,y")
- `result` : Résultat du tir ('miss', 'hit', 'sunk')
- `timestamp` : Horodatage de l'action (format: YYYY-MM-DD HH:MM:SS)
- `game_state` : Etat du jeu au moment de l'action (format compressé des positions des tirs)

### Exemple

```
game_id,turn,player,position,result,timestamp,game_state
20240318123456,1,player,"3,4",miss,2024-03-18 12:34:56,"3,4"
20240318123456,1,ai,"2,7",hit,2024-03-18 12:35:01,"2,7"
20240318123456,2,player,"3,5",hit,2024-03-18 12:35:06,"3,4;3,5"
```

## Page des statistiques

Cette page contient les statistiques suivantes :

- Distribution des victoires
- Taux de réussite des tirs (%)
- Historique des parties (nombre de parties jouées, durée moyenne d'une partie, nombre de victoires du joueur et de l'ia)

## Autres Fichiers Générés

À partir de la page statistiques, on peux aussi générer les fichiers suivant :

- `shots_heatmap.png` : Carte de chaleur des positions ciblées
- `statistics_report.txt` : Rapport textuel des statistiques
