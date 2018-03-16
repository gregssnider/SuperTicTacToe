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
from copy import deepcopy
from typing import List, Tuple


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


class SuperTicTacToe(GameState):
    """ The state of a 'super tic tac toe' game (the board).

    Attributes:
        board (List[List[int]]):
            Squares are specified with a tuple of indices. The first index
            specifies the tic-tac-toe game within the larger 3 x 3 grid. The
            second index specifies the square within that game:

                 first_index           second_index

                                     012   012   012
                0     1     2        345   345   345
                                     678   678   678

                                     012   012   012
                3     4     5        345   345   345
                                     678   678   678

                                     012   012   012
                6     7     8        345   345   345
                                     678   678   678

            For each square: 0 => empty, 1 => player 1 (X), 2 => player 2 (O)

        sub_boards_won (List[int]): The number of 'sub boards' (tic tac toe
            games) won by the two players.

        squares_played (int): The number of squares that have been marked with
            an 'X' or an 'O'.

        last_square_played (int): The index of the last square played in
            sub board. Needed because this index specifies the sub board that
            the next player must mark (if available for marking).
    """

    def __init__(self):
        super().__init__()
        self.board = [
            [0] * 9, [0] * 9, [0] * 9,
            [0] * 9, [0] * 9, [0] * 9,
            [0] * 9, [0] * 9, [0] * 9
        ]
        self.sub_boards_won = [0, 0, 0]
        self.squares_played = 0
        self.last_square_played = 0

    def clone(self):
        """ Create a deep clone of this game state. """
        state = SuperTicTacToe()
        state.player_just_moved = self.player_just_moved
        state.board = deepcopy(self.board)
        state.sub_boards_won = deepcopy(self.sub_boards_won)
        state.squares_played = self.squares_played
        state.last_square_played = 0
        return state

    def do_move(self, move: (int, int)):
        """ Update state by carrying out the given move.

        Args:
            move: The (sub_board, square) indices for the square to be marked
                with an 'X' or an 'O'.
        """
        assert len(move) == 2
        sub_board = move[0]
        square = move[1]
        assert self.board[sub_board][square] == 0

        # Update state of board.
        self.player_just_moved = 3 - self.player_just_moved
        self.last_square_played = square
        self.squares_played += 1
        self.board[sub_board][square] = self.player_just_moved

        # Check if player has won a sub_board (tic tac toe game).
        result = self.wins_sub_board(self.player_just_moved, sub_board)
        if result:
            self.sub_boards_won[self.player_just_moved] += 1

    def sub_board_is_available(self, sub_board) -> bool:
        """Check if a sub_board is available for writing.

        Args:
            sub_board: Index of desired sub board.

        Returns:
            True if sub board can be written.
        """
        # If won or lost, it's dead, can't be written anymore.
        if self.wins_sub_board(1, sub_board):
            return False
        if self.wins_sub_board(2, sub_board):
            return False

        # If all squares filled, it's dead, can't be written anymore.
        for i in range(9):
            if self.board[sub_board][i] == 0:
                return True
        return False

    def get_moves(self) -> List[Tuple[int]]:
        """ Get all possible moves from this state.

        Returns:
            A list of possible moves. A move is an (int, int) tuple where the
            first value is the index of the sub_board (tic tac toe game) and the
            second value is the index of the square in that game to be marked.
        """
        if self.sub_boards_won[1] == 3 or self.sub_boards_won[2] == 3:
            # Game over, someone has already won.
            return []
        elif self.squares_played == 0:
            # All squares are eligible to be marked.
            moves = []
            for i in range(9):
                for j in range(9):
                    moves.append((i, j))
            return moves
        elif self.sub_board_is_available(self.last_square_played):
            # Only squares in sub_board are legal.
            moves = []
            for i in range(9):
                if self.board[self.last_square_played][i] == 0:
                    moves.append((self.last_square_played, i))
            return moves
        else:
            # Any square in any available sub board is legal
            moves = []
            for sub_board in range(9):
                if self.sub_board_is_available(sub_board):
                    for i in range(9):
                        if self.board[sub_board][i] == 0:
                            moves.append((sub_board, i))
            return moves

    def get_result(self, player: int):
        """Get the result of the game from the viewpoint of player.

        Args:
            player: 1 or 2
            sub_board: The index of the sub_board to check (0 - 8)

        Returns:
            1.0 if player wins, 0.0 if player loses, 0.5 for a draw.

        """
        if self.sub_boards_won[player] == 3:
            return 1.0
        elif self.sub_boards_won[3 - player] == 3:
            return 0.0
        else:
            return 0.5

    def wins_sub_board(self, player: int, sub_board: int) -> bool:
        """Check if a player has won a sub board (tic tac toe game).

        Args:
            player: 1 or 2
            sub_board: The index of the sub_board to check (0 - 8)

        Returns:
            True if player has won the sub board.

        """
        assert player == 1 or player == 2
        sub = self.board[sub_board]
        for (x, y, z) in [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7),
                          (2, 5, 8), (0, 4, 8), (2, 4, 6)]:
            if sub[x] == sub[y] == sub[z]:
                if sub[x] == player:
                    return True
        return False

    def __repr__(self):
        """ Return a string representation of the board. """

        def mark(player: int) -> str:
            return ".XO"[player]

        b = self.board
        s = ""

        s += mark(b[0][0]) + mark(b[0][1]) + mark(b[0][2]) + ' '
        s += mark(b[1][0]) + mark(b[1][1]) + mark(b[1][2]) + ' '
        s += mark(b[2][0]) + mark(b[2][1]) + mark(b[2][2]) + ' ' + '\n'

        s += mark(b[0][3]) + mark(b[0][4]) + mark(b[0][5]) + ' '
        s += mark(b[1][3]) + mark(b[1][4]) + mark(b[1][5]) + ' '
        s += mark(b[2][3]) + mark(b[2][4]) + mark(b[2][5]) + ' ' + '\n'

        s += mark(b[0][6]) + mark(b[0][7]) + mark(b[0][8]) + ' '
        s += mark(b[1][6]) + mark(b[1][7]) + mark(b[1][8]) + ' '
        s += mark(b[2][6]) + mark(b[2][7]) + mark(b[2][8]) + ' ' + '\n'

        s += '\n'

        s += mark(b[3][0]) + mark(b[3][1]) + mark(b[3][2]) + ' '
        s += mark(b[4][0]) + mark(b[4][1]) + mark(b[4][2]) + ' '
        s += mark(b[5][0]) + mark(b[5][1]) + mark(b[5][2]) + ' ' + '\n'

        s += mark(b[3][3]) + mark(b[3][4]) + mark(b[3][5]) + ' '
        s += mark(b[4][3]) + mark(b[4][4]) + mark(b[4][5]) + ' '
        s += mark(b[5][3]) + mark(b[5][4]) + mark(b[5][5]) + ' ' + '\n'

        s += mark(b[3][6]) + mark(b[3][7]) + mark(b[3][8]) + ' '
        s += mark(b[4][6]) + mark(b[4][7]) + mark(b[4][8]) + ' '
        s += mark(b[5][6]) + mark(b[5][7]) + mark(b[5][8]) + ' ' + '\n'

        s += '\n'

        s += mark(b[6][0]) + mark(b[6][1]) + mark(b[6][2]) + ' '
        s += mark(b[7][0]) + mark(b[7][1]) + mark(b[7][2]) + ' '
        s += mark(b[8][0]) + mark(b[8][1]) + mark(b[8][2]) + ' ' + '\n'

        s += mark(b[6][3]) + mark(b[6][4]) + mark(b[6][5]) + ' '
        s += mark(b[7][3]) + mark(b[7][4]) + mark(b[7][5]) + ' '
        s += mark(b[8][3]) + mark(b[8][4]) + mark(b[8][5]) + ' ' + '\n'

        s += mark(b[6][6]) + mark(b[6][7]) + mark(b[6][8]) + ' '
        s += mark(b[7][6]) + mark(b[7][7]) + mark(b[7][8]) + ' '
        s += mark(b[8][6]) + mark(b[8][7]) + mark(b[8][8]) + ' ' + '\n'

        s += '\n\n'
        return s

