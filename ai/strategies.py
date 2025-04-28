"""
Stratégies d'IA.
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
        self.hits = []  # Touches non coulées
        self.targets = []  # Cibles prioritaires
        self.known_misses = set()  # Positions où on a déjà tiré et raté
        self.ships_sunk = []  # Positions des navires déjà coulés
    
    def process_result(self, position, result, board):
        """
        Traite le résultat d'un tir.
        
        Args:
            position (tuple): Position (x, y) du tir
            result (str ou tuple): Résultat du tir ('miss', 'hit' ou ('sunk', ship_name))
            board (Board): La grille de jeu
        """
        # Traiter selon le résultat
        if result == "hit":
            # Ajouter aux hits
            self.hits.append(position)
            
            self._add_adjacent_targets(position, board)
            
        elif result == "miss":
            # Ajouter aux misses connus
            self.known_misses.add(position)
            
            # Si on a des cibles qui ne sont pas valides à cause d'un miss, les retirer
            self.targets = [t for t in self.targets if t not in self.known_misses]
            
        elif isinstance(result, tuple) and result[0] == "sunk":
            # Trouver quels hits appartiennent au navire coulé
            sunk_ship = []
            for pos in self.hits:
                # Vérifier si ce hit appartient au navire qui vient d'être coulé
                for ship in board.ships:
                    if ship.name == result[1] and pos in ship.positions:
                        sunk_ship.append(pos)
            
            # Mettre à jour notre état interne
            for pos in sunk_ship:
                # Retirer ces positions des hits actifs
                if pos in self.hits:
                    self.hits.remove(pos)
                # Ajouter aux navires coulés
                self.ships_sunk.append(pos)
            
            # Nettoyer toutes les cibles adjacentes à ce navire
            self._clean_targets_around_sunk_ship(sunk_ship)
            
            # Réinitialiser les cibles si tous les navires actifs sont coulés
            if not self.hits:
                self.targets = []
    
    def _add_adjacent_targets(self, position, board):
        """Ajoute des cibles adjacentes à une position."""
        x, y = position
        
        # Les 4 directions possibles
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            target = (x + dx, y + dy)
            
            # Vérifier si la cible est valide
            if (0 <= target[0] < board.size and 
                0 <= target[1] < board.size and 
                target not in board.shots and
                target not in self.targets):
                
                # Si on a plusieurs hits, prioriser les cibles alignées
                if len(self.hits) > 1:
                    aligned = False
                    for hit in self.hits:
                        if hit != position:  # Différent du hit actuel
                            # Vérifier si alignés horizontalement
                            if hit[0] == position[0] and target[0] == position[0]:
                                aligned = True
                            # Vérifier si alignés verticalement
                            elif hit[1] == position[1] and target[1] == position[1]:
                                aligned = True
                    
                    # Si aligné, mettre en première position
                    if aligned:
                        self.targets.insert(0, target)
                    else:
                        self.targets.append(target)
                else:
                    # Sinon, juste ajouter à la fin
                    self.targets.append(target)
    
    def _clean_targets_around_sunk_ship(self, sunk_ship):
        """Nettoie les cibles autour d'un navire coulé."""
        if not sunk_ship:
            return
            
        # Calculer toutes les positions adjacentes au navire coulé
        adjacent_positions = set()
        for pos in sunk_ship:
            x, y = pos
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                adjacent_positions.add((x + dx, y + dy))
        
        # Retirer les positions du navire lui-même
        adjacent_positions = adjacent_positions - set(sunk_ship)
        
        # Retirer ces positions de nos cibles
        self.targets = [t for t in self.targets if t not in adjacent_positions]
    
    def get_next_target(self, board):
        """
        Retourne la prochaine cible à viser.
        
        Args:
            board (Board): La grille de jeu
            
        Returns:
            tuple ou None: Position (x, y) à viser, ou None si pas de cible
        """
        # Filtrer les cibles qui sont encore valides
        valid_targets = [t for t in self.targets if t in board.get_valid_moves()]
        
        # Si nous avons des cibles valides, prendre la première
        if valid_targets:
            target = valid_targets[0]
            self.targets.remove(target)
            return target
        
        # Si on n'a pas de cible mais des hits, générer de nouvelles cibles
        if self.hits and not valid_targets:
            for hit in self.hits:
                self._add_adjacent_targets(hit, board)
            
            # Réessayer de trouver une cible
            return self.get_next_target(board)
        
        return None
    
    def evaluate_move(self, move, board, data=None):
        """
        Évalue un coup.
        
        Args:
            move (tuple): Position (x, y) du coup à évaluer
            board (Board): La grille de jeu actuelle
            data (pandas.DataFrame, optional): Données historiques
            
        Returns:
            float: Score d'évaluation du coup
        """
        # Priorité absolue aux cibles dans notre liste
        if move in self.targets:
            return 100.0
        
        # Éviter les positions où on a déjà tiré et raté
        if move in self.known_misses:
            return -10.0
        
        # Vérifier si adjacent à un hit non coulé
        for hit in self.hits:
            x1, y1 = hit
            x2, y2 = move
            if (abs(x1 - x2) == 1 and y1 == y2) or (abs(y1 - y2) == 1 and x1 == x2):
                return 80.0
        
        # Éviter de tirer près des positions où on a déjà coulé un navire
        for pos in self.ships_sunk:
            x1, y1 = pos
            x2, y2 = move
            if (abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1):
                return 0.1  # Score très faible, mais pas négatif
        
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
        
        return hits / (hits + misses) * 10  # Multiplier par 10 pour donner plus de poids