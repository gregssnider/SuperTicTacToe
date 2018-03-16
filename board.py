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
from typing import List, Tuple
from copy import deepcopy
from game_state import GameState


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
    """ The state of the 'super tic tac toe' game (the board).

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
        result = self.sub_board_result(self.player_just_moved, sub_board)
        if result == 1.0:
            print('a board has been won')
            self.sub_boards_won[self.player_just_moved] += 1
            import sys
            sys.exit(1)
        '''
        elif result == 0.0:
            print('a board has been won')
            self.sub_boards_won[3 - self.player_just_moved] += 1
        else:
            pass
        '''

    def sub_board_is_available(self, sub_board):
        # If won or lost, it's dead.
        if self.sub_board_result(1, sub_board) == 1.0:
            return False
        if self.sub_board_result(2, sub_board) == 1.0:
            return False

        # If all squares filled, it's dead.
        for i in range(9):
            if self.board[sub_board][i] == 0:
                return True
        return False
        
    def get_moves(self) -> List[Tuple[int]]:
        """ Get all possible moves from this state.

        Returns:
            A list of possible moves.
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

    def sub_board_result(self, player: int, sub_board: int) -> float:
        """Get the result of a single sub_board (a single tic tac toe game)
        from the viewpoint of player.

        Args:
            player: 1 or 2
            sub_board: The index of the sub_board to check (0 - 8)

        Returns:
            1.0 if player wins, 0.0 if player loses, 0.5 for a draw.

        """
        sub_board = self.board[sub_board]
        for (x, y, z) in [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7),
                          (2, 5, 8), (0, 4, 8), (2, 4, 6)]:
            if sub_board[x] == sub_board[y] == sub_board[z]:
                if self.board[x] == player:
                    return 1.0
                else:
                    return 0.0

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

