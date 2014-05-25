""" Module for Mancala Board class. """

from .constants import P1_PITS, P1_STORE, P2_PITS, P2_STORE

class InvalidBoardArea(Exception):
    """ Exception flagged when moves are attempted on an unknown area. """
    pass

class Board(object):
    """ A Mancala board with size pockets per player and stones """

    def __init__(self, pits=6, stones=4, test_state=None):
        if test_state:
            self.board = test_state
        else:
            self.board = [[stones] * pits, [0], [stones] * pits, [0]]

    def _textify_board(self):
        """ Returns the current board as a printable string to show the user.

        Note that the order of player 2 pits are displayed in reverse
        from the list index to give the appearance of a loop.
        """
        return "   %d  %d  %d  %d  %d  %d\n %d                    %d\n   %d  %d  %d  %d  %d  %d\n" % (
                       # Player 2 pits in top row
                       self.board[2][5], self.board[2][4], self.board[2][3],
                       self.board[2][2], self.board[2][1], self.board[2][0],
                       # Player 2 & 1 stores in middle row
                       self.board[3][0], self.board[1][0],
                       # Player 1 pits on bottom row
                       self.board[0][0], self.board[0][1], self.board[0][2],
                       self.board[0][3], self.board[0][4], self.board[0][5])

    def _move_stones(self, player_num, start_index):
        """ Moves stones by the Player associated with player_num,
        starting at the given index.

        Returns finished state of the Board.

        player_num: integer from Player.number class
        start_index: integer specified by player (must be 0-5)
        """
        if player_num == 1:
            current_area = P1_PITS
        else:
            current_area = P2_PITS

        # Pick up the stones from the right pit.
        stones_grabbed = self.board[current_area][start_index]
        self.board[current_area][start_index] = 0

        # Ready a moving index
        index = start_index

        for stone in range(stones_grabbed):
            try:
                # Try to place in adjacent pit prior to incrementing index.
                self.board[current_area][index+1] += 1
                # Stone successfully placed, so increase index.
                index += 1
            except IndexError:
                # Proceed to next area
                current_area = self._get_next_area(current_area)

                # Check to ensure opposing store is skipped.
                if player_num == 1 and current_area == P2_STORE:
                    current_area = self._get_next_area(current_area)
                elif player_num == 2 and current_area == P1_STORE:
                    current_area = self._get_next_area(current_area)
                else:
                    pass
                # Reset index and increment stone at current position
                index = 0
                self.board[current_area][index] += 1

        # If last move earned a capture, process it.
        if self._earned_capture(player_num, current_area, index):
            self.board = self._process_capture(current_area, index)

        return self.board

    def _earned_capture(self, player_num, last_area, last_index):
        """ Checks whether the last move earned a capture.

        last_area: integer associated with last board area
        last_index: integer of the last move's index
        """

        opposing_area, opposing_index = self._get_opposing_area_and_index(
            last_area, last_index)

        # Check whether last move was in Player's own pits.
        if not (player_num == 1 and last_area == P1_PITS) and \
        not (player_num == 2 and last_area == P2_PITS):
            return False
        
        # Check whether last move's pit now has more than 1 stone.
        elif self.board[last_area][last_index] > 1:
            return False
        
        # Check whether opposite pit has capturable stones.
        elif self.board[opposing_area][opposing_index] == 0:
            return False

        # Placed stone in own empty pit, adjacent capturable stones.
        else:
            return True

    def _process_capture(self, last_area, last_index):
        """ Processes capture by moving stones to the player's store. """

        if last_area == P1_PITS:
            destination_store = P1_STORE
        else:
            destination_store = P2_STORE

        opposing_area, opposing_index = self._get_opposing_area_and_index(
            last_area, last_index)

        captured_stones = self.board[opposing_area][opposing_index]
        print "%d stones captured!" % captured_stones

        # Clear the two pits
        self.board[last_area][last_index] = 0
        self.board[opposing_area][opposing_index] = 0

        # Move captures and original stone to store
        total_gain = captured_stones + 1
        self.board[destination_store][0] += total_gain

        return self.board

    def _reverse_index(self, index):
        """ Returns the mirror index to check opposing stones. """
        reverse_index = range(len(self.board[0]))
        reverse_index.reverse()
        return reverse_index[index]

    def _get_opposing_area_and_index(self, orig_area, index, as_tuple=False):
        """ Returns opposing_area, opposing_index

        Optionally returns as tuple for assertion testing.
         """

        if orig_area == P1_PITS:
            opposing_area = P2_PITS
        elif orig_area == P2_PITS:
            opposing_area = P1_PITS
        elif orig_area == P1_STORE:
            opposing_area = P2_STORE
        elif orig_area == P2_STORE:
            opposing_area = P1_STORE
        else:
            raise InvalidBoardArea

        opposing_index = self._reverse_index(index)

        if as_tuple:
            return (opposing_area, opposing_index)
        else:
            return opposing_area, opposing_index


    def _get_next_area(self, current_area):
        """ Given a current area of transaction, gives the next area. """
        if current_area == P1_PITS:
            return P1_STORE
        elif current_area == P1_STORE:
            return P2_PITS
        elif current_area == P2_PITS:
            return P2_STORE
        elif current_area == P2_STORE:
            return P1_PITS
        else:
            raise InvalidBoardArea

    def get_score(self, player_num):
        """ Returns score for player_num. """
        if player_num == 1:
            return self.board[1][0]
        else:
            return self.board[3][0]

    def get_scores(self):
        """ Returns both scores as a tuple. """
        return (self.board[1][0], self.board[3][0])