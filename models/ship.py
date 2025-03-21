"""
Classe représentant un navire dans le jeu de bataille navale.
"""

class Ship:
    """Classe représentant un navire dans le jeu de bataille navale."""
    
    def __init__(self, name, size):
        """
        Initialise un nouveau navire.
        
        Args:
            name (str): Nom du navire
            size (int): Taille du navire
        """
        self.name = name
        self.size = size
        self.positions = []  # Liste des positions occupées par le navire [(x1, y1), (x2, y2), ...]
        self.hits = []  # Liste des positions touchées [(x, y), ...]
        
    def is_placed(self):
        """
        Vérifie si le navire a été placé sur la grille.
        
        Returns:
            bool: True si le navire est placé, False sinon
        """
        return len(self.positions) == self.size
        
    def is_sunk(self):
        """
        Vérifie si le navire est coulé.
        
        Returns:
            bool: True si le navire est coulé, False sinon
        """
        return len(self.hits) == self.size
    
    def place(self, positions):
        """
        Place le navire aux positions spécifiées.
        
        Args:
            positions (list): Liste de tuples (x, y) représentant les positions du navire
            
        Raises:
            ValueError: Si le nombre de positions ne correspond pas à la taille du navire
        """
        if len(positions) != self.size:
            raise ValueError(f"Le nombre de positions ({len(positions)}) ne correspond pas à la taille du navire ({self.size})")
        self.positions = positions
    
    def hit(self, position):
        """
        Enregistre un coup reçu et retourne True si le navire est touché, False sinon.
        
        Args:
            position (tuple): Position (x, y) du tir
            
        Returns:
            bool: True si le navire est touché, False sinon
        """
        if position in self.positions and position not in self.hits:
            self.hits.append(position)
            return True
        return False