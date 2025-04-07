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
        self.hits = []  # Liste de toutes les touches actuelles (non coulées)
        self.hit_stack = []  # Cases à explorer
        self.direction = None  # Direction identifiée (horizontal ou vertical)
    
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
            # Ajouter la position à la liste des touches
            self.hits.append(position)
            
            # Déterminer s'il y a une direction (horizontal ou vertical)
            if len(self.hits) >= 2:
                self.identify_direction()
            
            # Si une direction est identifiée, ajouter seulement les positions dans cette direction
            if self.direction:
                self.add_directional_targets(position, board)
            else:
                # Sinon, ajouter toutes les positions adjacentes
                adjacent_positions = [
                    (x+1, y), (x-1, y), (x, y+1), (x, y-1)
                ]
                
                # Filtrer les positions valides (dans la grille et non tirées)
                for pos in adjacent_positions:
                    px, py = pos
                    if 0 <= px < board.size and 0 <= py < board.size and pos not in board.shots:
                        self.hit_stack.append(pos)
        
        elif result == "miss":
            # Si on rate un tir alors qu'on suivait une direction, il faut essayer dans l'autre sens
            if self.direction and len(self.hits) >= 2:
                self.add_opposite_direction_targets(board)
        
        elif isinstance(result, tuple) and result[0] == "sunk":
            # Réinitialiser la stratégie car le navire est coulé
            self.hits = []
            self.hit_stack = []
            self.direction = None
    
    def identify_direction(self):
        """Identifie la direction du navire basée sur les touches existantes."""
        # Vérifier si les touches sont alignées horizontalement
        if all(hit[0] == self.hits[0][0] for hit in self.hits):
            self.direction = "horizontal"
        # Vérifier si les touches sont alignées verticalement
        elif all(hit[1] == self.hits[0][1] for hit in self.hits):
            self.direction = "vertical"
    
    def add_directional_targets(self, position, board):
        """
        Ajoute des cibles dans la direction identifiée.
        
        Args:
            position (tuple): Position (x, y) du dernier tir réussi
            board (Board): La grille de jeu
        """
        x, y = position
        # Vider la pile pour ne garder que les cibles dans la bonne direction
        self.hit_stack = []
        
        if self.direction == "horizontal":
            # Trouver les extrémités actuelles pour ce navire
            min_y = min(hit[1] for hit in self.hits)
            max_y = max(hit[1] for hit in self.hits)
            
            # Ajouter la case à gauche de la ligne
            left_pos = (x, min_y - 1)
            if 0 <= min_y - 1 < board.size and left_pos not in board.shots:
                self.hit_stack.append(left_pos)
            
            # Ajouter la case à droite de la ligne
            right_pos = (x, max_y + 1)
            if 0 <= max_y + 1 < board.size and right_pos not in board.shots:
                self.hit_stack.append(right_pos)
        
        elif self.direction == "vertical":
            # Trouver les extrémités actuelles pour ce navire
            min_x = min(hit[0] for hit in self.hits)
            max_x = max(hit[0] for hit in self.hits)
            
            # Ajouter la case au-dessus de la ligne
            top_pos = (min_x - 1, y)
            if 0 <= min_x - 1 < board.size and top_pos not in board.shots:
                self.hit_stack.append(top_pos)
            
            # Ajouter la case en-dessous de la ligne
            bottom_pos = (max_x + 1, y)
            if 0 <= max_x + 1 < board.size and bottom_pos not in board.shots:
                self.hit_stack.append(bottom_pos)
    
    def add_opposite_direction_targets(self, board):
        """
        Si un tir manque après avoir suivi une direction, essayez dans la direction opposée.
        
        Args:
            board (Board): La grille de jeu
        """
        if not self.hits:
            return
        
        if self.direction == "horizontal":
            # Trouver les extrémités actuelles
            hit_y_values = [hit[1] for hit in self.hits]
            min_y = min(hit_y_values)
            max_y = max(hit_y_values)
            x = self.hits[0][0]  # La ligne est la même pour toutes les touches
            
            # Vider la pile et ajouter seulement dans la direction opposée
            self.hit_stack = []
            
            # Si on a raté à droite, essayez à gauche
            if (x, max_y + 1) in board.shots and (x, min_y - 1) not in board.shots and 0 <= min_y - 1 < board.size:
                self.hit_stack.append((x, min_y - 1))
            # Si on a raté à gauche, essayez à droite
            elif (x, min_y - 1) in board.shots and (x, max_y + 1) not in board.shots and 0 <= max_y + 1 < board.size:
                self.hit_stack.append((x, max_y + 1))
        
        elif self.direction == "vertical":
            # Trouver les extrémités actuelles
            hit_x_values = [hit[0] for hit in self.hits]
            min_x = min(hit_x_values)
            max_x = max(hit_x_values)
            y = self.hits[0][1]  # La colonne est la même pour toutes les touches
            
            # Vider la pile et ajouter seulement dans la direction opposée
            self.hit_stack = []
            
            # Si on a raté en bas, essayez en haut
            if (max_x + 1, y) in board.shots and (min_x - 1, y) not in board.shots and 0 <= min_x - 1 < board.size:
                self.hit_stack.append((min_x - 1, y))
            # Si on a raté en haut, essayez en bas
            elif (min_x - 1, y) in board.shots and (max_x + 1, y) not in board.shots and 0 <= max_x + 1 < board.size:
                self.hit_stack.append((max_x + 1, y))
    
    def get_next_target(self, board):
        """
        Retourne la prochaine cible à viser.
        
        Args:
            board (Board): La grille de jeu
            
        Returns:
            tuple ou None: Position (x, y) à viser, ou None si pas de cible spécifique
        """
        if self.hit_stack:
            # S'il y a des cibles dans la pile, prendre la dernière ajoutée
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