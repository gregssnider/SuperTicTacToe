"""
Monte Carlo Tree Search for game play

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
import math
import random
from game_state import GameState


class Node:
    """ A node in the game tree. 
    
    Note wins is always from the viewpoint of player_just_moved.
    Crashes if state not specified.
    """

    def __init__(self, move=None, parent: 'Node'=None, state: GameState=None):
        """Construct a node.
        
        Args:
            move: The move that got us to this node - "None" for the root node
            parent: None for the root node. 
            state: 
        """
        self.move = move  # 
        self.parent_node = parent  # "None" for the root node
        self.child_nodes = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = state.get_moves()  # future child nodes
        self.player_just_moved = state.player_just_moved  # the only part of the state that the Node needs later

    def select_child(self) -> 'Node':
        """ Use the UCB1 formula to select a child node. 
        
        Often a constant UCTK is applied so we have lambda c: c.wins/c.visits + 
        UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
        exploration versus exploitation.
        """
        s = sorted(self.child_nodes,
                   key=lambda c: c.wins / c.visits + math.sqrt(
                       2 * math.log(self.visits) / c.visits))[-1]
        return s

    def add_child(self, move, s: GameState) -> 'Node':
        """ Remove m from untried_moves and add a new child node for this move.
            Return the added child node
        """
        n = Node(move=move, parent=self, state=s)
        self.untried_moves.remove(move)
        self.child_nodes.append(n)
        return n

    def update(self, result):
        """ Update this node.
        
        One additional visit and result additional wins. 
        Result must be from the viewpoint of player_just_moved.
        """
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(
            self.visits) + " U:" + str(self.untried_moves) + "]"

    def tree_to_string(self, indent) -> str:
        """ Convert a tree to a string.""" 
        s = self.indent_string(indent) + str(self)
        for c in self.child_nodes:
            s += c.tree_to_string(indent + 1)
        return s

    def indent_string(self, indent) -> str:
        s = "\n"
        for i in range(1, indent + 1):
            s += "| "
        return s

    def children_to_string(self):
        s = ""
        for c in self.child_nodes:
            s += str(c) + "\n"
        return s


def search(rootstate: GameState, itermax: int, verbose=False) -> 'Move':
    """ Do a UCT search.

    Assumes 2 alternating players (player 1 starts), with game results in the 
    range [0.0, 1.0].
    
    Args:
        rootstate: Starting state. 
        itermax: Iterations to search.
        verbose: True => print stuff out.

    Returns:
        The move that was most visited.
    """
    rootnode = Node(state=rootstate)

    for i in range(itermax):
        node = rootnode
        state = rootstate.clone()

        # Select
        while node.untried_moves == [] and node.child_nodes != []:
            # node is fully expanded and non-terminal
            node = node.select_child()
            state.do_move(node.move)

        # Expand
        if node.untried_moves != []:  
            # We can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untried_moves)
            state.do_move(m)
            # add child and descend tree
            node = node.add_child(m, state)

        # Rollout - this can often be made orders of magnitude quicker 
        # using a state.GetRandomMove() function
        while state.get_moves() != []:  # while state is non-terminal
            state.do_move(random.choice(state.get_moves()))

        # Backpropagate from the expanded node and work back to the root.
        while node != None:
            # state is terminal. Update node with result from POV of 
            # node.player_just_moved
            node.update(state.get_result(node.player_just_moved))
            node = node.parent_node

    # Output some information about the tree - can be omitted
    '''
    if (verbose):
        print(rootnode.tree_to_string(0))
    else:
        print(rootnode.children_to_string())
    '''

    # return the move that was most visited
    return sorted(rootnode.child_nodes, key=lambda c: c.visits)[-1].move  


def play_game(state: GameState):
    """ Play a sample game between two UCT players where each player gets a different number
        of UCT iterations (= simulations = tree nodes).
    """
    move = 1
    while (state.get_moves() != []):
        if state.player_just_moved == 1:
            # Player 2
            m = search(rootstate=state, itermax=10, verbose=False)
        else:
            # Player 1
            m = search(rootstate=state, itermax=1000, verbose=False)
        state.do_move(m)
        print("Move", move, 'player', state.player_just_moved)
        move += 1
        print(str(state))
    if state.get_result(state.player_just_moved) == 1.0:
        print("Player " + str(state.player_just_moved) + " wins!")
    elif state.get_result(state.player_just_moved) == 0.0:
        print("Player " + str(3 - state.player_just_moved) + " wins!")
    else:
        print("Nobody wins!")
