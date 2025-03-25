"""
Classe pour générer des statistiques sur les parties jouées de bataille navale.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

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
        # D'abord, on recharge les données pour avoir les plus récentes
        self.reload_data()
        
        if self.game_data.empty:
            return {"player": 0, "ai": 0}
        
        # Identifier les parties terminées (où un joueur a gagné)
        # Pour cela, on groupe par game_id et on prend le dernier tour
        game_results = self.game_data.groupby('game_id').apply(
            lambda x: x.sort_values('turn', ascending=False).iloc[0]
        )
        
        # Si player == "player" a fait un "sunk" au dernier tour, alors "ai" gagne
        # Si player == "ai" a fait un "sunk" au dernier tour, alors "player" gagne
        
        wins = {"player": 0, "ai": 0}
        
        for _, row in game_results.iterrows():
            if row['result'] == 'sunk':
                # Si le joueur a coulé un navire au dernier tour, l'IA a perdu
                if row['player'] == 'player':
                    wins['player'] += 1
                # Si l'IA a coulé un navire au dernier tour, le joueur a perdu
                elif row['player'] == 'ai':
                    wins['ai'] += 1
        
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
        
    def generate_heatmap(self, save_path=None):
        """
        Génère une heatmap des positions les plus ciblées.
        
        Args:
            save_path (str, optional): Chemin où sauvegarder l'image. Si None, affiche le graphique.
        """
        self.reload_data()
        
        if self.game_data.empty:
            return
        
        # Créer une matrice 10x10 pour stocker le nombre de tirs à chaque position
        heatmap_data = np.zeros((10, 10))
        
        # Parcourir les données pour remplir la heatmap
        for _, row in self.game_data.iterrows():
            if pd.notna(row['position']):  # Vérifier que la position n'est pas NaN
                position = row['position'].split(',')
                if len(position) == 2:  # Vérifier que la position est valide
                    try:
                        x, y = int(position[0]), int(position[1])
                        if 0 <= x < 10 and 0 <= y < 10:
                            heatmap_data[x][y] += 1
                    except ValueError:
                        # Ignorer les positions mal formatées
                        pass
        
        plt.figure(figsize=(10, 8))
        plt.imshow(heatmap_data, cmap='hot', interpolation='nearest')
        plt.colorbar(label='Nombre de tirs')
        plt.title('Heatmap des positions ciblées')
        plt.xlabel('Colonne')
        plt.ylabel('Ligne')
        
        # Ajout des lignes de grille
        plt.grid(color='black', linestyle='-', linewidth=0.5)
        
        # Ajout des indices de lignes et colonnes
        plt.xticks(np.arange(10))
        plt.yticks(np.arange(10))
        
        if save_path:
            plt.savefig(save_path)
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
        wins = self.get_wins_by_player()
        ratios = self.get_hit_miss_ratio()
        avg_length = self.get_average_game_length()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=== RAPPORT DE STATISTIQUES DE BATAILLE NAVALE ===\n\n")
            f.write(f"Date du rapport: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("1. VICTOIRES\n")
            f.write(f"   Joueur: {wins['player']} victoires\n")
            f.write(f"   IA: {wins['ai']} victoires\n\n")
            
            f.write("2. PRÉCISION\n")
            f.write(f"   Joueur: {ratios['player']*100:.1f}% de tirs réussis\n")
            f.write(f"   IA: {ratios['ai']*100:.1f}% de tirs réussis\n\n")
            
            f.write("3. DURÉE DES PARTIES\n")
            f.write(f"   Durée moyenne: {avg_length:.1f} tours\n\n")
            
            # Ajouter des statistiques supplémentaires si disponibles
            if not self.game_data.empty:
                total_games = self.game_data['game_id'].nunique()
                total_shots = len(self.game_data)
                f.write("4. STATISTIQUES GÉNÉRALES\n")
                f.write(f"   Nombre total de parties: {total_games}\n")
                f.write(f"   Nombre total de tirs: {total_shots}\n")
            
            f.write("\n=== FIN DU RAPPORT ===\n")