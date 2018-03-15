"""
Boards for tic-tac-toe and super tic-tac-toe.

Based on: http://mcts.ai/code/python.html. Comment from original source:

This is a very simple implementation of the UCT Monte Carlo Tree Search
algorithm in Python 3.6. The function UCT(rootstate, itermax, verbose = False)
is towards the bottom of the code. It aims to have the clearest and simplest
possible code, and for the sake of clarity, the code is orders of magnitude
less efficient than it could be made, particularly by using a
state.GetRandomMove() or state.DoRandomRollout() function.

Example GameState classes for Nim, OXO and Othello are included to give some
idea of how you can write your own GameState use UCT in your 2-player game.
Change the game to be played in the UCTPlayGame() function at the bottom of the
code.

Written by Peter Cowling, Ed Powley, Daniel Whitehouse (University of York, UK)
September 2012.

Licence is granted to freely use and distribute for any sensible/legal purpose
so long as this comment remains in any distributed code.

For more information about Monte Carlo Tree Search check out our web site at
www.mcts.ai
"""
from game_state import GameState
from typing import List


class TicTacToe(GameState):
    """ The state of the tic tac toe game (the board).

    Squares in the board are in this arrangement:

        012
        345
        678

    where 0 = empty, 1 = player 1 (X), 2 = player 2 (O)
    """

    def __init__(self):
        super().__init__()
        self.board = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    def clone(self):
        """ Create a deep clone of this game state. """
        state = TicTacToe()
        state.player_just_moved = self.player_just_moved
        state.board = self.board[:]
        return state

    def do_move(self, move: int):
        """ Update a state by carrying out the given move.

        A 'move' is game (subclass) dependent. Must update player_just_moved.
        """
        assert move >= 0 and move <= 8 and move == int(move) and self.board[
            move] == 0
        self.player_just_moved = 3 - self.player_just_moved
        self.board[move] = self.player_just_moved

    def get_moves(self) -> List[int]:
        """ Get all possible moves from this state.

        Returns:
            A list of possible moves. A move is a square on the board (0 - 8).
        """
        return [i for i in range(9) if self.board[i] == 0]

    def get_result(self, player: int) -> float:
        """Get the game result from the viewpoint of player.

        Args:
            player: 1 or 2

        Returns:
            1.0 if player wins, 0.0 if player loses, 0.5 for a draw.

        """
        for (x, y, z) in [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7),
                          (2, 5, 8), (0, 4, 8), (2, 4, 6)]:
            if self.board[x] == self.board[y] == self.board[z]:
                if self.board[x] == player:
                    return 1.0
                else:
                    return 0.0
        if self.get_moves() == []:
            # Draw
            return 0.5
        # Should not be possible to get here.
        assert False

    def __repr__(self):
        """ Return a string representation of the board. """
        s = ""
        for i in range(9):
            s += ".XO"[self.board[i]]
            if i % 3 == 2:
                s += "\n"
        return s
