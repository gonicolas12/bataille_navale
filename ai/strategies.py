"""
Stratégies d'IA pour le jeu de bataille navale.
"""

import random
import numpy as np

class BaseStrategy:
    """Classe de base pour les stratégies d'IA."""
    
    def evaluate_move(self, move, board, data=None):
        """
        Évalue un coup possible.
        
        Args:
            move (tuple): Position (x, y) du coup à évaluer
            board (Board): La grille de jeu actuelle
            data (pandas.DataFrame, optional): Données historiques des parties
            
        Returns:
            float: Score d'évaluation du coup
        """
        return 0  # Par défaut, tous les coups ont le même score


class RandomStrategy(BaseStrategy):
    """Stratégie aléatoire (pour référence/comparaison)."""
    
    def evaluate_move(self, move, board, data=None):
        """
        Évalue un coup de manière aléatoire.
        
        Args:
            move (tuple): Position (x, y) du coup à évaluer
            board (Board): La grille de jeu actuelle
            data (pandas.DataFrame, optional): Données historiques des parties
            
        Returns:
            float: Score aléatoire entre 0 et 1
        """
        return random.random()


class CenterWeightStrategy(BaseStrategy):
    """Stratégie donnant priorité au centre de la grille."""
    
    def evaluate_move(self, move, board, data=None):
        """
        Évalue un coup en favorisant le centre de la grille.
        
        Args:
            move (tuple): Position (x, y) du coup à évaluer
            board (Board): La grille de jeu actuelle
            data (pandas.DataFrame, optional): Données historiques des parties
            
        Returns:
            float: Score basé sur la distance au centre
        """
        x, y = move
        # Calculer la distance de Manhattan par rapport au centre
        center_x, center_y = board.size // 2, board.size // 2
        distance = abs(x - center_x) + abs(y - center_y)
        
        # Inverser la distance pour favoriser le centre (plus c'est proche, plus le score est élevé)
        max_distance = board.size - 1
        return (max_distance - distance) / max_distance


class CheckerboardStrategy(BaseStrategy):
    """Stratégie en damier pour optimiser la recherche initiale."""
    
    def evaluate_move(self, move, board, data=None):
        """
        Évalue un coup en favorisant un motif en damier.
        
        Args:
            move (tuple): Position (x, y) du coup à évaluer
            board (Board): La grille de jeu actuelle
            data (pandas.DataFrame, optional): Données historiques des parties
            
        Returns:
            float: 1.0 pour les positions du damier, 0.0 pour les autres
        """
        x, y = move
        return 1.0 if (x + y) % 2 == 0 else 0.0


class HuntTargetStrategy(BaseStrategy):
    """Stratégie de 'chasse' après avoir touché un navire."""
    
    def __init__(self):
        """Initialise la stratégie."""
        self.last_hit = None
        self.hit_stack = []
    
    def process_result(self, position, result, board):
        """
        Traite le résultat d'un tir pour mettre à jour la stratégie.
        
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
        
        elif isinstance(result, tuple) and result[0] == "sunk":
            self.last_hit = None
            self.hit_stack = []  # Réinitialiser la pile car le navire est coulé
    
    def get_next_target(self, board):
        """
        Retourne la prochaine cible à viser.
        
        Args:
            board (Board): La grille de jeu
            
        Returns:
            tuple ou None: Position (x, y) à viser, ou None si pas de cible spécifique
        """
        if self.hit_stack:
            next_move = self.hit_stack.pop()
            if next_move in board.get_valid_moves():
                return next_move
        return None
    
    def evaluate_move(self, move, board, data=None):
        """
        Évalue un coup en donnant une priorité très élevée aux positions adjacentes aux touches.
        
        Args:
            move (tuple): Position (x, y) du coup à évaluer
            board (Board): La grille de jeu actuelle
            data (pandas.DataFrame, optional): Données historiques des parties
            
        Returns:
            float: Score très élevé pour les positions ciblées
        """
        if move in self.hit_stack:
            return 100.0  # Score très élevé pour les positions adjacentes aux touches
        return 0.0


class HistoricalDataStrategy(BaseStrategy):
    """Stratégie utilisant les données historiques pour prédire les meilleurs coups."""
    
    def evaluate_move(self, move, board, data=None):
        """
        Évalue un coup en utilisant les données historiques.
        
        Args:
            move (tuple): Position (x, y) du coup à évaluer
            board (Board): La grille de jeu actuelle
            data (pandas.DataFrame): Données historiques des parties
            
        Returns:
            float: Score basé sur l'historique des parties
        """
        if data is None or data.empty:
            return 0.0
        
        # Convertir le tuple en chaîne pour la recherche
        move_str = f"{move[0]},{move[1]}"
        
        # Obtenir l'état de jeu actuel
        current_game_state = ";".join(f"{x},{y}" for x, y in board.shots)
        
        # Rechercher des parties similaires dans l'historique
        similar_games = data[data['game_state'].str.contains(current_game_state, na=False)]
        
        if similar_games.empty:
            return 0.0
        
        # Chercher ce coup dans des situations similaires
        matching_moves = similar_games[similar_games['position'] == move_str]
        
        if matching_moves.empty:
            return 0.0
        
        # Calculer le taux de réussite historique
        hits = matching_moves[matching_moves['result'].isin(['hit', 'sunk'])].shape[0]
        misses = matching_moves[matching_moves['result'] == 'miss'].shape[0]
        
        if hits + misses == 0:
            return 0.0
        
        # Retourner le taux de réussite
        return hits / (hits + misses) * 10  # Multiplier par 10 pour donner plus de poids