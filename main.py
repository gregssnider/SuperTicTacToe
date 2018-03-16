"""
Using Monte Carlo Tree Search to play Super Tic-Tac-Toe

The two players, 1 and 2, can be given different strengths (max number of
search iterations). The stronger player should win more often.

"""
from board import SuperTicTacToe
from play import play_game

player_1_strength = 1000
player_2_strength = 100
print('Super Tic-Tac-Toe')
print('    Player 1 (X) strength:', player_1_strength)
print('    Player 2 (O) strength:', player_2_strength)

game = SuperTicTacToe()
play_game(game, player_1_strength, player_2_strength, verbose=True);
