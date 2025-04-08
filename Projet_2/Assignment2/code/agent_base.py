from fenix import FenixAction
import math
import random
import time


class Agent:
    def __init__(self, player):
        """Initialise l'agent avec son identifiant de joueur (1 ou -1)."""
        self.player = player

    def act(self, state, remaining_time):
        """Doit être redéfini dans les sous-classes pour choisir une action."""
        raise NotImplementedError


class AlphaBetaAgent(Agent):
    def __init__(self, player, depth=3):
        """Initialise l'agent alpha-bêta avec une profondeur de recherche."""
        super().__init__(player)
        self.depth = depth
        self.time_limit = None

    def act(self, state, remaining_time):
        """Retourne le meilleur coup trouvé avec alpha-bêta, ou un coup aléatoire sinon."""
        self.time_limit = time.perf_counter() + remaining_time * 0.9
        _, move = self.alpha_beta_search(state)
        return move if move else random.choice(state.actions())
    
    def heuristic(self, action, state):
        """
        Heuristique simple : favorise les actions qui capturent des pièces.
        """
        # Plus l'action capture, plus elle est prioritaire 
        # roi > general > soldat 
        return len(action.removed)  
        
    def alpha_beta_search(self, state):
        """Lance l'algorithme alpha-bêta et retourne (valeur, coup optimal)."""
        player = self.player

        def max_value(state, alpha, beta, depth):
            """Tour du joueur actuel : cherche à maximiser la valeur."""
            if time.perf_counter() > self.time_limit or depth == 0 or state.is_terminal():
                return self.evaluate(state), None
            v, best_move = -math.inf, None
            actions = sorted(state.actions(), key=lambda a: self.heuristic(a, state), reverse=True)
            for a in actions:
                v2, _ = min_value(state.result(a), alpha, beta, depth - 1)
                if v2 > v:
                    v, best_move = v2, a
                    alpha = max(alpha, v)
                if v >= beta:
                    return v, best_move
            return v, best_move

        def min_value(state, alpha, beta, depth):
            """Tour de l'adversaire : cherche à minimiser la valeur."""
            if time.perf_counter() > self.time_limit or depth == 0 or state.is_terminal():
                return self.evaluate(state), None
            v, best_move = math.inf, None
            actions = sorted(state.actions(), key=lambda a: self.heuristic(a, state), reverse=True)
            for a in actions:
                v2, _ = max_value(state.result(a), alpha, beta, depth - 1)
                if v2 < v:
                    v, best_move = v2, a
                    beta = min(beta, v)
                if v <= alpha:
                    return v, best_move
            return v, best_move

        return max_value(state, -math.inf, math.inf, self.depth)

    def evaluate(self, state):
        """Évalue l'état du plateau : pondération selon les types de pièces."""
        total = 0
        for value in state.pieces.values():
            abs_val = abs(value)
            
            if abs_val == 1:
                weight = 1  # soldat
            elif abs_val == 2:
                weight = 3  # general

            elif abs_val == 3:
                weight = 5  # roi

            else:
                weight = 0  # au cas ou

            if value * self.player > 0:
                total += weight
            else:
                total -= weight
                
        print("Evaluation : ", total)
        return total

