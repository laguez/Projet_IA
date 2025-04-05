from fenix import FenixAction
import math
import random
import time

class Agent:
    """
    Classe de base pour tous les agents.
    """

    def __init__(self, player):
        self.player = player

    def act(self, state, remaining_time):
        """
        Méthode à surcharger dans les sous-classes.
        """
        raise NotImplementedError


class AlphaBetaAgent(Agent):
    """
    Agent IA utilisant l'algorithme Alpha-Beta
    """

    def __init__(self, player, depth=3):
        """
        Initialise l'agent Alpha-Beta.

        Args:
            player (int): Le joueur associé à l'agent (1 ou -1).
            depth (int, optional): La profondeur maximale de recherche. Defaults to 3.
        """
        super().__init__(player)
        self.depth = depth
        self.memo = {}
        self.coups_coupures = {}
        self.meilleur_coup = None
        self.limite_temps = None

    def act(self, etat, temps_restant):
        """
        Détermine le meilleur coup à jouer dans l'état actuel.

        Args:
            etat (FenixState): L'état actuel du jeu.
            temps_restant (float): Temps restant pour jouer (en secondes).

        Returns:
            FenixAction: L'action choisie par l'agent.
        """
        self.limite_temps = temps_restant * 0.9  # marge de sécurité
        debut_temps = time.perf_counter()
        self.meilleur_coup = None

        if temps_restant < 5:
            profondeur = 1
        elif temps_restant < 15:
            profondeur = 2
        elif etat.turn < 10:
            profondeur = 2
        else:
            profondeur = self.depth
            if len(etat.pieces) < 10:
                profondeur += 1

        self.coups_coupures = {i: [] for i in range(profondeur + 1)}

        score, coup = self._alphabeta(etat, profondeur, -math.inf, math.inf, True, debut_temps)

        if coup:
            print("Coup choisi :", coup)
            return coup
        if self.meilleur_coup:
            return self.meilleur_coup

        actions_possibles = etat.actions()
        if actions_possibles:
            return random.choice(actions_possibles)
        else:
            return None

    def _alphabeta(self, etat, profondeur, alpha, beta, maximisant, debut_temps):
        """
        Implémente l'algorithme Alpha-Beta avec élagage.

        Args:
            etat (FenixState): L'état du jeu à analyser.
            profondeur (int): Profondeur actuelle de recherche.
            alpha (float): Valeur alpha pour l'élagage.
            beta (float): Valeur beta pour l'élagage.
            maximisant (bool): Indique si on maximise ou minimise.
            debut_temps (float): Temps de début de recherche.

        Returns:
            tuple: Score évalué (float), meilleure action (FenixAction or None).
        """
        if time.perf_counter() - debut_temps > self.limite_temps:
            return self._evaluate(etat), None

        if profondeur == 0 or etat.is_terminal():
            return self._evaluate(etat), None

        cle = etat._hash()
        if cle in self.memo and self.memo[cle]['depth'] >= profondeur:
            entree = self.memo[cle]
            if profondeur == self.depth and maximisant:
                self.meilleur_coup = entree['action']
            return entree['value'], entree['action']

        actions = self._order_actions(etat, profondeur)
        meilleur = None

        if maximisant:
            max_eval = -math.inf
            for action in actions:
                prochain_etat = etat.result(action)
                val, _ = self._alphabeta(prochain_etat, profondeur - 1, alpha, beta, False, debut_temps)
                if val > max_eval:
                    max_eval = val
                    meilleur = action
                    if profondeur == self.depth:
                        self.meilleur_coup = action
                    if action not in self.coups_coupures[profondeur]:
                        self.coups_coupures[profondeur] = [action] + self.coups_coupures[profondeur][:1]
                alpha = max(alpha, val)
                if beta <= alpha:
                    break
            self.memo[cle] = {'value': max_eval, 'action': meilleur, 'depth': profondeur}
            return max_eval, meilleur
        else:
            min_eval = math.inf
            for action in actions:
                prochain_etat = etat.result(action)
                val, _ = self._alphabeta(prochain_etat, profondeur - 1, alpha, beta, True, debut_temps)
                if val < min_eval:
                    min_eval = val
                    meilleur = action
                    if action not in self.coups_coupures[profondeur]:
                        self.coups_coupures[profondeur] = [action] + self.coups_coupures[profondeur][:1]
                beta = min(beta, val)
                if beta <= alpha:
                    break
            self.memo[cle] = {'value': min_eval, 'action': meilleur, 'depth': profondeur}
            return min_eval, meilleur

    def _order_actions(self, etat, profondeur):
        """
        Trie les actions possibles selon des heuristiques : killer moves, captures, centralité.

        Args:
            etat (FenixState): L'état courant du jeu.
            profondeur (int): Profondeur actuelle de recherche.

        Returns:
            list[FenixAction]: Liste triée des actions les plus prometteuses.
        """
        actions_possibles = etat.actions()
        if not actions_possibles:
            return []

        scores = []
        for action in actions_possibles:
            note = 0

            if action in self.coups_coupures.get(profondeur, []):
                note += 1000

            for pos_capture in action.removed:
                valeur_piece = abs(etat.pieces.get(pos_capture, 0))
                note += 500 if valeur_piece == 3 else 200 if valeur_piece == 2 else 100

            fin = action.end
            bonus_central = 3 - abs(3 - fin[0]) - abs(4 - fin[1])
            note += bonus_central * 5

            scores.append((note, action))

        scores.sort(reverse=True)
        actions_triees = []
        for _, action in scores:
            actions_triees.append(action)
        return actions_triees

    def _evaluate(self, etat):
        """
        Évalue l'état du jeu à l'aide d'une heuristique.

        Args:
            etat (FenixState): L'état courant du jeu.

        Returns:
            float: Score évalué pour l'état.
        """
        if etat.is_terminal():
            return etat.utility(self.player) * 1000

        total = 0
        poids_pieces = {1: 10, 2: 30, 3: 1000}  # soldat, général, roi

        for position, valeur in etat.pieces.items():
            type_piece = abs(valeur)
            proprio = 1 if valeur > 0 else -1
            signe = 1 if proprio == self.player else -1

            base = poids_pieces.get(type_piece, 0)
            bonus_central = 3 - abs(3 - position[0]) - abs(4 - position[1])
            val_centrale = (2 if type_piece > 1 else 1) * bonus_central * 2

            avancee = 0
            if etat.turn > 10:
                if proprio == 1 and position[0] < 3:
                    avancee = 4 - position[0]
                elif proprio == -1 and position[0] > 3:
                    avancee = position[0] - 3
                avancee *= 3

            mobilite = 0
            for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                voisin = (position[0] + dx, position[1] + dy)
                if etat._is_inside(voisin) and voisin not in etat.pieces:
                    mobilite += 1
            mobilite *= 2 if proprio == etat.to_move() else 0

            allies = 0
            for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                voisin = (position[0] + dx, position[1] + dy)
                if voisin in etat.pieces and etat.pieces[voisin] * proprio > 0:
                    allies += 1
            isolement = max(0, 4 - allies)

            score = base + val_centrale + avancee + mobilite - isolement
            total += signe * score

        if etat.can_create_king and etat.to_move() == -self.player:
            total -= 500
        if etat.can_create_general and etat.to_move() == -self.player:
            total -= 100

        print("Évaluation finale:", total)

        return total
