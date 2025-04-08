import math
import random
import time
from fenix import FenixAction
from agent import Agent


class BaseAgent(Agent):
    def __init__(self, player, search_depth=3):
        """Agent utilisant l'algorithme alpha-bêta, avec une profondeur de recherche donnée."""
        super().__init__(player)
        self.depth = search_depth
        self.time_limit = None

    def act(self, state, remaining_time):
        """Décide du meilleur coup à jouer en fonction du temps restant et de l'état actuel."""
        start_time = time.perf_counter()
        moves = state.actions()

        if not moves:
            return None

        if remaining_time < 1 or len(moves) > 25:
            self.depth = 1
        elif remaining_time < 3 or len(moves) > 15:
            self.depth = 2
        else:
            self.depth = 3

        self.time_limit = start_time + min(1.2, remaining_time * 0.9)

        none, chosen_move = self.alpha_beta(state)

        if chosen_move in moves:
            return chosen_move

        return random.choice(moves)
    
    def heuristique(self, move, state):
        """
        Évalue rapidement un coup : favorise les captures importantes et les bonnes positions.
        Plus l'action capture, plus elle est prioritaire 
        roi > general > soldat 
        """
        points = 0
        piece_vals = {1: 2, 2: 5, 3: 10}

        for pos in move.removed:
            p = state.pieces.get(pos)
            if p:
                points += piece_vals.get(abs(p), 0)

        r, c = move.end
        mid_r, mid_c = state.dim[0] // 2, state.dim[1] // 2
        dist = abs(r - mid_r) + abs(c - mid_c)
        points += max(0, 5 - dist)

        return points

    def alpha_beta(self, state):
        """Recherche du meilleur coup via l'algorithme alpha-bêta."""

        def max_value(s, a, b, d):
            if time.perf_counter() > self.time_limit or d == 0 or s.is_terminal():
                return self.evaluate(s), None

            best_val, best_move = -math.inf, None
            options = sorted(s.actions(), key=lambda x: self.heuristique(x, s), reverse=True)

            for move in options:
                val, _ = min_value(s.result(move), a, b, d - 1)
                if val > best_val:
                    best_val, best_move = val, move
                    a = max(a, val)
                if best_val >= b:
                    break

            return best_val, best_move

        def min_value(s, a, b, d):
            if time.perf_counter() > self.time_limit or d == 0 or s.is_terminal():
                return self.evaluate(s), None

            best_val, best_move = math.inf, None
            options = sorted(s.actions(), key=lambda x: self.heuristique(x, s), reverse=True)

            for move in options:
                val, _ = max_value(s.result(move), a, b, d - 1)
                if val < best_val:
                    best_val, best_move = val, move
                    b = min(b, val)
                if best_val <= a:
                    break

            return best_val, best_move

        return max_value(state, -math.inf, math.inf, self.depth)

    def evaluate(self, state):
        """
        Donne un score à l'état du jeu :
        - Prend en compte les pièces, leur valeur et leur position
        - Bonus si l’adversaire n’a plus de roi
        - Bonus pour la protection du roi et la cohésion entre pièces alliées
        """

        score = 0
        allies = []
        king = None

        for position, piece in state.pieces.items():
            abs_val = abs(piece)
            val = {1: 1, 2: 3, 3: 5}.get(abs_val, 0) # soldat, general, roi 

            r, c = position
            center_dist = abs(r - state.dim[0] // 2) + abs(c - state.dim[1] // 2)
            val += max(0, 3 - center_dist)

            if piece * self.player > 0:
                score += val
                allies.append(position)
                if abs_val == 3:
                    king = position
            else:
                score -= val

        if king:
            around = [(king[0] + dx, king[1] + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if (dx, dy) != (0, 0)]
            protection = sum(0.5 for pos in around if pos in state.pieces and state.pieces[pos] * self.player > 0)
            score += protection

        close_bonus = 0
        for i in range(len(allies)):
            for j in range(i + 1, len(allies)):
                dist = abs(allies[i][0] - allies[j][0]) + abs(allies[i][1] - allies[j][1])
                if dist <= 2:
                    close_bonus += 0.3
        score += close_bonus

        if not state._has_king(-self.player):
            score += 50

        print("Evaluation : ", score)
        return score
