"""
Classe gérant le déroulement du jeu.
"""

from datetime import datetime
import pandas as pd
from models.board import Board
from models.ship import Ship
from ai.ai_player import AIPlayer

class GameManager:
    """Classe gérant le déroulement du jeu."""
    
    def __init__(self, data_file="data/game_data.csv"):
        """
        Initialise un nouveau gestionnaire de jeu.
        
        Args:
            data_file (str, optional): Chemin vers le fichier de données.
                Par défaut "data/game_data.csv".
        """
        self.player_board = Board()
        self.ai_board = Board()
        self.ai_player = AIPlayer(data_file)
        self.game_id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.turn = 0
        
        # Liste des navires à placer
        self.ships_config = [
            {"name": "Porte-avions", "size": 5},
            {"name": "Croiseur", "size": 4},
            {"name": "Contre-torpilleur", "size": 3},
            {"name": "Sous-marin", "size": 3},
            {"name": "Torpilleur", "size": 2}
        ]
    
    def initialize_game(self):
        """
        Initialise le jeu en plaçant les navires.
        
        Returns:
            bool: True si l'initialisation a réussi, False sinon
        """
        # Placer les navires de l'IA
        for ship_config in self.ships_config:
            ship = Ship(ship_config["name"], ship_config["size"])
            if not self.ai_board.place_ship_randomly(ship):
                return False
        
        # Placer les navires du joueur (de façon aléatoire aussi)
        for ship_config in self.ships_config:
            ship = Ship(ship_config["name"], ship_config["size"])
            if not self.player_board.place_ship_randomly(ship):
                return False
                
        return True
    
    def player_turn(self, position):
        """
        Gère le tour du joueur.
        
        Args:
            position (tuple): Position (x, y) du tir du joueur
            
        Returns:
            str ou tuple: Le résultat du tir ('miss', 'hit', 'already_shot' ou ('sunk', ship_name))
        """
        self.turn += 1
        
        # Le joueur tire sur la grille de l'IA
        result = self.ai_board.receive_shot(position)
        
        # Enregistrer le coup dans les données du jeu
        self._record_move("player", position, result)
        
        return result
    
    def ai_turn(self):
        """
        Gère le tour de l'IA.
        
        Returns:
            tuple: La position (x, y) du tir de l'IA et son résultat
        """
        # L'IA évalue les coups possibles et choisit le meilleur
        position = self.ai_player.evaluate_moves(self.player_board)
        
        # L'IA tire sur la grille du joueur
        result = self.player_board.receive_shot(position)
        
        # Mettre à jour la stratégie de l'IA en fonction du résultat
        self.ai_player.process_shot_result(position, result, self.player_board)
        
        # Enregistrer le coup dans les données du jeu
        self._record_move("ai", position, result)
        
        return position, result
    
    def _record_move(self, player, position, result):
        """
        Enregistre un coup dans l'historique des parties.
        
        Args:
            player (str): Le joueur qui a effectué le coup ('player' ou 'ai')
            position (tuple): Position (x, y) du tir
            result (str ou tuple): Le résultat du tir
        """
        x, y = position
        
        # Si le résultat est un tuple (dans le cas d'un navire coulé), extraire juste le type de résultat
        result_type = result[0] if isinstance(result, tuple) else result
        
        # Créer une nouvelle ligne pour le DataFrame
        new_data = {
            'game_id': self.game_id,
            'turn': self.turn,
            'player': player,
            'position': f"{x},{y}",
            'result': result_type,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'game_state': self._get_game_state(player)
        }
        
        # Ajouter la nouvelle ligne au DataFrame
        self.ai_player.game_data = pd.concat([self.ai_player.game_data, pd.DataFrame([new_data])], ignore_index=True)
        
        # Sauvegarder le DataFrame dans le fichier CSV
        self.ai_player.game_data.to_csv(self.ai_player.game_data_file, index=False)
    
    def _get_game_state(self, player):
        """
        Retourne une représentation de l'état du jeu.
        
        Args:
            player (str): Le joueur concerné ('player' ou 'ai')
            
        Returns:
            str: Une chaîne représentant l'état du jeu
        """
        if player == "player":
            return ";".join(f"{x},{y}" for x, y in self.ai_board.shots)
        else:
            return ";".join(f"{x},{y}" for x, y in self.player_board.shots)
    
    def is_game_over(self):
        """
        Vérifie si le jeu est terminé.
        
        Returns:
            bool: True si le jeu est terminé, False sinon
        """
        return self.player_board.all_ships_sunk() or self.ai_board.all_ships_sunk()
    
    def get_winner(self):
        """
        Retourne le gagnant du jeu.
        
        Returns:
            str ou None: 'player' si le joueur a gagné, 'ai' si l'IA a gagné, None si le jeu n'est pas terminé
        """
        if self.player_board.all_ships_sunk():
            return "ai"
        if self.ai_board.all_ships_sunk():
            return "player"
        return None