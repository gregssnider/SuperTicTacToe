"""
Abstract Game class for Monte Carlo Tree Search.

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
from abc import ABC, abstractmethod
from typing import List


class GameState(ABC):
    """ A state of the game, i.e. the game board.

    These are the only methods which are absolutely necessary to implement UCT
    in any 2-player, complete information, deterministic zero-sum game, although
    they can be enhanced and made quicker, for example by using a
    get_random_move() function to generate a random move during rollout.

    By convention, the players are numbered 1 and 2.

    Attributes:
        player_just_moved (int): The last player that played, 1 or 2.
    """

    def __init__(self):
        # At the root, pretend that player 2 just moved (in other words,
        # player 1 has the first move).
        self.player_just_moved = 2
        super().__init__()

    @abstractmethod
    def clone(self) -> 'GameState':
        """ Return a deep clone of this game state. """
        pass

    @abstractmethod
    def do_move(self, move: 'Move'):
        """ Update a state by carrying out the given move. A 'move' is
        game (subclass) dependent.

        Must update player_just_moved.
        """
        pass

    @abstractmethod
    def get_moves(self) -> List['Move']:
        """Get all possible moves from this state.

        Returns:
            List[Move]: A list of possible moves. 'Move' is subclass dependent.
        """
        pass

    @abstractmethod
    def get_result(self, player: int) -> float:
        """Get the game result from the viewpoint of player.

        Args:
            player: 1 or 2

        Returns:
            1.0 if player wins, 0.0 if player loses, 0.5 for a draw.

        """

        """ Get the game result from the viewpoint of player. 
        
        
        """
        pass

    @abstractmethod
    def __repr__(self):
        pass
