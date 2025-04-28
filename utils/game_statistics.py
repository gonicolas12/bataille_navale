"""
Classe pour générer des statistiques sur les parties jouées.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib as mpl
from datetime import datetime

class GameStatistics:
    """Classe pour générer des statistiques sur les parties jouées."""
    
    def __init__(self, game_data_file="data/game_data.csv"):
        """
        Initialise un nouveau gestionnaire de statistiques.
        
        Args:
            game_data_file (str, optional): Chemin vers le fichier de données de jeu.
                Par défaut "data/game_data.csv".
        """
        self.game_data_file = game_data_file
        
        if os.path.exists(game_data_file):
            self.game_data = pd.read_csv(game_data_file)
        else:
            self.game_data = pd.DataFrame()
    
    def reload_data(self):
        """Recharge les données du fichier CSV."""
        if os.path.exists(self.game_data_file):
            self.game_data = pd.read_csv(self.game_data_file)
    
    def get_wins_by_player(self):
        """
        Calcule le nombre de victoires par joueur.
        
        Returns:
            dict: Dictionnaire contenant le nombre de victoires par joueur
        """
        # On recharge les données pour avoir les plus récentes
        self.reload_data()
        
        if self.game_data.empty:
            return {"player": 0, "ai": 0}
        
        wins = {"player": 0, "ai": 0}
        
        # Obtenir tous les game_id uniques
        game_ids = self.game_data['game_id'].unique()
        
        for game_id in game_ids:
            # Obtenir les données de cette partie spécifique
            game_data = self.game_data[self.game_data['game_id'] == game_id]
            
            # Obtenir le dernier tour de cette partie
            last_turn = game_data['turn'].max()
            last_moves = game_data[game_data['turn'] == last_turn]
            
            # S'assurer qu'il y a au moins un coup dans le dernier tour
            if last_moves.empty:
                continue
                
            # Prendre le dernier coup du dernier tour
            last_move = last_moves.iloc[-1]
            
            # Si le dernier résultat est "sunk", alors le joueur qui a fait ce coup a gagné
            if last_move['result'] == 'sunk':
                winner = last_move['player']  # Le joueur qui a coulé le dernier navire est le gagnant
                wins[winner] += 1
        
        return wins
    
    def get_hit_miss_ratio(self):
        """
        Calcule le ratio de coups réussis/manqués par joueur.
        
        Returns:
            dict: Dictionnaire contenant le ratio de réussite par joueur
        """
        self.reload_data()
        
        if self.game_data.empty:
            return {"player": 0, "ai": 0}
        
        # Calculer les ratios pour chaque joueur
        result = {}
        for player in ["player", "ai"]:
            player_shots = self.game_data[self.game_data['player'] == player]
            
            # Ignorer les parties où le joueur n'a pas tiré
            if player_shots.empty:
                result[player] = 0
                continue
            
            hits = player_shots[player_shots['result'].isin(['hit', 'sunk'])].shape[0]
            total_shots = player_shots.shape[0]
            
            result[player] = hits / total_shots if total_shots > 0 else 0
        
        return result
    
    def get_average_game_length(self):
        """
        Calcule la durée moyenne des parties en nombre de tours.
        
        Returns:
            float: Durée moyenne des parties
        """
        self.reload_data()
        
        if self.game_data.empty:
            return 0
        
        # Grouper par game_id et compter le nombre de tours
        game_lengths = self.game_data.groupby('game_id')['turn'].max()
        
        return game_lengths.mean() if not game_lengths.empty else 0
    
    def get_shots_per_game(self):
        """
        Calcule le nombre moyen de tirs par partie pour chaque joueur.
        
        Returns:
            dict: Dictionnaire contenant le nombre moyen de tirs par partie pour chaque joueur
        """
        self.reload_data()
        
        if self.game_data.empty:
            return {"player": 0, "ai": 0}
        
        result = {}
        game_count = self.game_data['game_id'].nunique()
        
        for player in ["player", "ai"]:
            player_shots = self.game_data[self.game_data['player'] == player].shape[0]
            result[player] = player_shots / game_count if game_count > 0 else 0
        
        return result
    
    def get_win_rate(self):
        """
        Calcule le taux de victoire pour chaque joueur.
        
        Returns:
            dict: Dictionnaire contenant le taux de victoire pour chaque joueur
        """
        wins = self.get_wins_by_player()
        total_games = wins["player"] + wins["ai"]
        
        if total_games == 0:
            return {"player": 0, "ai": 0}
        
        return {
            "player": wins["player"] / total_games,
            "ai": wins["ai"] / total_games
        }
        
    def generate_heatmap(self, save_path=None):
        """
        Génère une heatmap des positions les plus ciblées.
        
        Args:
            save_path (str, optional): Chemin où sauvegarder l'image. Si None, affiche le graphique.
        """
        self.reload_data()
        
        if self.game_data.empty:
            return
        
        # Configurer matplotlib
        plt.style.use('dark_background')
        
        # Créer une matrice 10x10 pour stocker le nombre de tirs à chaque position
        player_heatmap = np.zeros((10, 10))
        ai_heatmap = np.zeros((10, 10))
        
        # Parcourir les données pour remplir les heatmaps
        for _, row in self.game_data.iterrows():
            if pd.notna(row['position']):  # Vérifier que la position n'est pas NaN
                position = row['position'].split(',')
                if len(position) == 2:  # Vérifier que la position est valide
                    try:
                        x, y = int(position[0]), int(position[1])
                        if 0 <= x < 10 and 0 <= y < 10:
                            if row['player'] == 'player':
                                player_heatmap[x][y] += 1
                            elif row['player'] == 'ai':
                                ai_heatmap[x][y] += 1
                    except ValueError:
                        # Ignorer les positions mal formatées
                        pass
        
        # Créer une figure avec deux sous-graphiques côte à côte
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
        fig.patch.set_facecolor('#0a192f')  # Couleur de fond
        
        # Sous-graphique pour le joueur
        ax1.set_facecolor('#172a45')  # Couleur de fond du graphique
        img1 = ax1.imshow(player_heatmap, cmap='hot', interpolation='nearest')
        ax1.set_title('Heatmap des Tirs du Joueur', color='white', fontsize=16, pad=15)
        
        # Sous-graphique pour l'IA
        ax2.set_facecolor('#172a45')  # Couleur de fond du graphique
        img2 = ax2.imshow(ai_heatmap, cmap='hot', interpolation='nearest')
        ax2.set_title('Heatmap des Tirs de l\'IA', color='white', fontsize=16, pad=15)
        
        # Ajouter des barres de couleur
        cbar1 = fig.colorbar(img1, ax=ax1, pad=0.01)
        cbar1.set_label('Nombre de tirs', color='white', fontsize=12, labelpad=15)
        cbar1.ax.tick_params(colors='white')
        
        cbar2 = fig.colorbar(img2, ax=ax2, pad=0.01)
        cbar2.set_label('Nombre de tirs', color='white', fontsize=12, labelpad=15)
        cbar2.ax.tick_params(colors='white')
        
        # Personnaliser les axes pour les deux graphiques
        for ax in [ax1, ax2]:
            # Convertir les indices de colonnes en lettres (A-J)
            column_labels = [chr(65 + i) for i in range(10)]
            ax.set_xticks(np.arange(10))
            ax.set_xticklabels(column_labels, fontsize=11, color='white')
            
            # Convertir les indices de lignes en nombres (1-10)
            row_labels = [str(i + 1) for i in range(10)]
            ax.set_yticks(np.arange(10))
            ax.set_yticklabels(row_labels, fontsize=11, color='white')
            
            # Ajouter des lignes de grille
            ax.grid(color='white', linestyle='-', linewidth=0.5, alpha=0.3)
            
            # Personnaliser les labels des axes
            ax.set_xlabel('Colonne', color='white', fontsize=12, labelpad=10)
            ax.set_ylabel('Ligne', color='white', fontsize=12, labelpad=10)
        
        # Ajouter un titre global
        fig.suptitle('Analyse des Positions Ciblées', fontsize=20, color='white', y=0.98)
        
        # Ajuster les marges et l'espacement
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def export_statistics_report(self, output_file="data/statistics_report.txt"):
        """
        Exporte un rapport textuel des statistiques.
        
        Args:
            output_file (str, optional): Chemin du fichier de sortie.
                Par défaut "data/statistics_report.txt".
        """
        # Recharger les données pour obtenir les statistiques les plus récentes
        self.reload_data()
        
        wins = self.get_wins_by_player()
        ratios = self.get_hit_miss_ratio()
        avg_length = self.get_average_game_length()
        win_rates = self.get_win_rate()
        shots_per_game = self.get_shots_per_game()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("================================================\n")
            f.write("   RAPPORT DE STATISTIQUES DE BATAILLE NAVALE    \n")
            f.write("================================================\n\n")
            
            f.write(f"Date du rapport: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Fichier de données: {self.game_data_file}\n\n")
            
            f.write("------------------------------------------------\n")
            f.write("1. RÉSUMÉ DES PARTIES\n")
            f.write("------------------------------------------------\n")
            total_games = wins["player"] + wins["ai"]
            f.write(f"   Total des parties jouées: {total_games}\n")
            f.write(f"   Durée moyenne d'une partie: {avg_length:.1f} tours\n\n")
            
            f.write("------------------------------------------------\n")
            f.write("2. BILAN DES VICTOIRES\n")
            f.write("------------------------------------------------\n")
            f.write(f"   Joueur: {wins['player']} victoires ({win_rates['player']*100:.1f}%)\n")
            f.write(f"   IA: {wins['ai']} victoires ({win_rates['ai']*100:.1f}%)\n\n")
            
            f.write("------------------------------------------------\n")
            f.write("3. PRÉCISION DES TIRS\n")
            f.write("------------------------------------------------\n")
            f.write(f"   Joueur: {ratios['player']*100:.1f}% de tirs réussis\n")
            f.write(f"   IA: {ratios['ai']*100:.1f}% de tirs réussis\n\n")
            
            f.write("------------------------------------------------\n")
            f.write("4. NOMBRE DE TIRS PAR PARTIE\n")
            f.write("------------------------------------------------\n")
            f.write(f"   Joueur: {shots_per_game['player']:.1f} tirs/partie\n")
            f.write(f"   IA: {shots_per_game['ai']:.1f} tirs/partie\n\n")
            
            # Ajouter des statistiques sur les parties individuelles
            if not self.game_data.empty and total_games > 0:
                f.write("------------------------------------------------\n")
                f.write("5. HISTORIQUE DES DERNIÈRES PARTIES\n")
                f.write("------------------------------------------------\n")
                
                # Obtenir la liste des parties uniques, triées par date (en supposant que game_id est basé sur la date)
                game_ids = sorted(self.game_data['game_id'].unique(), reverse=True)
                
                # Limiter à 5 dernières parties
                recent_games = game_ids[:min(5, len(game_ids))]
                
                for i, game_id in enumerate(recent_games, 1):
                    game_data = self.game_data[self.game_data['game_id'] == game_id]
                    max_turn = game_data['turn'].max()
                    last_move = game_data[game_data['turn'] == max_turn].iloc[0]
                    
                    # Déterminer le gagnant
                    winner = "Joueur" if last_move['player'] == 'player' and last_move['result'] == 'sunk' else "IA"
                    
                    # Obtenir la date du dernier tour
                    game_date = last_move['timestamp'] if 'timestamp' in last_move else "Date inconnue"
                    
                    f.write(f"   Partie #{i}: {game_date}\n")
                    f.write(f"   - Durée: {max_turn} tours\n")
                    f.write(f"   - Gagnant: {winner}\n")
                    
                    # Statistiques de précision
                    player_shots = game_data[game_data['player'] == 'player']
                    ai_shots = game_data[game_data['player'] == 'ai']
                    
                    player_hits = player_shots[player_shots['result'].isin(['hit', 'sunk'])].shape[0]
                    ai_hits = ai_shots[ai_shots['result'].isin(['hit', 'sunk'])].shape[0]
                    
                    player_accuracy = player_hits / len(player_shots) if len(player_shots) > 0 else 0
                    ai_accuracy = ai_hits / len(ai_shots) if len(ai_shots) > 0 else 0
                    
                    f.write(f"   - Précision Joueur: {player_accuracy*100:.1f}% ({player_hits}/{len(player_shots)})\n")
                    f.write(f"   - Précision IA: {ai_accuracy*100:.1f}% ({ai_hits}/{len(ai_shots)})\n\n")
            
            f.write("================================================\n")
            f.write("                FIN DU RAPPORT                  \n")
            f.write("================================================\n")