"""
Classe représentant le joueur IA pour le jeu de bataille navale.
"""

import pandas as pd
import os
import random

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
        self.last_hit = None
        self.hit_stack = []  # Pile pour stocker les positions adjacentes aux tirs réussis
        self.moves_evaluation = {}  # Dictionnaire pour évaluer les coups possibles
        
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
        Évalue tous les coups possibles et retourne le meilleur.
        
        Args:
            board (Board): La grille de jeu de l'adversaire
            
        Returns:
            tuple: La position (x, y) du meilleur coup à jouer
        """
        valid_moves = board.get_valid_moves()
        
        # Réinitialiser le dictionnaire d'évaluation
        self.moves_evaluation = {move: 0 for move in valid_moves}
        
        # Si on a des coups en attente (adjacents à un tir réussi), on les privilégie
        if self.hit_stack:
            next_move = self.hit_stack.pop()
            if next_move in valid_moves:
                return next_move
            
        # 1. Stratégie basique : ajouter des points pour les positions centrales
        for move in valid_moves:
            x, y = move
            # Le centre de la grille est plus susceptible de contenir des navires
            distance_to_center = abs(x - board.size // 2) + abs(y - board.size // 2)
            self.moves_evaluation[move] -= distance_to_center * 0.5  # Moins c'est loin du centre, mieux c'est
        
        # 2. Parcourir les données historiques pour améliorer l'évaluation
        if not self.game_data.empty:
            current_game_state = self._get_current_game_state(board)
            
            # Rechercher des parties similaires dans l'historique
            similar_games = self.game_data[self.game_data['game_state'].str.contains(current_game_state, na=False)]
            
            for move in valid_moves:
                # Convertir le tuple en chaîne pour la recherche
                move_str = f"{move[0]},{move[1]}"
                
                # Chercher ce coup dans des situations similaires
                matching_moves = similar_games[similar_games['position'] == move_str]
                
                if not matching_moves.empty:
                    hits = matching_moves[matching_moves['result'].isin(['hit', 'sunk'])].shape[0]
                    misses = matching_moves[matching_moves['result'] == 'miss'].shape[0]
                    
                    # Ajouter des points en fonction des résultats historiques
                    if hits + misses > 0:
                        hit_rate = hits / (hits + misses)
                        self.moves_evaluation[move] += hit_rate * 10
        
        # 3. Stratégie en damier pour optimiser les tirs
        for move in valid_moves:
            x, y = move
            if (x + y) % 2 == 0:  # Motif en damier
                self.moves_evaluation[move] += 1
        
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
        # Simplification : utiliser une chaîne représentant les positions des tirs
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
        x, y = position
        
        if result == "hit":
            self.last_hit = position
            
            # Ajouter les positions adjacentes à explorer
            adjacent_positions = [
                (x+1, y), (x-1, y), (x, y+1), (x, y-1)
            ]
            
            # Filtrer les positions valides (dans la grille et non tirées)
            for pos in adjacent_positions:
                px, py = pos
                if 0 <= px < board.size and 0 <= py < board.size and pos not in board.shots:
                    self.hit_stack.append(pos)
            
            # Mélanger pour éviter des motifs prévisibles
            random.shuffle(self.hit_stack)
        
        elif result[0] == "sunk":  # Le résultat est un tuple ('sunk', ship_name) si un navire est coulé
            self.last_hit = None
            self.hit_stack = []  # Réinitialiser la pile car le navire est coulé