from agent import Agent
from random_agent import RandomAgent
import visual_game_manager

# Exemple : Rouge = humain, Noir = agent AlphaBeta
# game_manager = visual_game_manager.VisualGameManager(red_agent=None, black_agent=AlphaBetaAgent(-1))

# Exemple : les deux agents s'affrontent automatiquement
game_manager = visual_game_manager.VisualGameManager(red_agent=Agent(1), black_agent=RandomAgent(-1))

game_manager.play()