"""
Classe pour le joueur IA.
"""

import pandas as pd
import os
import random
from ai.strategies import BaseStrategy, RandomStrategy, CenterWeightStrategy, CheckerboardStrategy, HuntTargetStrategy, HistoricalDataStrategy

class AIPlayer:
    """Classe représentant le joueur IA."""
    
    def __init__(self, game_data_file="data/game_data.csv"):
        """
        Initialise un nouveau joueur IA.
        
        Args:
            game_data_file (str, optional): Chemin vers le fichier de données de jeu.
                Par défaut "data/game_data.csv".
        """
        self.game_data_file = game_data_file
        self.moves_evaluation = {}
        
        # Initialiser les stratégies
        self.center_strategy = CenterWeightStrategy()
        self.checkerboard_strategy = CheckerboardStrategy()
        self.hunt_target_strategy = HuntTargetStrategy()
        self.historical_strategy = HistoricalDataStrategy()
        
        # Créer le dossier data s'il n'existe pas
        os.makedirs(os.path.dirname(game_data_file), exist_ok=True)
        
        # Charger les données des parties précédentes si le fichier existe
        if os.path.exists(game_data_file):
            self.game_data = pd.read_csv(game_data_file)
        else:
            # Créer un DataFrame vide avec les colonnes nécessaires
            self.game_data = pd.DataFrame(columns=[
                'game_id', 'turn', 'player', 'position', 'result', 'timestamp', 'game_state'
            ])
    
    def evaluate_moves(self, board):
        """
        Evalue tous les coups possibles et retourne le meilleur.
        
        Args:
            board (Board): La grille de jeu de l'adversaire
            
        Returns:
            tuple: La position (x, y) du meilleur coup à jouer
        """
        valid_moves = board.get_valid_moves()
        
        # Réinitialiser le dictionnaire d'évaluation
        self.moves_evaluation = {move: 0 for move in valid_moves}
        
        # Vérifier si la stratégie de chasse a une cible prioritaire
        next_target = self.hunt_target_strategy.get_next_target(board)
        if next_target:
            return next_target
        
        # Différentes stratégies, plus le poids est élevé, plus la stratégie est prioritaire
        for move in valid_moves:
            # Stratégie du centre (poids: 1.0)
            center_score = self.center_strategy.evaluate_move(move, board)
            self.moves_evaluation[move] += center_score * 1.0
            
            # Stratégie du damier (poids: 1.5)
            checkerboard_score = self.checkerboard_strategy.evaluate_move(move, board)
            self.moves_evaluation[move] += checkerboard_score * 1.5
            
            # Stratégie basée sur l'historique des données (poids: 2.0)
            if not self.game_data.empty:
                historical_score = self.historical_strategy.evaluate_move(move, board, self.game_data)
                self.moves_evaluation[move] += historical_score * 2.0
        
        # Trouver le coup avec le meilleur score
        best_move = max(self.moves_evaluation.items(), key=lambda x: x[1])[0]
        return best_move
    
    def _get_current_game_state(self, board):
        """
        Retourne une représentation de l'état actuel du jeu pour la comparaison.
        
        Args:
            board (Board): La grille de jeu
            
        Returns:
            str: Une chaîne représentant l'état du jeu
        """
        # Utiliser une chaîne représentant les positions des tirs
        shots_str = ";".join(f"{x},{y}" for x, y in board.shots)
        return shots_str
    
    def process_shot_result(self, position, result, board):
        """
        Traite le résultat d'un tir pour améliorer la stratégie de l'IA.
        
        Args:
            position (tuple): Position (x, y) du tir
            result (str ou tuple): Résultat du tir ('miss', 'hit' ou ('sunk', ship_name))
            board (Board): La grille de jeu
        """
        # Utiliser la stratégie HuntTarget pour traiter le résultat
        self.hunt_target_strategy.process_result(position, result, board)