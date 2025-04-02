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
        self.cutoffs = {}
        self.best_move = None
        self.time_limit = None

    def act(self, state, remaining_time):
        """
        Détermine le meilleur coup à jouer dans l'état actuel.

        Args:
            state (FenixState): L'état actuel du jeu.
            remaining_time (float): Temps restant pour jouer (en secondes).

        Returns:
            FenixAction: L'action choisie par l'agent.
        """
        self.time_limit = remaining_time * 0.9  # marge de sécurité
        start = time.perf_counter()
        self.best_move = None

        # adaptation de la profondeur
        if remaining_time < 5:
            depth = 1
        elif remaining_time < 15:
            depth = 2
        elif state.turn < 10:
            depth = 2
        else:
            depth = self.depth
            if len(state.pieces) < 10:
                depth += 1  # plus profond en fin de partie

        # killer moves init
        self.cutoffs = {}
        for i in range(depth + 1):
            self.cutoffs[i] = []

        score, move = self._alphabeta(state, depth, -math.inf, math.inf, True, start)

        if move:
            print("Move : ", move)
            return move
        if self.best_move:
            return self.best_move

        # fallback random
        actions = state.actions()
        if actions : 
            return random.choice(actions) 
        else: 
            return None

    def _alphabeta(self, state, depth, alpha, beta, maximizing, start):
        """
        Implémente l'algorithme Alpha-Beta avec élagage.

        Args:
            state (FenixState): L'état du jeu à analyser.
            depth (int): Profondeur actuelle de recherche.
            alpha (float): Valeur alpha pour l'élagage.
            beta (float): Valeur beta pour l'élagage.
            maximizing (bool): Indique si on maximise ou minimise.
            start (float): Temps de début de recherche.

        Returns:
            tuple: Score évalué (float), meilleure action (FenixAction or None).
        """
        if time.perf_counter() - start > self.time_limit:
            return self._evaluate(state), None  # trop long

        if depth == 0 or state.is_terminal():
            return self._evaluate(state), None

        key = state._hash()
        if key in self.memo and self.memo[key]['depth'] >= depth:
            entry = self.memo[key]
            if depth == self.depth and maximizing:
                self.best_move = entry['action']
            return entry['value'], entry['action']

        actions = self._order_actions(state, depth)
        best = None

        if maximizing:
            max_eval = -math.inf
            for action in actions:
                next_state = state.result(action)
                val, _ = self._alphabeta(next_state, depth - 1, alpha, beta, False, start)
                if val > max_eval:
                    max_eval = val
                    best = action
                    if depth == self.depth:
                        self.best_move = action
                    if action not in self.cutoffs[depth]:
                        self.cutoffs[depth] = [action] + self.cutoffs[depth][:1]
                alpha = max(alpha, val)
                if beta <= alpha:
                    break
            self.memo[key] = {'value': max_eval, 'action': best, 'depth': depth}
            return max_eval, best
        else:
            min_eval = math.inf
            for action in actions:
                next_state = state.result(action)
                val, _ = self._alphabeta(next_state, depth - 1, alpha, beta, True, start)
                if val < min_eval:
                    min_eval = val
                    best = action
                    if action not in self.cutoffs[depth]:
                        self.cutoffs[depth] = [action] + self.cutoffs[depth][:1]
                beta = min(beta, val)
                if beta <= alpha:
                    break
            self.memo[key] = {'value': min_eval, 'action': best, 'depth': depth}
            return min_eval, best

    def _order_actions(self, state, depth):
        """
        Trie les actions possibles selon des heuristiques : killer moves, captures, centralité.

        Args:
            state (FenixState): L'état courant du jeu.
            depth (int): Profondeur actuelle de recherche.

        Returns:
            list[FenixAction]: Liste triée des actions les plus prometteuses.
        """
        moves = state.actions()
        if not moves:
            return []

        ordered = []
        for m in moves:
            score = 0

            if m in self.cutoffs.get(depth, []):
                score += 1000

            for p in m.removed:
                val = abs(state.pieces.get(p, 0))
                score += 500 if val == 3 else 200 if val == 2 else 100

            end = m.end
            center = 3 - abs(3 - end[0]) - abs(4 - end[1])
            score += center * 5

            ordered.append((score, m))

        ordered.sort(reverse=True)
        return [m for _, m in ordered]

    def _evaluate(self, state):
        """
        Trie les actions possibles selon des heuristiques : killer moves, captures, centralité.

        Args:
            state (FenixState): L'état courant du jeu.
            depth (int): Profondeur actuelle de recherche.

        Returns:
            list[FenixAction]: Liste triée des actions les plus prometteuses.
        """
        if state.is_terminal():
            return state.utility(self.player) * 1000

        total = 0
        weights = {1: 10, 2: 30, 3: 1000}  # soldat, général, roi

        for pos, val in state.pieces.items():
            t = abs(val)
            owner = 1 if val > 0 else -1
            sign = 1 if owner == self.player else -1

            base = weights.get(t, 0)
            center_bonus = 3 - abs(3 - pos[0]) - abs(4 - pos[1])
            center_val = (2 if t > 1 else 1) * center_bonus * 2

            advance = 0
            if state.turn > 10:
                if owner == 1 and pos[0] < 3:
                    advance = 4 - pos[0]
                elif owner == -1 and pos[0] > 3:
                    advance = pos[0] - 3
                advance *= 3

            # mobilité intégrée ici
            mobility = 0
            for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                n = (pos[0] + dx, pos[1] + dy)
                if state._is_inside(n) and n not in state.pieces:
                    mobility += 1
            mobility *= 2 if owner == state.to_move() else 0

            # isolement (amis autour)
            friends = 0
            for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                n = (pos[0] + dx, pos[1] + dy)
                if n in state.pieces and state.pieces[n] * owner > 0:
                    friends += 1
            isolation = max(0, 4 - friends)

            score = base + center_val + advance + mobility - isolation
            total += sign * score

        # menaces adverses (résurrections)
        if state.can_create_king and state.to_move() == -self.player:
            total -= 500
        if state.can_create_general and state.to_move() == -self.player:
            total -= 100

        print("Évaluation finale:", total)

        return total
