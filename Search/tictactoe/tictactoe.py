"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)
    return X if x_count == o_count else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    return {(i, j) for i in range(3) for j in range(3) if board[i][j] is EMPTY}


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    # Raise an exception if action is out of range
    if action[0] not in range(3) or action[1] not in range(3):
        raise ValueError("Action out of bounds")
    
    # Raise an exception if tile is not empty
    if board[action[0]][action[1]] is not EMPTY:
        raise ValueError("Invalid action")
    
    new_board = [row[:] for row in board]  # Deep copy of the board
    new_board[action[0]][action[1]] = player(board)  # Perform Action
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] and row[0] is not EMPTY:
            return row[0]
    
    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] is not EMPTY:
            return board[0][col]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not EMPTY:
        return board[0][2]
    
    # No Winner was found
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    return winner(board) is not None or all(cell is not EMPTY for row in board for cell in row)


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    if win == X:
        return 1
    elif win == O:
        return -1
    else:
        return 0


# Define a function to get the max value
def max_value(board):
    # If board is in terminal state, return the utility
    if terminal(board):
        return utility(board), None
       
    # Set max score to lowest possible score
    v = -math.inf
    best_action = None

    # Loop over actions
    for action in actions(board):
        # Make the action and Proceed to Oponents move
        score, _ = min_value(result(board, action))

        # If a better score is found then upadate best action and max score
        if score > v:
            v = score
            best_action = action

    # Return score and action
    return v, best_action


# Define a function to get the min value
def min_value(board):
    # If board is in terminal state, return the utility
    if terminal(board):
        return utility(board), None
    
    # Set max score to highest possible score
    v = math.inf
    best_action = None

    # Loop over actions
    for action in actions(board):
        # Make the action and Proceed to Oponents move
        score, _ = max_value(result(board, action))

        # If a score less than min score is found, update min score and best action
        if score < v:
            v = score
            best_action = action

    # Return score and action
    return v, best_action


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Check if the Current state is a terminal state. In this case no more moves can be made
    if terminal(board):
        return None

    # Get the current player. (This represents the Player AI is playing as)
    current_player = player(board)

    # if AI is playing as X then it wants to maximise the value. 
    if current_player == X:
        _, action = max_value(board)  
    # Other wise minimise the value
    else:
        _, action = min_value(board)
    return action
