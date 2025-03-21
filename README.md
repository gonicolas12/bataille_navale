# Bataille Navale - Jeu 1v1 (Humain vs IA)

Projet réalisé dans le cadre du module "Manipulation de données en Python" - YNOV B2 Informatique 2024/2025.

## Description du Projet

Ce projet est un jeu de bataille navale dans lequel un joueur humain affronte une intelligence artificielle. L'IA utilise une stratégie avancée basée sur une combinaison de règles prédéfinies et d'apprentissage à partir des parties précédentes.

## Fonctionnalités

- Interface graphique avec Tkinter
- Placement aléatoire des navires
- IA stratégique qui apprend des parties précédentes
- Enregistrement de toutes les actions dans un fichier CSV
- Visualisations statistiques avec Matplotlib
- Affichage des statistiques de jeu

## Prérequis

- Python 3.8 ou supérieur
- NumPy
- Pandas
- Matplotlib

## Installation

1. Clonez ce dépôt :
```
git clone https://github.com/gonicolas12/bataille_navale.git
cd bataille-navale
```

2. Installez les dépendances :
```
pip install -r requirements.txt
```

## Utilisation

Pour lancer le jeu en mode graphique :
```
python main.py
```

## Architecture du Projet

```
bataille_navale/
│
├── main.py                     # Point d'entrée principal
│
├── models/
│   ├── __init__.py
│   ├── ship.py                 # Classe Ship (navire)
│   ├── board.py                # Classe Board (grille)
│   └── game_manager.py         # Classe GameManager
│
├── ai/
│   ├── __init__.py
│   ├── ai_player.py            # IA principale
│   └── strategies.py           # Stratégies d'IA
│
├── utils/
│   ├── __init__.py
│   └── game_statistics.py      # Statistiques de jeu
│
├── ui/
│   ├── __init__.py
│   ├── gui.py                  # Interface principale
│   ├── game_board_view.py      # Vue des grilles
│   └── statistics_view.py      # Vue des statistiques
│
├── data/
│   ├── game_data.csv           # Données des parties
│   └── README.md               # Documentation des données
│
│
├── README.md                   # Documentation du projet
└── requirements.txt            # Dépendances
```

## Détails Techniques

### Classe Ship
Représente un navire avec sa taille, nom et état (positions, impacts).

### Classe Board
Gère la grille de jeu 10x10 avec placement des navires et réception des tirs.

### Classe AIPlayer
Implémente l'intelligence artificielle selon les 5 points du cahier des charges :

1. Dictionnaire des coups possibles
2. Fonction d'évaluation 
3. Théorie stratégique (centre, lignes, etc.)
4. Exploitation des données historiques
5. Sélection du meilleur coup

### Classe GameManager
Gère le déroulement du jeu et l'enregistrement des données.

### Classe GameStatistics
Génère les statistiques et graphiques à partir des données enregistrées.

## Réponse aux Exigences du Cahier des Charges

- ✅ POO : Architecture complètement orientée objet
- ✅ NumPy : Utilisé pour les grilles de jeu
- ✅ Pandas : Utilisé pour le stockage et l'analyse des données
- ✅ Matplotlib : Utilisé pour la visualisation des statistiques
- ✅ Stockage externe : Toutes les parties sont enregistrées dans un CSV
- ✅ Configuration IA : Implémentation complète des 5 points requis
- ✅ Interface graphique : Réalisée avec Tkinter

## Auteur

- [@nicolasgouy](https://www.github.com/gonicolas12)