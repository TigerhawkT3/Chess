#-------------------------------------------------------------------------------
# Name:        Chess
# Purpose:
#
# Author:      David Muller
#
# Created:     03/29/2014
# Copyright:   (c) David Muller 2014
# Licence:     <your license>
#-------------------------------------------------------------------------------

from tkinter import *
from random import *
import sys
from pygame import mixer
import time

class Player(object):
    """
    An object of this class represents a player.
    Attributes:
        color (string): a string representing the player's color
            (black or white)
        mode (string): a string representing the player's choice of UI mode -
            two clicks to move or click-and-drag to move
    """
    def __init__(self, color):
        self.color = color
        self.mode = "click"

class Piece(object):
    """
    An object of this class represents a chess piece.
    Attributes:
        color (string): the color of the piece
        location(string): a two-character representation of the piece's location
    """
    def __init__(self, color, location):
        self.color = color # the color of a piece - either "black" or "white"
        self.location = location # the location of the piece, expressed
        # as a 2-char string. "00" is the top left square, "07" is the bottom
        # left, "70" is the top right, and "77" is the bottom right.

    def add_if_okay(self, num1, num2):
        """
        This method is used for pieces whose movesets extend until they hit
        a piece: queens, rooks, bishops.
        Parameters:
            num1 (string): the x value of the move, from "0" to "7"
            num2 (string): the y value of the move, from "0" to "7"
        """
        if num1 not in range(8) or num2 not in range(8): # if not on board
            return False # don't add to moves
        loc = str(num1) + str(num2)
        contents = Chess.all_squares.get(str(num1)+str(num2)).piece
        if contents is None: # if the destination is empty
            self.moveset.add(loc) # add to moves
            return True # could be moves in that direction
        else: # if there's a piece there
            if contents.color is not self.color: # and it's an enemy
                self.moveset.add(loc) # add it
            return False # stop looking for moves in that direction

class Pawn(Piece):
    """
    An object of this class represents a pawn piece.
    Attributes:
        direction (int): describes the direction the pawn can move - -1 for "up"
            or 1 for "down"
        moved (boolean): starts False, and then changes to True if it gets moved
        vulnerable (boolean): a vulnerable state, caused by a first move
            spanning two spaces, lasts for one turn and enables the pawn to be
            captured en passant by enemy pawns
        type (string): a string describing the piece with its color and type
        moveset (set): a set of locations where this piece may move
    """
    def __init__(self, color, location):
        super().__init__(color, location)
        self.direction = 1
        if color == "white": # white player
            self.direction = -1 # moves 'up' the board, negative on canvas
        self.moved = False # hasn't moved yet
        self.vulnerable = False # not vulnerable to en passant
        self.type = self.color + "_pawn" # for dictionary key

    def generate_moveset(self):
        """
        Generates a moveset for this piece. Pawns can move ahead one space. If
        it's their first move, they can move ahead two spaces. If there's an
        enemy to their front-left or front-right, they can move and capture. If
        an enemy pawn's first move brings them adjacent to the pawn in question,
        the enemy pawn can be captured by moving to the front-left or
        front-right.
        """
        self.moveset = set() # start with an empty set
        # look one space ahead
        loc = self.location[0] + str(int(self.location[1])+self.direction)
        if len(loc) == 2: # if there's no '-' sign in the location
            # and it's on the board
            if int(loc[0]) in range(8) and int(loc[1]) in range(8):
                if Chess.all_squares.get(loc).piece is None: # and empty
                    self.moveset.add(loc) # add it
        # look another space ahead and do the same thing
        loc = loc[0]+str(int(loc[1])+self.direction)
        if len(loc) == 2:
            if int(loc[0]) in range(8) and int(loc[1]) in range(8):
                # make sure it's the first move, though
                if not self.moved and Chess.all_squares.get(loc).piece is None \
                and Chess.all_squares.get(loc[0]+ \
                # and we can't jump a piece, so check the square behind target
                str(int(loc[1])-self.direction)).piece is None:
                    self.moveset.add(loc) # add it
        loc = str(int(self.location[0])-1) + \
        str(int(self.location[1])+self.direction) # can it capture an enemy?
        if len(loc) == 2: # make sure there's no '-' sign
            # and it's on the board
            if int(loc[0]) in range(8) and int(loc[1]) in range(8):
                # if there's a piece
                if Chess.all_squares.get(loc).piece is not None:
                    # and it's an enemy
                    if Chess.all_squares.get(loc).piece.color is not self.color:
                        self.moveset.add(loc) # it's a valid move
                elif int(loc[0]) in range(8) and \
                int(loc[1])-self.direction in range(8): # no piece there
                    # but there is a piece behind there
                    if Chess.all_squares.get \
                    (loc[0]+str(int(loc[1])-self.direction)).piece is not None:
                        # and it's a pawn
                        if "pawn" in Chess.all_squares.get \
                        (loc[0]+str(int(loc[1])-self.direction)).piece.type:
                            if Chess.all_squares.get \
                            (loc[0]+str(int(loc[1])-self.direction)) \
                            .piece.vulnerable: # and it's vulnerable
                                self.moveset.add(loc) # add due to en passant
        loc = str(int(self.location[0])+1) + \
        str(int(self.location[1])+self.direction) # now the other capture square
        if len(loc) == 2: # if there's no '-' sign
            # and it's on the board
            if int(loc[0]) in range(8) and int(loc[1]) in range(8):
                # and there's a piece there
                if Chess.all_squares.get(loc).piece is not None:
                    # and the piece is an enemy
                    if Chess.all_squares.get(loc).piece.color is not self.color:
                        self.moveset.add(loc) # add the location
                elif int(loc[0]) in range(8) and \
                int(loc[1])-self.direction in range(8): # no piece there
                    # but there is a piece behind there
                    if Chess.all_squares.get \
                    (loc[0]+str(int(loc[1])-self.direction)).piece is not None:
                        # and it's a pawn
                        if "pawn" in Chess.all_squares.get \
                        (loc[0]+str(int(loc[1])-self.direction)).piece.type:
                            if Chess.all_squares.get\
                            (loc[0]+str(int(loc[1])-self.direction)) \
                            .piece.vulnerable: # and it's vulnerable
                                self.moveset.add(loc) # add due to en passant

class Rook(Piece):
    """
    An object of this class represents a rook piece.
    Attributes:
        moved (boolean): False if the piece hasn't moved yet, True as soon as
            it has
        type (string): a string describing the piece with its color and type
        moveset: a set of locations where this piece may move
    """
    def __init__(self, color, location):
        super().__init__(color, location)
        self.moved = False # used to check castles
        self.type = self.color + "_rook" # for dictionary key

    def generate_moveset(self):
        """
        Generates a moveset for this piece. Rooks can move in straight lines
        horizontally or vertically until they reach a piece. If the piece
        is an enemy, that space is a valid move for the rook.
        """
        self.moveset = set() # start with an empty set
        # here we're going to start looking for pieces to add in each of
        # four directions. it'll first try to add a square, and then if it's
        # empty it'll move to the next one. if there's a piece in that square,
        # it'll add it if the piece is an enemy and then stop looking in that
        # direction. getting to the end of the board will also stop that
        # direction. this method relies heavily on add_if_okay, which checks
        # a square and lets this method know whether there are more pieces to
        # check in that direction.

        for num in range((int(self.location[1])+1),8): # look down
            if not self.add_if_okay(int(self.location[0]), num):
                break # stop this direction
        for num in range((int(self.location[0])+1),8): # look to the right
            if not self.add_if_okay(num, int(self.location[1])):
                break # stop this direction
        for num in range((int(self.location[1])-1),-1,-1): # look up
            if not self.add_if_okay(int(self.location[0]), num):
                break # stop this direction
        for num in range((int(self.location[0])-1),-1,-1): # look to the left
            if not self.add_if_okay(num, int(self.location[1])):
                break # stop this direction

class Knight(Piece):
    """
    An object of this class represents a knight piece.
    Attributes:
        type (string): a string describing the piece with its color and type
        moveset (set): a set of locations where this piece may move
    """
    def __init__(self, color, location):
        super().__init__(color, location)
        self.type = self.color + "_knight" # for dictionary key

    def generate_moveset(self):
        """
        Generates a moveset for this piece. Knights can move to a predetermined
        set of locations relative to their current position. If a location is
        off the board or occupied by an allied piece, that location is not
        included in the moveset.
        """
        # the knight moveset is hard-coded. we start with the full possible
        # set of moves.
        self.moveset = {str(int(self.location[0])-2)+ \
        str(int(self.location[1])-1),
        str(int(self.location[0])-2)+str(int(self.location[1])+1),
        str(int(self.location[0])-1)+str(int(self.location[1])-2),
        str(int(self.location[0])-1)+str(int(self.location[1])+2),
        str(int(self.location[0])+1)+str(int(self.location[1])-2),
        str(int(self.location[0])+1)+str(int(self.location[1])+2),
        str(int(self.location[0])+2)+str(int(self.location[1])-1),
        str(int(self.location[0])+2)+str(int(self.location[1])+1)}

        occupied = set() # we'll populate this set with invalid moves
        for place in self.moveset:
            if len(place) != 2: # if there's a '-' sign
                occupied.add(place) # that square is no good
                continue # immediately check the next square
            # if the square is not on the board
            if int(place[0]) not in range(8) or int(place[1]) not in range(8):
                occupied.add(place) # it's no good
                continue # immediately check the next square
            occupier = Chess.all_squares.get(place).piece
            if occupier is not None: # if there is a piece there
                if occupier.color is self.color: # and it's allied
                    occupied.add(place) # that square is no good
        self.moveset -= occupied # subtract the invalid squares from the total

class Bishop(Piece):
    """
    An object of this class represents a bishop piece.
    Attributes:
        type (string): a string describing the piece with its color and type
        moveset (set): a set of locations where this piece may move
    """
    def __init__(self, color, location):
        super().__init__(color, location)
        self.type = self.color + "_bishop" # for dictionary key

    def generate_moveset(self):
        """
        Generates a moveset for this piece. Bishops can move in diagonal lines
        until they reach a piece. If the piece is an enemy, that space is a
        valid move for the bishop.
        """
        self.moveset = set()# start with an empty set
        # here we're going to start looking for pieces to add in each of
        # four directions. it'll first try to add a square, and then if it's
        # empty it'll move to the next one. if there's a piece in that square,
        # it'll add it if the piece is an enemy and then stop looking in that
        # direction. getting to the end of the board will also stop that
        # direction. this method relies heavily on add_if_okay, which checks
        # a square and lets this method know whether there are more pieces to
        # check in that direction.

        other = int(self.location[0]) + 1 # start going to the right
        for num in range((int(self.location[1])+1),8): # and down
            if not self.add_if_okay(other, num): # if you hit a piece or the end
                break # stop this direction
            other += 1 # this is what makes it diagonal
        other = int(self.location[1]) - 1 # now go up
        for num in range((int(self.location[0])+1),8): # and to the right
            if not self.add_if_okay(num, other): # if you hit a piece or the end
                break # stop this direction
            other -= 1 # decrement the axis not handled in the for loop
        other = int(self.location[0]) - 1 # now go to the left
        for num in range((int(self.location[1])-1),-1,-1): # and up
            if not self.add_if_okay(other, num): # if you hit a piece or the end
                break # stop this direction
            other -= 1 # decrement the axis not handled in the for loop
        other = int(self.location[1]) + 1 # now go down
        for num in range((int(self.location[0])-1),-1,-1): # and to the left
            if not self.add_if_okay(num, other): # if you hit a piece or the end
                break # stop this direction
            other += 1 # increment the axis not handled in the for loop

class King(Piece):
    """
    An object of this class represents a king piece.
    Attributes:
        moved (boolean): False if the piece hasn't moved yet, True as soon as
            it has
        type (string): a string describing the piece with its color and type
        moveset (set): a set of locations where this piece may move
    """
    def __init__(self, color, location):
        super().__init__(color, location)
        self.moved = False
        self.type = self.color + "_king" # for dictionary key

    def generate_moveset(self):
        """
        Generates a moveset for this piece. Kings can move to a predetermined
        set of locations relative to their current position. If a location is
        off the board or occupied by an allied piece, that location is not
        included in the moveset.
        """
        # the king moveset is hard-coded. we start with the full possible
        # set of moves.
        self.moveset = {str(int(self.location[0])-1)+ \
        str(int(self.location[1])-1),
        str(int(self.location[0])-1)+str(int(self.location[1])),
        str(int(self.location[0])-1)+str(int(self.location[1])+1),
        str(int(self.location[0]))+str(int(self.location[1])-1),
        str(int(self.location[0]))+str(int(self.location[1])+1),
        str(int(self.location[0])+1)+str(int(self.location[1])-1),
        str(int(self.location[0])+1)+str(int(self.location[1])),
        str(int(self.location[0])+1)+str(int(self.location[1])+1)}

        occupied = set() # we'll populate this set with invalid moves
        for place in self.moveset:
            if len(place) != 2: # if there's a '-' sign
                occupied.add(place) # that square is no good
                continue # immediately check the next square
            # if the square is not on the board
            if int(place[0]) not in range(8) or int(place[1]) not in range(8):
                occupied.add(place) # it's no good
                continue # immediately check the next square
            occupier = Chess.all_squares.get(place).piece
            if occupier is not None: # if there is a piece there
                if occupier.color is self.color: # and it's allied
                    occupied.add(place) # that square is no good
        self.moveset -= occupied # subtract the invalid squares from the total

class Queen(Piece):
    """
    An object of this class represents a queen piece.
    Attributes:
        type (string): a string describing the piece with its color and type
        moveset (set): a set of locations where this piece may move
    """
    def __init__(self, color, location):
        super().__init__(color, location)
        self.type = self.color + "_queen" # for dictionary key

    def generate_moveset(self):
        """
        Generates a moveset for this piece. Queens can move in diagonal,
        horizontal, or vertical lines until they reach a piece. If the piece is
        an enemy, that space is a valid move for the queen.
        """

        self.moveset = set() # we'll start with an empty set
        # here we're going to start looking for pieces to add in each of
        # eight directions. it'll first try to add a square, and then if it's
        # empty it'll move to the next one. if there's a piece in that square,
        # it'll add it if the piece is an enemy and then stop looking in that
        # direction. getting to the end of the board will also stop that
        # direction. the latter part of this method relies heavily on
        # add_if_okay, which checks a square and lets this method know whether
        # there are more pieces to check in that direction.

        other = int(self.location[0]) + 1 # start going to the right
        for num in range((int(self.location[1])+1),8): # and down
            if not self.add_if_okay(other, num): # if you hit a piece or the end
                break # stop this direction
            other += 1 # this is what makes it diagonal
        other = int(self.location[1]) - 1 # now go up
        for num in range((int(self.location[0])+1),8): # and to the right
            if not self.add_if_okay(num, other): # if you hit a piece or the end
                break # stop this direction
            other -= 1 # decrement the axis not handled in the for loop
        other = int(self.location[0]) - 1 # now go to the left
        for num in range((int(self.location[1])-1),-1,-1): # and up
            if not self.add_if_okay(other, num): # if you hit a piece or the end
                break # stop this direction
            other -= 1 # decrement the axis not handled in the for loop
        other = int(self.location[1]) + 1 # now go down
        for num in range((int(self.location[0])-1),-1,-1): # and to the left
            if not self.add_if_okay(num, other): # if you hit a piece or the end
                break # stop this direction
            other += 1 # increment the axis not handled in the for loop
        for num in range((int(self.location[1])+1),8): # look down
            if not self.add_if_okay(int(self.location[0]), num):
                break # stop this direction
        for num in range((int(self.location[0])+1),8): # look to the right
            if not self.add_if_okay(num, int(self.location[1])):
                break # stop this direction
        for num in range((int(self.location[1])-1),-1,-1): # look up
            if not self.add_if_okay(int(self.location[0]), num):
                break # stop this direction
        for num in range((int(self.location[0])-1),-1,-1): # look to the left
            if not self.add_if_okay(num, int(self.location[1])):
                break # stop this direction

class Square(object):
    """
    An object of this class represents a square on the board.
    Attributes:
        location (string): a string representing the square's location
        piece (Piece): the Piece object "resting" on that Square object
    """
    def __init__(self, location):
        self.location = location # the location of the square, expressed
        # as a 2-char string. "00" is the top left square, "07" is the bottom
        # left, "70" is the top right, and "77" is the bottom right.
        self.piece = None # the piece on this square. None if empty.

class Chess(object):

    """
    An object of this class represents a Chess game, with easy mode, hard mode,
    and two-player mode.

    Attributes:
        all_squares (dictionary): a class variable (not member variable) of
            the Chess class. The keys are two-character strings describing
            the location of an object on the board, and the values are Squares
            on the board.
        frame (Frame): a tkinter Frame that holds the visible game
        easy_button (Button): a tkinter Button that launches a new AI match
        human_button (Button): a tkinter Button that launches a new 2P match
        castle_black_left_button (Button): a tkinter Button that performs the
            black queenside castling, if legal
        castle_black_right_button (Button): a tkinter Button that performs the
            black kingside castling, if legal
        castle_white_left_button (Button): a tkinter Button that performs the
            white queenside castling, if legal
        castle_white_right_button (Button): a tkinter Button that performs the
            white kingside castling, if legal
        mode (string): "easy" for easy AI play, "hard" for hard AI play, and
            "human" for 2P matches
        status_message (Label): a tkinter Label that displays the appropriate
            message when a player wins
        text_box (Entry): a tkinter Entry box for the user to enter a file name
        txt_label (Label): a tkinter Label that just says '.txt'
        instructions (Label): a tkinter Label with the hotkeys
        instructions (Label): a tkinter Label that provides basic instructions
        white_player (Player): a Player object, using the white pieces
        black_player (Player): a Player object, using the black pieces
        black_king_gif (PhotoImage): a PhotoImage object containing a GIF of
            the black king
        black_queen_gif (PhotoImage): a PhotoImage object containing a GIF of
            the black queen
        black_rook_gif (PhotoImage): a PhotoImage object containing a GIF of
            a black rook
        black_bishop_gif (PhotoImage): a PhotoImage object containing a GIF of
            a black bishop
        black_knight_gif (PhotoImage): a PhotoImage object containing a GIF of
            a black knight
        black_pawn_gif (PhotoImage): a PhotoImage object containing a GIF of
            a black pawn
        white_king_gif (PhotoImage): a PhotoImage object containing a GIF of
            the white king
        white_queen_gif (PhotoImage): a PhotoImage object containing a GIF of
            the white queen
        white_rook_gif (PhotoImage): a PhotoImage object containing a GIF of
            a white rook
        white_bishop_gif (PhotoImage): a PhotoImage object containing a GIF of
            a white bishop
        white_knight_gif (PhotoImage): a PhotoImage object containing a GIF of
            a white knight
        white_pawn_gif (PhotoImage): a PhotoImage object containing a GIF of
            a white pawn
        transparent_square_gif (PhotoImage): a PhotoImage object containing a
            GIF of a transparent square - when there's no Piece on a Square,
            this image is displayed
        piece_pics (dictionary): a dictionary describing which images go with
            which pieces. The keys are strings describing the piece (like
            "black_bishop"), and the values are PhotoImage instance variables
            (like self.black_bishop_gif).
        board (Canvas): the visible board, containing rectangles and images
        squares (list): the visible squares on the board, composed of black
            and white rectangles
        white_promotions (int): the number of pawns that white has promoted
            into queens
        black_promotions (int): the number of pawns that black has promoted
            into queens
        black_rook_1 (Rook): the queenside black rook
        black_knight_1 (Knight): the queenside black knight
        black_bishop_1 (Bishop): the queenside black bishop
        black_queen (Queen): the black queen
        black_king (King): the black king
        black_bishop_2 (Bishop): the kingside black bishop
        black_knight_2 (Knight): the kingside black knight
        black_rook_2 (Rook): the kingside black rook
        black_pawn_1 (Pawn): the first black pawn from left
        black_pawn_2 (Pawn): the second black pawn from left
        black_pawn_3 (Pawn): the third black pawn from left
        black_pawn_4 (Pawn): the fourth black pawn from left
        black_pawn_5 (Pawn): the fifth black pawn from left
        black_pawn_6 (Pawn): the sixth black pawn from left
        black_pawn_7 (Pawn): the seventh black pawn from left
        black_pawn_8 (Pawn): the eighth black pawn from left
        extra_black_queens (list): a list with cells that point to the extra
            queens that black can unlock via pawn promotion
        white_pawn_1 (Pawn): the first white pawn from left
        white_pawn_2 (Pawn): the second white pawn from left
        white_pawn_3 (Pawn): the third white pawn from left
        white_pawn_4 (Pawn): the fourth white pawn from left
        white_pawn_5 (Pawn): the fifth white pawn from left
        white_pawn_6 (Pawn): the sixth white pawn from left
        white_pawn_7 (Pawn): the seventh white pawn from left
        white_pawn_8 (Pawn): the eighth white pawn from left
        white_knight_1 (Knight): the queenside white knight
        white_bishop_1 (Bishop): the queenside white bishop
        white_queen (Queen): the white queen
        white_king (King): the white king
        white_bishop_2 (Bishop): the kingside white bishop
        white_knight_2 (Knight): the kingside white knight
        white_rook_2 (Rook): the kingside white rook
        extra_white_queens (list): a list with cells that point to the extra
            queens that white can unlock via pawn promotion
        all_pieces (list): a list that points to each piece
        square_overlay (list): a 2D list that refers to each image that rests
            on a square. Squares with no piece have a transparent image, and
            squares with a piece have an image of that piece. This list is
            compatible with all_squares - a particular cell in one array matches
            the proper cell in the other array so that each square can contain
            the proper image.
        player (Player): a reference to the currently-active Player
        first_click (boolean): describes whether the player can expect to select
            a piece with this click. If it's False, the player is currently
            seeing move options for their selected piece.
        last_ai_piece (Piece): a reference to the last Piece object the AI
            player moved - allows the program to discourage the AI from moving
            a piece and ignoring the rest, which also prevents the AI from
            moving one piece back and forth for several turns
        chosen_piece (Piece): the Piece that a human player has selected with
            their first click
        last_source (string): a string representation of the last-moved piece's
            previous location
        last_target (string): a string representation of the last-moved piece's
            current location
        dragged_piece (int): an int representation of the PhotoImage to be
            dragged around in click-drag mode
        autosave (boolean): True if the file to be saved or loaded is the
            autosave, False otherwise
        sound_folder (string): Folder containing the sound files.
        icon_folder (string): Folder containing the icon files.
        audio (boolean): True if the user wants sound effects, False otherwise.
    """
    def __init__(self, parent):

        parent.title("Chess") # title for the window
        self.parent = parent

        # Here's the frame:
        self.frame = Frame(parent)
        self.frame.pack()

        # Here are three mode buttons:
        self.easy_button = Button(self.frame, text =
            "New easy game", fg="white", bg="black", command=self.new_easy)
        self.easy_button.grid(row=0, column=0, padx=5, pady=5)
        self.hard_button = Button(self.frame, text =
            "New hard game", fg = "black", bg="#ECE9D8", command=self.new_hard)
        self.hard_button.grid(row=0, column=1, padx=5, pady=5)
        self.human_button = Button(self.frame, text =
            "New 2P game", fg = "black", bg="#ECE9D8", command=self.new_human)
        self.human_button.grid(row=0, column=2, padx=5, pady=5)

        # Here are four castle buttons:
        self.castle_black_left_button = Button(self.frame, text =
            "Castle here", command=self.castle_black_left)
        self.castle_black_left_button.grid(row=1, column=0, padx=5, pady=5)
        self.castle_black_right_button = Button(self.frame, text =
            "Castle here", command=self.castle_black_right)
        self.castle_black_right_button.grid(row=1, column=2, padx=5, pady=5)
        self.castle_white_left_button = Button(self.frame, text =
            "Castle here", command=self.castle_white_left)
        self.castle_white_left_button.grid(row=3, column=0, padx=5, pady=5)
        self.castle_white_right_button = Button(self.frame, text =
            "Castle here", command=self.castle_white_right)
        self.castle_white_right_button.grid(row=3, column=2, padx=5, pady=5)

        # Here are two UI-mode buttons:
        self.black_click_button = Button(self.frame, text =
            "Active mode:\nclick/click", command=self.black_ui_toggle)
        self.black_click_button.grid(row=1, column=1, padx=5, pady=5)
        self.white_click_button = Button(self.frame, text =
            "Active mode:\nclick/click", command=self.white_ui_toggle)
        self.white_click_button.grid(row=3, column=1, padx=5, pady=5)

        # The game starts on easy mode without making the player press a button.
        self.mode = "easy"

        # Status message. When the game ends, the result is described here.
        self.status_message = Label(self.frame, text = "")
        self.status_message.grid(row=4, column = 0, columnspan=3)

        # Filename box explanation
        self.name_here = Label(self.frame, text = "Load/save a file/folder: ")
        self.name_here.grid(row=5, column=0, sticky="E")

        # Text box for entering a file name
        self.text_box = Entry(self.frame, width=32, justify=RIGHT)
        self.text_box.grid(row=5, column=1, sticky="E")

        # Set a default file name
        self.text_box.delete(0, END)
        self.text_box.insert(0, "savechess")

        # '.txt' label
        self.txt_label = Label(self.frame, text = ".txt (or folder)")
        self.txt_label.grid(row=5, column=2, sticky="W")

        # Create the two players, white and black.
        self.white_player = Player("white")
        self.black_player = Player("black")

        """
        Default sounds from http://www.trekcore.com/audio:
            game_start.ogg - computerbeep_50.mp3 'Computer Beep 50'
            ui_toggle.ogg - hologram_off_2.mp3 'Hologram Off 2'
            audio_on.ogg - computerbeep_73.mp3 'Computer Beep 73'
            select_piece.ogg - computerbeep_55.mp3 'Computer Beep 55'
            move_piece.ogg - computerbeep_74.mp3 'Computer Beep 74'
            computer_move.ogg - computerbeep_75.mp3 'Computer Beep 75'
            castle.ogg - energize.mp3 'Energize'
            undo.ogg - input_failed_clean.mp3 'Input Failed 1'
            torpedo.ogg - tng_torpedo_clean.mp3 'TNG Torpedo 1'
            explosion.ogg - largeexplosion4.mp3 'Large Explosion 4'
        """
        audiostring = " | (A)udio" # this will go in the instructions label
        self.audio = True

        try: # here, we're going to try enabling audio with pygame
            mixer.init(buffer=512) # initialize the mixer
            try: # first we'll look into the command line
                self.sound_folder = sys.argv[2] + "/" # there was an argv
                # so now we check to make sure every single audio file is
                # present and can be loaded. it's either this or using
                # try/except every time a sound is played.
                mixer.music.load(self.sound_folder + "ui_toggle.ogg")
                mixer.music.load(self.sound_folder + "audio_on.ogg")
                mixer.music.load(self.sound_folder + "select_piece.ogg")
                mixer.music.load(self.sound_folder + "move_piece.ogg")
                mixer.music.load(self.sound_folder + "computer_move.ogg")
                mixer.music.load(self.sound_folder + "castle.ogg")
                mixer.music.load(self.sound_folder + "undo.ogg")
                mixer.music.load(self.sound_folder + "torpedo.ogg")
                mixer.music.load(self.sound_folder + "explosion.ogg")
                mixer.music.load(self.sound_folder + "game_start.ogg")
            except: # well, something failed in the command line attempt. either
            # there was no command line argv given there, or the folder was
            # missing, or one of the files was missing. so now we try the
            # default sound folder, checking it for every needed file.
                self.sound_folder = "sfx/"
                mixer.music.load(self.sound_folder + "ui_toggle.ogg")
                mixer.music.load(self.sound_folder + "audio_on.ogg")
                mixer.music.load(self.sound_folder + "select_piece.ogg")
                mixer.music.load(self.sound_folder + "move_piece.ogg")
                mixer.music.load(self.sound_folder + "computer_move.ogg")
                mixer.music.load(self.sound_folder + "castle.ogg")
                mixer.music.load(self.sound_folder + "undo.ogg")
                mixer.music.load(self.sound_folder + "torpedo.ogg")
                mixer.music.load(self.sound_folder + "explosion.ogg")
                mixer.music.load(self.sound_folder + "game_start.ogg")
            # if we've gotten this far, then an audio load was successful
            self.parent.bind("<Control-a>", self.audio_toggle) # bind buttons
            self.parent.bind("<Control-A>", self.audio_toggle)
        except: # couldn't load audio for some reason. either pygame isn't
        # installed on the user's machine, or it couldn't find an audio folder.
            audiostring = "" # so we won't mention audio in the instructions
            self.audio = False # we'll disable audio
            # and we'll give the user a message telling them what happened
            self.parent.after(0, self.audio_failed)

        # Game instructions.
        self.instructions = Label(self.frame, \
        text="Ctrl + ... (S)ave game | (L)oad game | (Z)Undo" + \
        audiostring + "\n" + \
        "a(U)dio from folder | (I)cons from folder\n" + \
        "(E)asy manual AI move | (H)ard manual AI move")
        self.instructions.grid(row=6, column = 0, columnspan = 3)


        # now we'll load the piece icons
        try: # first we'll try an argv-specified folder
            try:
                icon_folder = sys.argv[1] + "/" # there was an argv
                # so now we check to make sure every single icon file is
                # present and can be loaded.
                self.black_king_gif = PhotoImage(file=icon_folder+"black_king.gif")
                self.black_queen_gif = PhotoImage(file=icon_folder+"black_queen.gif")
                self.black_rook_gif = PhotoImage(file=icon_folder+"black_rook.gif")
                self.black_bishop_gif = PhotoImage(file=icon_folder+"black_bishop.gif")
                self.black_knight_gif = PhotoImage(file=icon_folder+"black_knight.gif")
                self.black_pawn_gif = PhotoImage(file=icon_folder+"black_pawn.gif")

                self.white_king_gif = PhotoImage(file=icon_folder+"white_king.gif")
                self.white_queen_gif = PhotoImage(file=icon_folder+"white_queen.gif")
                self.white_rook_gif = PhotoImage(file=icon_folder+"white_rook.gif")
                self.white_bishop_gif = PhotoImage(file=icon_folder+"white_bishop.gif")
                self.white_knight_gif = PhotoImage(file=icon_folder+"white_knight.gif")
                self.white_pawn_gif = PhotoImage(file=icon_folder+"white_pawn.gif")

                self.transparent_square_gif = \
                PhotoImage(file=icon_folder+"transparent_square.gif")
            except: # well, something failed in the command line attempt. either
            # there was no command line argv given there, or the folder was
            # missing, or one of the files was missing. so now we try the
            # default icon folder, checking it for every needed file.
                icon_folder = "piece_icons/"
                self.black_king_gif = PhotoImage(file=icon_folder+"black_king.gif")
                self.black_queen_gif = PhotoImage(file=icon_folder+"black_queen.gif")
                self.black_rook_gif = PhotoImage(file=icon_folder+"black_rook.gif")
                self.black_bishop_gif = PhotoImage(file=icon_folder+"black_bishop.gif")
                self.black_knight_gif = PhotoImage(file=icon_folder+"black_knight.gif")
                self.black_pawn_gif = PhotoImage(file=icon_folder+"black_pawn.gif")

                self.white_king_gif = PhotoImage(file=icon_folder+"white_king.gif")
                self.white_queen_gif = PhotoImage(file=icon_folder+"white_queen.gif")
                self.white_rook_gif = PhotoImage(file=icon_folder+"white_rook.gif")
                self.white_bishop_gif = PhotoImage(file=icon_folder+"white_bishop.gif")
                self.white_knight_gif = PhotoImage(file=icon_folder+"white_knight.gif")
                self.white_pawn_gif = PhotoImage(file=icon_folder+"white_pawn.gif")

                self.transparent_square_gif = \
                PhotoImage(file=icon_folder+"transparent_square.gif")
        except: # couldn't load the piece icons. there was no helpful argv, and
        # the default folder ("piece_icons") couldn't be found or had missing
        # files. disable all buttons, announce the FLAGRANT ERROR, end this
        # method immediately without organizing the icons or drawing the board,
        # and auto-quit after 30 seconds.
            self.easy_button.config(state=DISABLED)
            self.hard_button.config(state=DISABLED)
            self.human_button.config(state=DISABLED)
            self.black_click_button.config(state=DISABLED)
            self.white_click_button.config(state=DISABLED)
            self.castle_black_left_button.config(state=DISABLED)
            self.castle_black_right_button.config(state=DISABLED)
            self.castle_white_left_button.config(state=DISABLED)
            self.castle_white_right_button.config(state=DISABLED)
            self.instructions.config(text = \
            "FLAGRANT ERROR: Could not find images for the piece icons.\n" + \
            "If you specified a folder, it is missing or corrupted.\n" + \
            "The default folder is missing or corrupted.\n" + \
            "The game will exit automatically in 30 seconds.")
            self.parent.after(30000, self.images_failed)
            return

        # this organizes this piece icons into an easily-accessed dictionary.
        # the keys match the 'type' string variable of Piece objects.
        self.piece_pics = {"black_king":self.black_king_gif,
        "black_queen":self.black_queen_gif, "black_rook":self.black_rook_gif,
        "black_bishop":self.black_bishop_gif, \
        "black_knight":self.black_knight_gif,
        "black_pawn":self.black_pawn_gif, "white_king":self.white_king_gif,
        "white_queen":self.white_queen_gif, "white_rook":self.white_rook_gif,
        "white_bishop":self.white_bishop_gif, \
        "white_knight":self.white_knight_gif,
        "white_pawn":self.white_pawn_gif,
        "transparent_square":self.transparent_square_gif}

         # save the icon folder, as we may need to revert to it later
        self.icon_folder = icon_folder

        self.autosave = False # this is only true while undoing a move

        # Draws the board, which involves reinitialization of match-specific
        # variables.
        self.draw_board()

    def draw_board(self):
        """
        Creates the game, wiping any previous conditions.
        """

        # This generates the board. Rectangles are saved to a 2D array.
        self.board = Canvas(self.frame, width=400, height = 400)
        self.last_source = None

        self.squares = [] # this is a 2D list of black/white squares
        for row in range(8):
            self.squares.append([])
            for column in range(8):
                if (row+column)%2 == 0:
                    color = 'white'
                else:
                    color = 'black'
                self.squares[row].append(self.board.create_rectangle(row*50,
                    column*50,row*50+50,column*50+50, fill = color))

        self.board.grid(row=2, column=0, columnspan=3)

        # Make a dictionary of location:Square.
        Chess.all_squares = {str(row)+str(column):Square(str(row)+str(column))
            for row in range(8) for column in range(8)}

        self.white_promotions = 0 # number of white pawns promoted into queens
        self.black_promotions = 0 # number of black pawns promoted into queens

        # The pieces.
        self.black_rook_1 = Rook("black", "00")
        self.black_knight_1 = Knight("black", "10")
        self.black_bishop_1 = Bishop("black", "20")
        self.black_queen = Queen("black", "30")
        self.black_king = King("black", "40")
        self.black_bishop_2 = Bishop("black", "50")
        self.black_knight_2 = Knight("black", "60")
        self.black_rook_2 = Rook("black", "70")
        self.black_pawn_1 = Pawn("black", "01")
        self.black_pawn_2 = Pawn("black", "11")
        self.black_pawn_3 = Pawn("black", "21")
        self.black_pawn_4 = Pawn("black", "31")
        self.black_pawn_5 = Pawn("black", "41")
        self.black_pawn_6 = Pawn("black", "51")
        self.black_pawn_7 = Pawn("black", "61")
        self.black_pawn_8 = Pawn("black", "71")
        self.extra_black_queens = [Queen("black", "88") for i in range(8)]

        self.white_pawn_1 = Pawn("white", "06")
        self.white_pawn_2 = Pawn("white", "16")
        self.white_pawn_3 = Pawn("white", "26")
        self.white_pawn_4 = Pawn("white", "36")
        self.white_pawn_5 = Pawn("white", "46")
        self.white_pawn_6 = Pawn("white", "56")
        self.white_pawn_7 = Pawn("white", "66")
        self.white_pawn_8 = Pawn("white", "76")
        self.white_rook_1 = Rook("white", "07")
        self.white_knight_1 = Knight("white", "17")
        self.white_bishop_1 = Bishop("white", "27")
        self.white_queen = Queen("white", "37")
        self.white_king = King("white", "47")
        self.white_bishop_2 = Bishop("white", "57")
        self.white_knight_2 = Knight("white", "67")
        self.white_rook_2 = Rook("white", "77")
        self.extra_white_queens = [Queen("white", "88") for i in range(8)]

        # This will put pieces in each square to set up the game.
        Chess.all_squares.get("00").piece = self.black_rook_1
        Chess.all_squares.get("10").piece = self.black_knight_1
        Chess.all_squares.get("20").piece = self.black_bishop_1
        Chess.all_squares.get("30").piece = self.black_queen
        Chess.all_squares.get("40").piece = self.black_king
        Chess.all_squares.get("50").piece = self.black_bishop_2
        Chess.all_squares.get("60").piece = self.black_knight_2
        Chess.all_squares.get("70").piece = self.black_rook_2
        Chess.all_squares.get("01").piece = self.black_pawn_1
        Chess.all_squares.get("11").piece = self.black_pawn_2
        Chess.all_squares.get("21").piece = self.black_pawn_3
        Chess.all_squares.get("31").piece = self.black_pawn_4
        Chess.all_squares.get("41").piece = self.black_pawn_5
        Chess.all_squares.get("51").piece = self.black_pawn_6
        Chess.all_squares.get("61").piece = self.black_pawn_7
        Chess.all_squares.get("71").piece = self.black_pawn_8

        Chess.all_squares.get("06").piece = self.white_pawn_1
        Chess.all_squares.get("16").piece = self.white_pawn_2
        Chess.all_squares.get("26").piece = self.white_pawn_3
        Chess.all_squares.get("36").piece = self.white_pawn_4
        Chess.all_squares.get("46").piece = self.white_pawn_5
        Chess.all_squares.get("56").piece = self.white_pawn_6
        Chess.all_squares.get("66").piece = self.white_pawn_7
        Chess.all_squares.get("76").piece = self.white_pawn_8
        Chess.all_squares.get("07").piece = self.white_rook_1
        Chess.all_squares.get("17").piece = self.white_knight_1
        Chess.all_squares.get("27").piece = self.white_bishop_1
        Chess.all_squares.get("37").piece = self.white_queen
        Chess.all_squares.get("47").piece = self.white_king
        Chess.all_squares.get("57").piece = self.white_bishop_2
        Chess.all_squares.get("67").piece = self.white_knight_2
        Chess.all_squares.get("77").piece = self.white_rook_2

        # this will store the Piece objects in a list so that they can be easily
        # iterated through later on
        self.all_pieces = [self.black_rook_1, self.black_knight_1,
        self.black_bishop_1, self.black_queen, self.black_king,
        self.black_bishop_2, self.black_knight_2, self.black_rook_2,
        self.black_pawn_1, self.black_pawn_2, self.black_pawn_3,
        self.black_pawn_4, self.black_pawn_5, self.black_pawn_6,
        self.black_pawn_7, self.black_pawn_8]

        for i in range(8):
            self.all_pieces.append(self.extra_black_queens[i])

        self.all_pieces += [self.white_pawn_1, self.white_pawn_2,
        self.white_pawn_3, self.white_pawn_4, self.white_pawn_5,
        self.white_pawn_6, self.white_pawn_7, self.white_pawn_8,
        self.white_rook_1, self.white_knight_1, self.white_bishop_1,
        self.white_queen, self.white_king, self.white_bishop_2,
        self.white_knight_2, self.white_rook_2]

        for i in range(8):
            self.all_pieces.append(self.extra_white_queens[i])

        self.square_overlay = [] # a list of all the piece icons or transparent
        # images that can rest on any given square
        for row in range(8):
            self.square_overlay.append([])
            for column in range(8):
                self.square_overlay[row].append \
                (self.board.create_image(row*50,column*50,
                anchor=NW,image=None))

        # this is the image that can float around the board, used when a player
        # is using the click-and-drag interface
        self.dragged_piece = self.board.create_image(50,50, \
        image=self.piece_pics.get("transparent_square"))

        # look at the state of the board and put images where needed
        self.refresh_images()

        # Now generate initial movesets.
        self.generate_all_movesets()

        # Bind the left mouse button to the new board.
        if self.white_player.mode == "click":
            self.board.bind("<Button-1>", self.click_click)
        else:
            self.board.bind("<Button-1>", self.click_hold)

        # these are the game controls
        self.parent.bind("<Control-e>", self.easy_step)
        self.parent.bind("<Control-h>", self.hard_step)
        self.parent.bind("<Control-s>", self.save)
        self.parent.bind("<Control-l>", self.load)
        self.parent.bind("<Control-z>", self.undo)
        self.parent.bind("<Control-u>", self.audio_from_folder)
        self.parent.bind("<Control-i>", self.icons_from_folder)
        self.parent.bind("<Control-E>", self.easy_step)
        self.parent.bind("<Control-H>", self.hard_step)
        self.parent.bind("<Control-S>", self.save)
        self.parent.bind("<Control-L>", self.load)
        self.parent.bind("<Control-Z>", self.undo)
        self.parent.bind("<Control-U>", self.audio_from_folder)
        self.parent.bind("<Control-I>", self.icons_from_folder)

        # Set a status message.
        self.status_message.config(text = "Welcome to Chess!")

        if self.audio: # if audio is on
            if not self.autosave: # and this isn't being restored with undo
                mixer.music.load(self.sound_folder + "game_start.ogg")
                mixer.music.play() # play 'game_start'
            else: # if it's being restored with undo
                mixer.music.load(self.sound_folder + "undo.ogg")
                mixer.music.play() # play the 'undo' sound

        # Make sure the first player is white.
        self.player = self.white_player

        # Checks if any castling moves are available.
        # At this point, they won't be.
        self.check_castles()

        # When this is True, clicking the mouse on a square does move
        # highlighting and stuff. When it's False, clicking the mouse on a
        # square moves the selected piece to the clicked square.
        self.first_click = True

        self.last_ai_piece = self.black_king # the AI needs to check what piece
        # it moved last, so this makes sure it can do that even before its first
        # move

    def easy_step(self, event):
        """
        If it's currently black's turn, this tells the easy AI to make one move.
        Parameter:
            event (sequence): data describing the input. In this case, it's
            just the keyboard input used to access this method.
        """
        # if it's black's turn and the game isn't over
        if self.player is self.black_player and \
        self.black_king.location != "88" \
        and self.white_king.location != "88":
            self.easy_move() # make an easy move
            self.status_message.config(text = "Easy AI moved for Black! " + \
            "White's turn.") # and announce that
        else: # if not
            self.status_message.config(text = "It must be Black's " + \
            "turn for that.") # explain why it didn't move

    def hard_step(self, event):
        """
        If it's currently black's turn, this tells the hard AI to make one move.
        Parameter:
            event (sequence): data describing the input. In this case, it's
            just the keyboard input used to access this method.
        """
        # if it's black's turn and the game isn't over
        if self.player is self.black_player and \
        self.black_king.location != "88" \
        and self.white_king.location != "88":
            self.hard_move() # make a hard move
            self.status_message.config(text = "Hard AI moved for Black! " + \
            "White's turn.") # and announce that
        else: # if not
            self.status_message.config(text = "It must be Black's " + \
            "turn for that.") # explain why it didn't move

    def save(self, event):
        """
        Saves the current game state to a file. The name is whatever was entered
        into the text box. If nothing was entered, it's given the default name
        "savechess.txt" in the current working directory. Click/drag UI options
        are included.
        Parameter:
            event (sequence): data describing the input. In this case, it's
            just the keyboard input used to access this method.
        """
        savelist = [] # a list of variables to be written to a file. This
        # includes everything needed to restore a game to its previous state.

        savelist.append(self.player.color) # whose turn it is
        savelist.append(self.black_player.mode) # black's UI mode
        savelist.append(self.black_promotions) # black's promoted pawns
        savelist.append(self.white_player.mode) # white's UI mode
        savelist.append(self.white_promotions) # white's promoted pawns

        for piece in range(48): # location of all 48 pieces
            savelist.append(self.all_pieces[piece].location)

        # whether each pawn has moved and whether it's vulnerable
        savelist.append(self.black_pawn_1.moved)
        savelist.append(self.black_pawn_1.vulnerable)
        savelist.append(self.black_pawn_2.moved)
        savelist.append(self.black_pawn_2.vulnerable)
        savelist.append(self.black_pawn_3.moved)
        savelist.append(self.black_pawn_3.vulnerable)
        savelist.append(self.black_pawn_4.moved)
        savelist.append(self.black_pawn_4.vulnerable)
        savelist.append(self.black_pawn_5.moved)
        savelist.append(self.black_pawn_5.vulnerable)
        savelist.append(self.black_pawn_6.moved)
        savelist.append(self.black_pawn_6.vulnerable)
        savelist.append(self.black_pawn_7.moved)
        savelist.append(self.black_pawn_7.vulnerable)
        savelist.append(self.black_pawn_8.moved)
        savelist.append(self.black_pawn_8.vulnerable)

        savelist.append(self.white_pawn_1.moved)
        savelist.append(self.white_pawn_1.vulnerable)
        savelist.append(self.white_pawn_2.moved)
        savelist.append(self.white_pawn_2.vulnerable)
        savelist.append(self.white_pawn_3.moved)
        savelist.append(self.white_pawn_3.vulnerable)
        savelist.append(self.white_pawn_4.moved)
        savelist.append(self.white_pawn_4.vulnerable)
        savelist.append(self.white_pawn_5.moved)
        savelist.append(self.white_pawn_5.vulnerable)
        savelist.append(self.white_pawn_6.moved)
        savelist.append(self.white_pawn_6.vulnerable)
        savelist.append(self.white_pawn_7.moved)
        savelist.append(self.white_pawn_7.vulnerable)
        savelist.append(self.white_pawn_8.moved)
        savelist.append(self.white_pawn_8.vulnerable)

        # whether each rook or king has moved
        savelist.append(self.black_rook_1.moved)
        savelist.append(self.black_rook_2.moved)
        savelist.append(self.black_king.moved)
        savelist.append(self.white_rook_1.moved)
        savelist.append(self.white_rook_2.moved)
        savelist.append(self.white_king.moved)

        savelist.append(self.mode) # easy, hard, or human mode

        if self.autosave: # if this is being autosaved
            filename = "tempchess.txt" # indicate such
        else: # if it's a deliberate save
            filename = self.text_box.get() + ".txt" # get the filename
            if filename == ".txt": # if it's empty,
                filename = "savechess.txt" # use a default
                self.text_box.insert(0, "savechess") # and say so

        try: # write the above-created list to a file with the specified name
            with open(filename, 'w', encoding = 'utf-8-sig') as output:
                for item in savelist:
                    output.write(str(item) + "\n")
            if not self.autosave:
                self.status_message.config(text = "File saved as " + \
                filename + ".")
        except: # if that doesn't work for some reason, say so
            self.status_message.config(text = "Error saving file.")

    def load(self, event):
        """
        Looks for a file with a name matching whatever was entered in the text
        box. If nothing is in the text box, it looks for a file called
        "savechess.txt" in the current working directory. If a file is found,
        its data are used to restore a save state. Click/drag UI options are
        included.
        Parameter:
            event (sequence): data describing the input. In this case, it's
            just the keyboard input used to access this method.
        """
        savelist = [] # a list that will be populated from a file

        if self.autosave: # if this is from an autosave
            filename = "tempchess.txt" # indicate such
        else: # if it's a deliberate load
            filename = self.text_box.get() + ".txt" # get the filename
            if filename == ".txt": # if it's empty
                filename = "savechess.txt" # use a default
                self.text_box.insert(0, "savechess") # and say so

        try: # open the specified file and write the contents to the list
            with open(filename, 'r', encoding = 'utf-8-sig') as file:
                for line in file:
                    savelist.append(line[:-1])
        except: # if that doesn't work for some reason, say so
            self.status_message.config(text = "Save file not found.")
            return # and end this method early

        if savelist[-1] == "easy":
            self.new_easy() # easy mode
        elif savelist[-1] == "hard":
            self.new_hard() # hard mode
        else:
            self.new_human() # human mode

        # Make a dictionary of location:Square.
        Chess.all_squares = {str(row)+str(column):Square(str(row)+str(column))
            for row in range(8) for column in range(8)}

        if savelist[0] == "black":
            self.player = self.black_player # black's turn
        else:
            self.player = self.white_player # white's turn
        if self.black_player.mode != savelist[1]: # if in wrong black UI mode
            if self.audio: # if audio is on
                # suppress it because the load/undo sound is higher priority
                # than the UI mode sound
                self.audio = False
                self.black_ui_toggle() # toggle the UI mode
                self.audio = True # and turn audio back on
            else: # if audio is off
                self.black_ui_toggle() # toggle the UI mode
        self.black_promotions = int(savelist[2]) # promoted black pawns
        if self.white_player.mode != savelist[3]: # if in wrong white UI mode
            if self.audio: # if audio is on
                # suppress it because the load/undo sound is higher priority
                # than the UI mode sound
                self.audio = False
                self.white_ui_toggle() # toggle the UI mode
                self.audio = True # and turn audio back on
            else: # if audio is off
                self.white_ui_toggle() # toggle the UI mode
        self.white_promotions = int(savelist[4]) # promoted white pawns

        for piece in range(48): # location of all 48 pieces
            self.all_pieces[piece].location = savelist[piece+5]
            if self.all_pieces[piece].location != "88":
                Chess.all_squares.get(savelist[piece+5]).piece = \
                self.all_pieces[piece]

        # whether each pawn has moved and whether it's vulnerable
        self.black_pawn_1.moved = (savelist[53] == "True")
        self.black_pawn_1.vulnerable = (savelist[54] == "True")
        self.black_pawn_2.moved = (savelist[55] == "True")
        self.black_pawn_2.vulnerable = (savelist[56] == "True")
        self.black_pawn_3.moved = (savelist[57] == "True")
        self.black_pawn_3.vulnerable = (savelist[58] == "True")
        self.black_pawn_4.moved = (savelist[59] == "True")
        self.black_pawn_4.vulnerable = (savelist[60] == "True")
        self.black_pawn_5.moved = (savelist[61] == "True")
        self.black_pawn_5.vulnerable = (savelist[62] == "True")
        self.black_pawn_6.moved = (savelist[63] == "True")
        self.black_pawn_6.vulnerable = (savelist[64] == "True")
        self.black_pawn_7.moved = (savelist[65] == "True")
        self.black_pawn_7.vulnerable = (savelist[66] == "True")
        self.black_pawn_8.moved = (savelist[67] == "True")
        self.black_pawn_8.vulnerable = (savelist[68] == "True")

        self.white_pawn_1.moved = (savelist[69] == "True")
        self.white_pawn_1.vulnerable = (savelist[70] == "True")
        self.white_pawn_2.moved = (savelist[71] == "True")
        self.white_pawn_2.vulnerable = (savelist[72] == "True")
        self.white_pawn_3.moved = (savelist[73] == "True")
        self.white_pawn_3.vulnerable = (savelist[74] == "True")
        self.white_pawn_4.moved = (savelist[75] == "True")
        self.white_pawn_4.vulnerable = (savelist[76] == "True")
        self.white_pawn_5.moved = (savelist[77] == "True")
        self.white_pawn_5.vulnerable = (savelist[78] == "True")
        self.white_pawn_6.moved = (savelist[79] == "True")
        self.white_pawn_6.vulnerable = (savelist[80] == "True")
        self.white_pawn_7.moved = (savelist[81] == "True")
        self.white_pawn_7.vulnerable = (savelist[82] == "True")
        self.white_pawn_8.moved = (savelist[83] == "True")
        self.white_pawn_8.vulnerable = (savelist[84] == "True")

        # whether each rook or king has moved
        self.black_rook_1.moved = (savelist[85] == "True")
        self.black_rook_2.moved = (savelist[86] == "True")
        self.black_king.moved = (savelist[87] == "True")
        self.white_rook_1.moved = (savelist[88] == "True")
        self.white_rook_2.moved = (savelist[89] == "True")
        self.white_king.moved = (savelist[90] == "True")

        if self.player.mode == "click": # current UI mode binding
            self.board.bind("<Button-1>", self.click_click)
        else:
            self.board.bind("<Button-1>", self.click_hold)

        if self.player is self.black_player: # announce whose turn it is
            self.status_message.config(text = "File loaded from " + \
            filename + "! Black's turn.")
        else:
            self.status_message.config(text = "File loaded from " + \
            filename + "! White's turn.")

        if self.black_king.location == "88": # if white has already won
            self.board.unbind("<Button-1>") # unbind the mouse
            self.status_message.config(text = "White wins!") # announce winner
        if self.white_king.location == "88": # if black has already won
            self.board.unbind("<Button-1>") # unbind the mouse
            self.status_message.config(text = "Black wins!") # announce winner

        self.check_castles() # check which castle buttons should be active
        self.refresh_images() # display images for each piece

    def undo(self, event):
        """
        Undoes the last human move (plus an AI move, if relevant) by loading the
        temporary save file. If there's no temporary save file, a generic
        loading error message is displayed. If a new game was just started or
        loaded and no one has moved yet, undo will go back to the previous
        game. Undo can be used even after someone has won. Undo serves as a
        sort of crash protection, as it saves the entire game state every time
        someone moves - just start the program up and hit undo.
        Parameter:
            event (sequence): data describing the input. In this case, it's
            just the keyboard input used to access this method.
        """
        self.autosave = True # specify that this load is from an autosave
        self.load(event) # load, and it'll use the right data automatically
        self.autosave = False # turn autosave flag back off

        if self.player is self.black_player: # say whose turn it is
            player = "Black"
        else:
            player = "White"
        self.status_message.config(text = "Move undone. " + \
            player + "'s turn.")

    def check_castles(self):
        """
        Checks if anyone can castle, then makes the appropriate buttons
            available.
        """
        # if the castling area is empty, it's that player's turn, and the rook
        # and king haven't moved, enable. else, disable. if the game is over,
        # the buttons are disabled.
        if(not self.black_rook_1.moved and not self.black_king.moved and
        self.black_king.location != "88" and \
        self.white_king.location != "88" and
        Chess.all_squares.get("10").piece is None and
        Chess.all_squares.get("20").piece is None and
        Chess.all_squares.get("30").piece is None):
            self.castle_black_left_button.config(state=NORMAL)
        else:
            self.castle_black_left_button.config(state=DISABLED)
        if(not self.black_rook_2.moved and not self.black_king.moved and
        self.black_king.location != "88" and \
        self.white_king.location != "88" and
        self.player is self.black_player and
        Chess.all_squares.get("50").piece is None and
        Chess.all_squares.get("60").piece is None):
            self.castle_black_right_button.config(state=NORMAL)
        else:
            self.castle_black_right_button.config(state=DISABLED)
        if(not self.white_rook_1.moved and not self.white_king.moved and
        self.black_king.location != "88" and \
        self.white_king.location != "88" and
        self.player is self.white_player and
        Chess.all_squares.get("17").piece is None and
        Chess.all_squares.get("27").piece is None and
        Chess.all_squares.get("37").piece is None):
            self.castle_white_left_button.config(state=NORMAL)
        else:
            self.castle_white_left_button.config(state=DISABLED)
        if(not self.white_rook_2.moved and not self.white_king.moved and
        self.black_king.location != "88" and \
        self.white_king.location != "88" and
        self.player is self.white_player and
        Chess.all_squares.get("57").piece is None and
        Chess.all_squares.get("67").piece is None):
            self.castle_white_right_button.config(state=NORMAL)
        else:
            self.castle_white_right_button.config(state=DISABLED)

    def generate_all_movesets(self):
        """
        Goes through each piece and generates a moveset for it.
        """
        self.black_rook_1.generate_moveset()
        self.black_knight_1.generate_moveset()
        self.black_bishop_1.generate_moveset()
        self.black_queen.generate_moveset()
        self.black_king.generate_moveset()
        self.black_bishop_2.generate_moveset()
        self.black_knight_2.generate_moveset()
        self.black_rook_2.generate_moveset()
        self.black_pawn_1.generate_moveset()
        self.black_pawn_2.generate_moveset()
        self.black_pawn_3.generate_moveset()
        self.black_pawn_4.generate_moveset()
        self.black_pawn_5.generate_moveset()
        self.black_pawn_6.generate_moveset()
        self.black_pawn_7.generate_moveset()
        self.black_pawn_8.generate_moveset()
        for piece in self.extra_black_queens:
            piece.generate_moveset()

        self.white_rook_1.generate_moveset()
        self.white_knight_1.generate_moveset()
        self.white_bishop_1.generate_moveset()
        self.white_queen.generate_moveset()
        self.white_king.generate_moveset()
        self.white_bishop_2.generate_moveset()
        self.white_knight_2.generate_moveset()
        self.white_rook_2.generate_moveset()
        self.white_pawn_1.generate_moveset()
        self.white_pawn_2.generate_moveset()
        self.white_pawn_3.generate_moveset()
        self.white_pawn_4.generate_moveset()
        self.white_pawn_5.generate_moveset()
        self.white_pawn_6.generate_moveset()
        self.white_pawn_7.generate_moveset()
        self.white_pawn_8.generate_moveset()
        for piece in self.extra_white_queens:
            piece.generate_moveset()

    def new_easy(self):
        """
        Starts a new game on one-player easy mode.
        """

        # Generate the board.
        self.draw_board()

        # Set easy mode.
        self.mode = "easy"

        # Highlight the button of the current mode, and make sure the other
        # buttons are not highlighted.
        self.easy_button.config(fg="white", bg="black")
        self.hard_button.config(fg="black", bg="#ECE9D8")
        self.human_button.config(fg="black", bg="#ECE9D8")

    def new_hard(self):
        """
        Starts a new game on one-player hard mode.
        """

        # Generate the board.
        self.draw_board()

        # Set easy mode.
        self.mode = "hard"

        # Highlight the button of the current mode, and make sure the other
        # buttons are not highlighted.
        self.easy_button.config(fg="black", bg="#ECE9D8")
        self.hard_button.config(fg="white", bg="black")
        self.human_button.config(fg="black", bg="#ECE9D8")

    def new_human(self):
        """
        Starts a new game on two-player mode.
        """

        # Generate the board.
        self.draw_board()

        # Set two-player mode.
        self.mode = "human"

        # Highlight the button of the current mode, and make sure the other
        # buttons are not highlighted.
        self.easy_button.config(fg="black", bg="#ECE9D8")
        self.hard_button.config(fg="black", bg="#ECE9D8")
        self.human_button.config(fg="white", bg="black")

    def easy_move(self):
        """
        This does nothing but choose a valid piece and move, and carry it out.
        """
        # create a set of all AI pieces
        living_pieces = {self.black_rook_1, self.black_knight_1,
        self.black_bishop_1, self.black_queen, self.black_king,
        self.black_bishop_2, self.black_knight_2, self.black_rook_2,
        self.black_pawn_1, self.black_pawn_2, self.black_pawn_3,
        self.black_pawn_4, self.black_pawn_5, self.black_pawn_6,
        self.black_pawn_7, self.black_pawn_8}
        for extra in self.extra_black_queens:
            living_pieces.add(extra)

        dead_pieces = set() # empty set for invalid AI pieces
        self.generate_all_movesets()
        for piece in living_pieces:
            # if a piece is dead or has no available moves
            if piece.location == "88" or len(piece.moveset) == 0:
                dead_pieces.add(piece) # add to this set
        living_pieces -= dead_pieces # remove this set from the total

        piece_to_move = sample(living_pieces, 1)[0] # pick a random piece
        move = sample(piece_to_move.moveset, 1)[0] # and a random move

        for piece in living_pieces:
            if self.white_king.location in piece.moveset: # if the AI win now
                piece_to_move = piece # use an appropriate piece
                move = self.white_king.location # and win

        # color the squares to indicate the move's origin and target
        self.board.itemconfig(self.squares[int(piece_to_move.location[0])]
            [int(piece_to_move.location[1])], fill="darkblue")
        self.board.itemconfig(self.squares[int(move[0])]
            [int(move[1])], fill="darkgreen")

        self.move(piece_to_move, move) # carry out the move
        self.check_castles() # check castling buttons
        # if audio is on and the AI didn't just win
        if self.audio and self.white_king.location != "88":
            mixer.music.load(self.sound_folder + "computer_move.ogg")
            mixer.music.play() # play the 'computer_move' sound

    def hard_move(self):
        """
        Tries to capture valuable pieces. Defends valuable pieces by capturing
        the threat or by fleeing. Tries to avoid moving the king too much or
        moving the same piece back and forth repeatedly.
        """
        # create a set of all AI pieces
        living_pieces = {self.black_rook_1, self.black_knight_1,
        self.black_bishop_1, self.black_queen, self.black_king,
        self.black_bishop_2, self.black_knight_2, self.black_rook_2,
        self.black_pawn_1, self.black_pawn_2, self.black_pawn_3,
        self.black_pawn_4, self.black_pawn_5, self.black_pawn_6,
        self.black_pawn_7, self.black_pawn_8}
        for extra in self.extra_black_queens:
            living_pieces.add(extra)

        dead_pieces = set() # empty set for invalid AI pieces
        self.generate_all_movesets()
        for piece in living_pieces:
            # if a piece is dead or has no available moves
            if piece.location == "88" or len(piece.moveset) == 0:
                dead_pieces.add(piece) # add to this set
        living_pieces -= dead_pieces # remove this set from the total

        piece_to_move = sample(living_pieces, 1)[0] # pick a random piece
        move = sample(piece_to_move.moveset, 1)[0] # and a random move

        # make a set of all enemy pieces
        enemy_pieces = {self.white_rook_1, self.white_knight_1,
        self.white_bishop_1, self.white_queen, self.white_king,
        self.white_bishop_2, self.white_knight_2, self.white_rook_2,
        self.white_pawn_1, self.white_pawn_2, self.white_pawn_3,
        self.white_pawn_4, self.white_pawn_5, self.white_pawn_6,
        self.white_pawn_7, self.white_pawn_8}
        for extra in self.extra_white_queens:
            enemy_pieces.add(extra)

        dead_enemies = set() # make an empty set for nonthreatening enemies
        for piece in enemy_pieces:
            # if a piece is dead or has no available moves
            if piece.location == "88" or len(piece.moveset) == 0:
                dead_enemies.add(piece) # consider it dead
        enemy_pieces -= dead_enemies # remove this set from the total

        enemy_moves = set() # make an empty set for enemy moves
        for piece in enemy_pieces:
            enemy_moves |= piece.moveset # add all pieces' moves to this set

        safe_moves = set() # a set for safe moves
        safe_pieces = set() # a set for safe pieces
        for piece in living_pieces:
            # if you start with a piece's moveset and then remove all the
            # squares where the enemy could move and the piece has some squares
            # still available, it's safe to move
            if len(piece.moveset - enemy_moves) > 0:
                # add those moves to the safe moves
                safe_moves |= piece.moveset - enemy_moves
                safe_pieces.add(piece) # add that piece to the safe pieces

        # while the randomly-chosen move isn't safe but there were some
        # available, or the randomly-chosen piece is the king and the RNG
        # puts a stop to it
        while (move not in safe_moves and len(safe_moves) > 5) or \
        (piece_to_move is self.black_king and randint(0,9) in range(9)):
            piece_to_move = sample(safe_pieces, 1)[0] # pick another piece
            # and another move
            move = sample(piece_to_move.moveset & safe_moves, 1)[0]

        # check the queenside knights
        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.black_knight_1, self.white_knight_1)
        if decision[0]: # if there's a capture or escape
            # if there's a capture or the current plan is to escape with a
            # lower-priority piece or the moving piece isn't a knight
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_knight":
                piece_to_move = decision[2] # use the returned piece
                move = decision[3] # and use the returned move

        # check the kingside knights
        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.black_knight_2, self.white_knight_2)
        if decision[0]: # if there's a capture or escape
            # if there's a capture or the current plan is to escape with a
            # lower-priority piece or the moving piece isn't a knight
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_knight":
                piece_to_move = decision[2] # use the returned piece
                move = decision[3] # and use the returned move

        # check the queenside bishops
        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.black_bishop_1, self.white_bishop_1)
        if decision[0]: # if there's a capture or escape
            # if there's a capture or the current plan is to escape with a
            # lower-priority piece or the moving piece isn't a bishop
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_bishop":
                piece_to_move = decision[2] # use the returned piece
                move = decision[3] # and use the returned move

        # check the kingside bishops
        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.black_bishop_2, self.white_bishop_2)
        if decision[0]: # if there's a capture or escape
            # if there's a capture or the current plan is to escape with a
            # lower-priority piece or the moving piece isn't a bishop
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_bishop":
                piece_to_move = decision[2] # use the returned piece
                move = decision[3] # and use the returned move

        # check the queenside rooks
        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.black_rook_1, self.white_rook_1)
        if decision[0]: # if there's a capture or escape
            # if there's a capture or the current plan is to escape with a
            # lower-priority piece or the moving piece isn't a rook
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_rook":
                piece_to_move = decision[2] # use the returned piece
                move = decision[3] # and use the returned move

        # check the kingside rooks
        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.black_rook_2, self.white_rook_2)
        if decision[0]: # if there's a capture or escape
            # if there's a capture or the current plan is to escape with a
            # lower-priority piece or the moving piece isn't a rook
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_rook":
                piece_to_move = decision[2] # use the returned piece
                move = decision[3] # use the returned move

        # check the queens
        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.black_queen, self.white_queen)
        if decision[0]: # if there's a capture or escape
            # if there's a capture or the current plan is to escape with a
            # lower-priority piece or the moving piece isn't a queen
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_queen":
                piece_to_move = decision[2] # use the returned piece
                move = decision[3] # use the returned move

        # check the extra queens
        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.extra_black_queens[1], self.extra_white_queens[1])
        if decision[0]: # if there's a capture or escape
            # if there's a capture or the current plan is to escape with a
            # lower-priority piece or the moving piece isn't a queen
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_queen":
                piece_to_move = decision[2] # use the returned piece
                move = decision[3] # use the returned move

        # check the kings
        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.black_king, self.white_king)
        if decision[0]: # if there's a capture or escape
            # if there's a capture or the current plan is to escape with a
            # lower-priority piece or the moving piece isn't a king
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_king":
                piece_to_move = decision[2] # use the returned piece
                move = decision[3] # use the returned move

        # fill the source and target squares with the proper colors
        self.board.itemconfig(self.squares[int(piece_to_move.location[0])]
            [int(piece_to_move.location[1])], fill="darkblue")
        self.board.itemconfig(self.squares[int(move[0])]
            [int(move[1])], fill="darkgreen")

        self.move(piece_to_move, move) # move
        self.check_castles() # check castling buttons
        # if there's audio and the AI didn't just win
        if self.audio and self.white_king.location != "88":
            mixer.music.load(self.sound_folder + "computer_move.ogg")
            mixer.music.play() # play the 'computer_move' sound

    def piece_priority(self, living_pieces, safe_moves, enemy_pieces,
    enemy_moves, check_ally, check_enemy):
        """
        Determines which move is the most important. Tries to capture first. If
        there's nothing to capture, avoids being captured if necessary. If a
        piece is in danger but it may be safely rescued by capturing an enemy
        piece (even if it's a less-valuable piece), it uses that strategy.
        """
        for piece in living_pieces:
            if check_enemy.location in piece.moveset: # if AI can capture
                return [True, True, piece, check_enemy.location] # do so

        if check_ally.location in enemy_moves: # if AI piece is threatened
            for enemy in enemy_pieces: # look at enemy pieces
                if enemy.location in safe_moves: # if enemy can be captured
                    for piece in living_pieces: # look at available pieces
                        # find one that can capture the enemy
                        if enemy.location in piece.moveset:
                            return[True, True, piece, enemy.location] # do so
            for loc in check_ally.moveset: # look at the piece's moveset
                if loc not in enemy_moves: # if a move is safe
                    # if the AI is considering moving right back where it came
                    # from and there's other stuff it could do,
                    if ((check_ally is self.last_ai_piece and loc == \
                    self.last_source) and len(check_ally.moveset) > 1):
                        continue # pick a different target
                    return [True, False, check_ally, loc] # successful escape

        return [False, False] # no capture or escape

    def click_click(self, event):
        """
        Carry out a human player's desired move, if possible.
        Parameter:
            event (sequence): data describing the input. In this case, it's
                just mouse cursor coordinates when the mouse was left-clicked.
        """

        # Parses the mouse cursor location at the time of the click into a
        # string that the game's logic can handle.
        click = str(event.x//50) + str(event.y//50)
        token = Chess.all_squares.get(click).piece

        if self.first_click: # if it's the first click
            if not self.choose_piece(token): # and no piece was chosen
                return # return out of the method
            self.first_click = False # a piece was chosen, so first_click is
            # now False
        else:
            # on the second click, a target has been chosen
            self.choose_target(click)
            self.first_click = True # and first_click is True again

    def click_hold(self, event):
        """
        Indicates which piece a player wants to move.
        Parameter:
            event (sequence): data describing the input. In this case, it's
                just mouse cursor coordinates when the mouse was left-clicked.
        """

        # Parses the mouse cursor location at the time of the click into a
        # string that the game's logic can handle.
        click = str(event.x//50) + str(event.y//50)
        token = Chess.all_squares.get(click).piece

        if not self.choose_piece(token): # if no piece was chosen
            return # return out of the method
        # by this point a piece was chosen
        # so make that piece "disappear" from its square
        self.board.itemconfig(self.square_overlay[int(click[0])]
        [int(click[1])], image=self.piece_pics.get("transparent_square"))
        # and appear
        self.board.itemconfig(self.dragged_piece, image=self.piece_pics.get
        (self.chosen_piece.type))
        # at the user's mouse cursor
        self.board.coords(self.dragged_piece, event.x, event.y)
        self.board.bind("<B1-Motion>", self.click_drag) # bind click_drag()
        # and click_release()
        self.board.bind("<ButtonRelease-1>", self.click_release)

    def click_drag(self, event):
        """
        Visually drags a piece across the board.
        Parameter:
            event (sequence): data describing the input. In this case, it's
                just mouse cursor coordinates when the mouse moved, while the
                left mouse button was held down.
        """
        # moves the dragged_piece to the event coordinates (the mouse cursor)
        # whenever the user moves the mouse while dragging a piece
        self.board.coords(self.dragged_piece, event.x, event.y)

    def click_release(self, event):
        """
        Indicates which square a player wants to move to. Humans only.
        Parameter:
            event (sequence): data describing the input. In this case, it's
            just mouse cursor coordinates when the left mouse button was
            released.
        """
        # clear the dragged piece
        self.board.itemconfig(self.dragged_piece, image=self.piece_pics.get
        ("transparent_square"))
        # choose the cursor's current location as a target
        self.choose_target(str(event.x//50) + str(event.y//50))
        self.board.unbind("<B1-Motion>") # unbind the 'motion' effect
        self.board.unbind("<ButtonRelease-1>") # and the 'release' effect
        self.refresh_images() # refresh the board to see what we've got

    def choose_piece(self, token):
        """
        Chooses a piece to move. Humans only.
        Parameter:
            token (Piece): the piece that the player wants to select
        """
        if token is None: # if a square with no piece was chosen
            return False # no piece chosen
        if token.color != self.player.color: # if an opponent's piece was chosen
            return False # no piece chosen
        self.chosen_piece = token # by now, we've chosen a piece
        token.generate_moveset() # what are its possible moves?
        if len(token.moveset) == 0: # if it can't move
            return False # no piece chosen
        if self.player is self.white_player: # if it's white's turn
            color = "" # don't add a color prefix
        else: # otherwise
            color = "dark" # add 'dark'
        # now we color the piece's square with a variety of blue
        self.board.itemconfig(self.squares[int(token.location[0])]
        [int(token.location[1])], fill=color+"blue")
        for move in token.moveset: # for every move the piece can make
            # color those squares a variety of green
            self.board.itemconfig(self.squares[int(move[0])][int(move[1])],
            fill=color+"green")
        if self.audio: # if audio is on
            mixer.music.load(self.sound_folder + "select_piece.ogg")
            mixer.music.play() # play the 'select_piece' sound
        return True # piece was chosen

    def choose_target(self, click):
        """
        Moves a chosen piece to the selected square, if possible. Humans only.
        Parameter:
            click (string): a string representing the location of the selected
                destination square
        """
        # color the board with white and black squares
        for row in range(8):
            for column in range(8):
                if (row+column)%2 == 0:
                    color = 'white'
                else:
                    color = 'black'
                self.board.itemconfig(self.squares[row][column], fill=color)
        if self.player is self.white_player: # if it's white's turn
            color = "dark" # add a 'dark' color prefix
        else: # otherwise
            color = "" # add no prefix
        # if there was a previous move
        if self.last_source is not None and self.last_target is not None:
            # color that origin square a variety of blue
            self.board.itemconfig(self.squares[int(self.last_source[0])]
                [int(self.last_source[1])], fill=color+"blue")
            # and color the target square a variety of green
            self.board.itemconfig(self.squares[int(self.last_target[0])]
                [int(self.last_target[1])], fill=color+"green")
        if click == None: # if there was no piece on the target square
            self.first_click = True # go back to first click
            return # and return out of this method
        # if the target square is in the chosen piece's moveset
        if click in self.chosen_piece.moveset:
            self.autosave = True # set autosave
            self.save(0) # and save
            self.autosave = False # turn off autosave
            self.move(self.chosen_piece, click) # move the piece
            # if black hasn't lost
            if self.black_king.location != "88":
                delay = 0
                # if audio is on and white hasn't lost
                if self.audio and self.white_king.location != "88":
                    delay = 1000 # set a 1000ms delay
                    mixer.music.load(self.sound_folder + "move_piece.ogg")
                    mixer.music.play() # play the 'move_piece' sound
                if self.mode == "easy": # if easy mode is on
                    self.parent.after(delay,self.easy_move) # do an easy move
                if self.mode == "hard": # if hard mode is on
                    self.parent.after(delay,self.hard_move) # do a hard move
            self.check_castles() # check castling buttons

    def move(self, chosen_piece, destination):
        """
        Carries out a player's move (human or computer), with win logic.
        Parameters:
            chosen_piece (Piece): the Piece that the player (human or AI) is
                moving
            destination (string): the string representation of the destination
                square
        """
        # if there was a piece moved previously
        if self.last_source is not None and self.last_target is not None:
            for row in range(8): # go by row
                for column in range(8): # and column
                    if (row+column)%2 == 0: # and every other square
                        color = 'white' # should be white
                    else:
                        color = 'black' # or black
                    # recolor the board
                    self.board.itemconfig(self.squares[row][column], fill=color)
        self.last_source = chosen_piece.location # this piece is the last source
        self.last_target = destination # its destination is the last target
        if self.player is self.white_player: # if white went
            color = "" # no color prefix
            self.status_message.config(text = "Black's turn.") # announce black
        else: # if black went
            color = "dark" # 'dark' color prefix
            self.status_message.config(text = "White's turn.") # announce white
        # color the last source with a variety of blue
        self.board.itemconfig(self.squares[int(self.last_source[0])]
            [int(self.last_source[1])], fill=color+"blue")
        # color the last target with a variety of green
        self.board.itemconfig(self.squares[int(self.last_target[0])]
            [int(self.last_target[1])], fill=color+"green")

        self.safe_pawns() # all pawns are safe from en passant
        # piece on the target square
        target_piece = Chess.all_squares.get(destination).piece
        # chosen piece's original location
        original_location = chosen_piece.location
        if hasattr(chosen_piece, "moved"): # if this piece has a 'moved' attr
            chosen_piece.moved = True # this piece has moved
        if "pawn" in chosen_piece.type: # if this piece is a pawn
            # and it was allowed to move 2 squares
            if int(destination[1]) - int(chosen_piece.location[1]) \
            in range(-2,3,4):
                chosen_piece.vulnerable = True # it's vulnerable
            # the piece on the square behind the pawn
            behind = Chess.all_squares.get(destination[0] +
            str(int(destination[1])-chosen_piece.direction)).piece
            if behind is not None: # if there's actually a piece there
                if "pawn" in behind.type: # and it's a pawn
                    if behind.vulnerable: # and it was vulnerable
                        behind.location = "88" # that pawn is captured
                        # and the square is now empty
                        Chess.all_squares.get(destination[0] +
                        str(int(destination[1])-chosen_piece.direction)) \
                        .piece = None
            # if the pawn got to the top row
            if destination[1] == "0":
                chosen_piece.location = "88" # the pawn gets sort of 'captured'
                # if there was an enemy on that square
                if target_piece is not None:
                    target_piece.location = "88" # it's captured
                # and the former pawn becomes the next extra queen
                target_piece = Chess.all_squares.get(destination).piece = \
                self.extra_white_queens[self.white_promotions]
                target_piece.location = destination # located at the destination
                self.white_promotions += 1 # increment the extra queen counter
                chosen_piece = target_piece # chosen piece set to target
            # if the pawn got to the bottom row
            if destination[1] == "7":
                chosen_piece.location = "88" # the pawn gets sort of 'captured'
                # if there was an enemy on that square
                if target_piece is not None:
                    target_piece.location = "88" # it's captured
                # and the former pawn becomes the next extra queen
                target_piece = Chess.all_squares.get(destination).piece= \
                self.extra_black_queens[self.black_promotions]
                target_piece.location = destination # located at the destination
                self.black_promotions += 1 # increment the extra queen counter
                chosen_piece = target_piece # chosen piece set to target
        if target_piece is not None: # if there was a piece on the target square
            # if it really was a capture and not a promotion
            if target_piece.color != chosen_piece.color:
                target_piece.location = "88" # the target piece is captured
            if self.black_king.location == "88": # if it was the black king
                self.game_end("White") # end the game with white winner
            if self.white_king.location == "88": # if it was the white king
                self.game_end("Black") # end the game with black winner

        self.check_castles() # check the castle buttons
        Chess.all_squares.get(destination).piece = target_piece \
        = chosen_piece # put chosen piece into target and destination pieces
        # original location is now empty
        Chess.all_squares.get(original_location).piece = None
        # set the chosen piece's location to the destination
        chosen_piece.location = destination
        self.refresh_images() # refresh the images
        if self.player is self.white_player: # if it was white's turn
            self.player = self.black_player # now it's black's
        else: # if it was black's turn
            self.player = self.white_player # now it's white's
        if self.black_king.location != "88" and self.white_king.location \
        != "88": # if the game continues
            if self.player.mode == "click": # if it's click mode
                self.board.bind("<Button-1>", self.click_click) # bind that
            else: # otherwise
                self.board.bind("<Button-1>", self.click_hold) # bind drag

    def game_end(self, winner):
        """
        Handles end-of-game actions, including messages, event unbindings,
        and sound effects.
        Parameters:
            winner (string): "Black" or "White", describing the winner
        """
        self.status_message.config(text = winner + " wins!") # announce the win
        self.board.unbind("<Button-1>") # unbind the mouse
        # disable the castle buttons
        self.castle_black_left_button.config(state=DISABLED)
        self.castle_black_right_button.config(state=DISABLED)
        self.castle_white_left_button.config(state=DISABLED)
        self.castle_white_right_button.config(state=DISABLED)
        if self.audio: # if audio is on
            mixer.music.load(self.sound_folder + "torpedo.ogg")
            mixer.music.play() # fire torpedo
            time.sleep(1) # wait 1sec
            mixer.music.play() # fire again
            time.sleep(1) # wait 1sec
            mixer.music.play() # and again
            time.sleep(1) # wait 1sec
            mixer.music.load(self.sound_folder + "explosion.ogg")
            mixer.music.play() # play explosion sound

    def safe_pawns(self):
        """
        When a player starts their turn, all of their pieces start out as not
        vulnerable.
        """
        if self.player.color == "white": # if it's white's turn
            # make all their pawns safe
            self.white_pawn_1.vulnerable = False
            self.white_pawn_2.vulnerable = False
            self.white_pawn_3.vulnerable = False
            self.white_pawn_4.vulnerable = False
            self.white_pawn_5.vulnerable = False
            self.white_pawn_6.vulnerable = False
            self.white_pawn_7.vulnerable = False
            self.white_pawn_8.vulnerable = False
        else: # if it's black's turn
            # make all their pawns safe
            self.black_pawn_1.vulnerable = False
            self.black_pawn_2.vulnerable = False
            self.black_pawn_3.vulnerable = False
            self.black_pawn_4.vulnerable = False
            self.black_pawn_5.vulnerable = False
            self.black_pawn_6.vulnerable = False
            self.black_pawn_7.vulnerable = False
            self.black_pawn_8.vulnerable = False

    def castle_black_left(self):
        """
        Castles at black queenside.
        """
        self.safe_pawns() # sets the current player's pawns to safe
        # color the board with black and white squares
        for row in range(8):
            for column in range(8):
                if (row+column)%2 == 0:
                    color = 'white'
                else:
                    color = 'black'
                self.board.itemconfig(self.squares[row][column], fill=color)
        # hard-coded last-move indicator, since this is a hard-coded move
        self.board.itemconfig(self.squares[3][0], fill="darkblue")
        self.board.itemconfig(self.squares[2][0], fill="darkgreen")
        # give each square its proper piece
        Chess.all_squares.get("00").piece = None
        Chess.all_squares.get("20").piece = self.black_king
        Chess.all_squares.get("30").piece = self.black_rook_1
        Chess.all_squares.get("40").piece = None
        # give its piece its proper location and status
        self.black_king.location = "20"
        self.black_king.moved = True
        self.black_rook_1.location = "30"
        self.black_rook_1.moved = True
        self.player = self.white_player # other player's turn
        self.check_castles() # refresh the castling buttons
        self.refresh_images() # as well as the piece icons
        self.status_message.config(text = "Black castled queenside! " + \
        "White's turn.") # announce the event
        if self.audio: # if audio is on
            mixer.music.load(self.sound_folder + "castle.ogg")
            mixer.music.play() # play the 'castle' sound

    def castle_black_right(self):
        """
        Castles at black kingside.
        """
        self.safe_pawns() # sets the current player's pawns to safe
        # color the board with black and white squares
        for row in range(8):
            for column in range(8):
                if (row+column)%2 == 0:
                    color = 'white'
                else:
                    color = 'black'
                self.board.itemconfig(self.squares[row][column], fill=color)
        # hard-coded last-move indicator, since this is a hard-coded move
        self.board.itemconfig(self.squares[5][0], fill="darkblue")
        self.board.itemconfig(self.squares[6][0], fill="darkgreen")
        # give each square its proper piece
        Chess.all_squares.get("40").piece = None
        Chess.all_squares.get("50").piece = self.black_rook_2
        Chess.all_squares.get("60").piece = self.black_king
        Chess.all_squares.get("70").piece = None
        # give its piece its proper location and status
        self.black_rook_2.location = "50"
        self.black_rook_2.moved = True
        self.black_king.location = "60"
        self.black_king.moved = True
        self.player = self.white_player # other player's turn
        self.check_castles() # refresh the castling buttons
        self.refresh_images() # as well as the piece icons
        self.status_message.config(text = "Black castled kingside! " + \
        "White's turn.") # announce the event
        if self.audio: # if audio is on
            mixer.music.load(self.sound_folder + "castle.ogg")
            mixer.music.play() # play the 'castle' sound

    def castle_white_left(self):
        """
        Castles at white queenside.
        """
        self.safe_pawns() # sets the current player's pawns to safe
        # color the board with black and white squares
        for row in range(8):
            for column in range(8):
                if (row+column)%2 == 0:
                    color = 'white'
                else:
                    color = 'black'
                self.board.itemconfig(self.squares[row][column], fill=color)
        # hard-coded last-move indicator, since this is a hard-coded move
        self.board.itemconfig(self.squares[3][7], fill="blue")
        self.board.itemconfig(self.squares[2][7], fill="green")
        # give each square its proper piece
        Chess.all_squares.get("07").piece = None
        Chess.all_squares.get("27").piece = self.white_king
        Chess.all_squares.get("37").piece = self.white_rook_1
        Chess.all_squares.get("47").piece = None
        # give its piece its proper location and status
        self.white_king.location = "27"
        self.white_king.moved = True
        self.white_rook_1.location = "37"
        self.white_rook_1.moved = True
        self.player = self.black_player # other player's turn
        self.check_castles() # refresh the castling buttons
        self.refresh_images() # as well as the piece icons
        if self.audio: # if audio is on
            delay = 2000 # set a 2000ms delay
            mixer.music.load(self.sound_folder + "castle.ogg")
            mixer.music.play() # and play the 'castle' sound
        else: # if audio is off
            delay = 0 # set a delay of 0
        if self.mode == "easy": # if it's on easy mode
            self.parent.after(delay,self.easy_move) # AI makes an easy move
        if self.mode == "hard": # if it's on hard mode
            self.parent.after(delay,self.hard_move) # AI makes a hard move
        self.status_message.config(text = "White castled queenside! " + \
        "Black's turn.") # announce the event

    def castle_white_right(self):
        """
        Castles at white kingside.
        """
        self.safe_pawns() # sets the current player's pawns to safe
        # color the board with black and white squares
        for row in range(8):
            for column in range(8):
                if (row+column)%2 == 0:
                    color = 'white'
                else:
                    color = 'black'
                self.board.itemconfig(self.squares[row][column], fill=color)
        # hard-coded last-move indicator, since this is a hard-coded move
        self.board.itemconfig(self.squares[5][7], fill="blue")
        self.board.itemconfig(self.squares[6][7], fill="green")
        # give each square its proper piece
        Chess.all_squares.get("47").piece = None
        Chess.all_squares.get("57").piece = self.white_rook_2
        Chess.all_squares.get("67").piece = self.white_king
        Chess.all_squares.get("77").piece = None
        # give its piece its proper location and status
        self.white_rook_2.location = "57"
        self.white_rook_2.moved = True
        self.white_king.location = "67"
        self.white_king.moved = True
        self.player = self.black_player # other player's turn
        self.check_castles() # refresh the castling buttons
        self.refresh_images() # as well as the piece icons
        if self.audio: # if audio is on
            delay = 2000 # set a 2000ms delay
            mixer.music.load(self.sound_folder + "castle.ogg")
            mixer.music.play() # and play the 'castle' sound
        else: # if audio is off
            delay = 0 # set a delay of 0
        if self.mode == "easy": # if it's on easy mode
            self.parent.after(delay,self.easy_move) # AI makes an easy move
        if self.mode == "hard": # if it's on hard mode
            self.parent.after(delay,self.hard_move) # AI makes a hard move
        self.status_message.config(text = "White castled kingside! " + \
        "Black's turn.") # announce the event

    def refresh_images(self):
        """
        Looks at each Square. If the Square contains a Piece, the proper
        square_overlay cell has its image set to that piece's image. If the
        Square doesn't contain a Piece, the proper square_overlay cell has its
        image set to the transparent image.
        """
        for row in range(8):
            for column in range(8):
                # get the piece to be drawn
                drawpiece = Chess.all_squares.get(str(row)+str(column)).piece
                if drawpiece is not None: # if there's an actual piece there
                    # place the appropriate image in the appropriate spot
                    self.board.itemconfig(self.square_overlay[row][column],
                    image=self.piece_pics.get(drawpiece.type))
                else: # otherwise
                    # use the transparent image.
                    self.board.itemconfig(self.square_overlay[row][column],
                    image=self.piece_pics.get("transparent_square"))

    def black_ui_toggle(self):
        """
        Switches between the "click/click" move functionality and the
        "click/drag" move functionality for the black player.
        """
        if self.black_player.mode == "click": # if the player is in click mode
            self.black_player.mode = "drag" # switch to drag mode
            # label the button to reflect the change
            self.black_click_button.config(text = "Active mode:\nclick/drag")
            # if it's their turn and the game isn't over
            if self.player is self.black_player and \
            self.black_king.location != "88" and \
            self.white_king.location != "88":
                # bind click_hold() to the mouse button
                self.board.bind("<Button-1>", self.click_hold)
            self.choose_target(None) # in effect, clears the first_click attr

        else: # if the player is in drag mode
            self.black_player.mode = "click" # switch to click mode
            # label the button to reflect the change
            self.black_click_button.config(text = "Active mode:\nclick/click")
            # if it's their turn and the game isn't over
            if self.player is self.black_player and \
            self.black_king.location != "88" and \
            self.white_king.location != "88":
                # bind click_click() to the mouse button
                self.board.bind("<Button-1>", self.click_click)

        if self.audio: # if audio is on
            mixer.music.load(self.sound_folder + "ui_toggle.ogg")
            mixer.music.play() # play the 'ui_toggle' sound

    def white_ui_toggle(self):
        """
        Switches between the "click/click" move functionality and the
        "click/drag" move functionality for the white player.
        """
        if self.white_player.mode is "click": # if the player is in click mode
            self.white_player.mode = "drag" # switch to drag mode
            # label the button to reflect the change
            self.white_click_button.config(text = "Active mode:\nclick/drag")
            # if it's their turn and the game isn't over
            if self.player is self.white_player and \
            self.black_king.location != "88" and \
            self.white_king.location != "88":
                # bind click_hold() to the mouse button
                self.board.bind("<Button-1>", self.click_hold)
            self.choose_target(None) # in effect, clears the first_click attr

        else: # if the player is in drag mode
            self.white_player.mode = "click" # switch to click mode
            # label the button to reflect the change
            self.white_click_button.config(text = "Active mode:\nclick/click")
            # if it's their turn and the game isn't over
            if self.player is self.white_player and \
            self.black_king.location != "88" and \
            self.white_king.location != "88":
                # bind click_click() to the mouse button
                self.board.bind("<Button-1>", self.click_click)

        if self.audio: # if audio is on
            mixer.music.load(self.sound_folder + "ui_toggle.ogg")
            mixer.music.play() # play the 'ui_toggle' sound

    def audio_toggle(self, event):
        """
        Switches between audio mode and silent mode, with a message.
        Parameter:
            event (sequence): data describing the input. In this case, it's
            just the keyboard input used to access this method.
        """
        if self.audio: # if audio is on
            self.audio = False # turn it off
            mixer.music.stop() # stop all sounds
            # and announce such
            self.status_message.config(text = "Audio deactivated.")
        else: # otherwise
            self.audio = True # turn it on
            mixer.music.load(self.sound_folder + "audio_on.ogg")
            mixer.music.play() # play the 'audio_on' sound
            # and announce such
            self.status_message.config(text = "Audio activated.")

    def audio_from_folder(self, event):
        """
        Attempts to load audio from a specified folder. If that fails, attempts
        to load audio from the previous folder.
        Parameter:
            event (sequence): data describing the input. In this case, it's
            just the keyboard input used to access this method.
        """
        try:
            # initialize the mixer, since the user might have started the game
            # with a missing default sound folder, intending to choose one
            # at runtime
            mixer.init(buffer=512)
            # save the previous folder, just in case
            previous_sound = self.sound_folder
            try: # let's try the entered folder
                self.sound_folder = self.text_box.get() + "/" # get the name
                # and try everything
                mixer.music.load(self.sound_folder + "ui_toggle.ogg")
                mixer.music.load(self.sound_folder + "audio_on.ogg")
                mixer.music.load(self.sound_folder + "select_piece.ogg")
                mixer.music.load(self.sound_folder + "move_piece.ogg")
                mixer.music.load(self.sound_folder + "computer_move.ogg")
                mixer.music.load(self.sound_folder + "castle.ogg")
                mixer.music.load(self.sound_folder + "undo.ogg")
                mixer.music.load(self.sound_folder + "torpedo.ogg")
                mixer.music.load(self.sound_folder + "explosion.ogg")
                mixer.music.load(self.sound_folder + "game_start.ogg")
                self.status_message.config(text = "Audio loaded from " + \
                "entered sound folder.") # success message
            except: # entered folder was no good
                # failure message
                self.status_message.config(text = "Unable to load audio" + \
                "from entered sound folder (absent or corrupted).")
                # now try the previous sound folder. We don't need to try the
                # default folder because either the previous one was fine or
                # the default was attempted already.
                self.sound_folder = previous_sound + "/"
                mixer.music.load(self.sound_folder + "ui_toggle.ogg")
                mixer.music.load(self.sound_folder + "audio_on.ogg")
                mixer.music.load(self.sound_folder + "select_piece.ogg")
                mixer.music.load(self.sound_folder + "move_piece.ogg")
                mixer.music.load(self.sound_folder + "computer_move.ogg")
                mixer.music.load(self.sound_folder + "castle.ogg")
                mixer.music.load(self.sound_folder + "undo.ogg")
                mixer.music.load(self.sound_folder + "torpedo.ogg")
                mixer.music.load(self.sound_folder + "explosion.ogg")
                mixer.music.load(self.sound_folder + "game_start.ogg")
            # success, with some sort of audio. Bind the audio hotkey.
            self.parent.bind("<Control-a>", self.audio_toggle)
            self.parent.bind("<Control-A>", self.audio_toggle)
        except: # audio failed
            self.audio = False # turn off audio
            # inform the user of what happened
            self.status_message.config(text = "Unable to load audio. " + \
                "Either the entered sound folder, previous sound folder,\n" + \
                "and default sound folder are absent or corrupted, " + \
                "or pygame is not installed.")

    def icons_from_folder(self, event):
        """
        Attempts to load icons from a specified folder. If that fails, attempts
        to load icons from the previous folder.
        Parameter:
            event (sequence): data describing the input. In this case, it's
            just the keyboard input used to access this method.
        """
        try: # first we'll try the specified folder
            # save the previous one, just in case
            previous_icons = self.icon_folder
            icon_folder = self.text_box.get() + "/" # get the name
            # and try everything
            self.black_king_gif = PhotoImage(file=icon_folder+"black_king.gif")
            self.black_queen_gif = PhotoImage(file=icon_folder+"black_queen.gif")
            self.black_rook_gif = PhotoImage(file=icon_folder+"black_rook.gif")
            self.black_bishop_gif = PhotoImage(file=icon_folder+"black_bishop.gif")
            self.black_knight_gif = PhotoImage(file=icon_folder+"black_knight.gif")
            self.black_pawn_gif = PhotoImage(file=icon_folder+"black_pawn.gif")

            self.white_king_gif = PhotoImage(file=icon_folder+"white_king.gif")
            self.white_queen_gif = PhotoImage(file=icon_folder+"white_queen.gif")
            self.white_rook_gif = PhotoImage(file=icon_folder+"white_rook.gif")
            self.white_bishop_gif = PhotoImage(file=icon_folder+"white_bishop.gif")
            self.white_knight_gif = PhotoImage(file=icon_folder+"white_knight.gif")
            self.white_pawn_gif = PhotoImage(file=icon_folder+"white_pawn.gif")

            self.transparent_square_gif = \
            PhotoImage(file=icon_folder+"transparent_square.gif")

            self.status_message.config(text = "Icons loaded from " + \
            "entered image folder.") # success message
        except: # entered folder was no good
            # failure message
            self.status_message.config(text = "Unable to load icons" + \
            "from entered image folder (absent or corrupted).")
            # now try the previous folder. Although this is guaranteed to work
            # because the game auto-exits if it can't find images, we still
            # need to go through everything to make sure that all the pieces
            # are displaying images from a single, intact folder.
            icon_folder = previous_icons + "/"
            self.black_king_gif = PhotoImage(file=icon_folder+"black_king.gif")
            self.black_queen_gif = PhotoImage(file=icon_folder+"black_queen.gif")
            self.black_rook_gif = PhotoImage(file=icon_folder+"black_rook.gif")
            self.black_bishop_gif = PhotoImage(file=icon_folder+"black_bishop.gif")
            self.black_knight_gif = PhotoImage(file=icon_folder+"black_knight.gif")
            self.black_pawn_gif = PhotoImage(file=icon_folder+"black_pawn.gif")

            self.white_king_gif = PhotoImage(file=icon_folder+"white_king.gif")
            self.white_queen_gif = PhotoImage(file=icon_folder+"white_queen.gif")
            self.white_rook_gif = PhotoImage(file=icon_folder+"white_rook.gif")
            self.white_bishop_gif = PhotoImage(file=icon_folder+"white_bishop.gif")
            self.white_knight_gif = PhotoImage(file=icon_folder+"white_knight.gif")
            self.white_pawn_gif = PhotoImage(file=icon_folder+"white_pawn.gif")

            self.transparent_square_gif = \
            PhotoImage(file=icon_folder+"transparent_square.gif")

        # put the loaded images into the piece_pics set
        self.piece_pics = {"black_king":self.black_king_gif,
        "black_queen":self.black_queen_gif, "black_rook":self.black_rook_gif,
        "black_bishop":self.black_bishop_gif, \
        "black_knight":self.black_knight_gif,
        "black_pawn":self.black_pawn_gif, "white_king":self.white_king_gif,
        "white_queen":self.white_queen_gif, "white_rook":self.white_rook_gif,
        "white_bishop":self.white_bishop_gif, \
        "white_knight":self.white_knight_gif,
        "white_pawn":self.white_pawn_gif,
        "transparent_square":self.transparent_square_gif}

        self.icon_folder = icon_folder # save this as the current icon folder
        self.refresh_images() # refresh the piece images

    def audio_failed(self):
        """
        Display the audio failure status message. It's in a separate method
        so that it can be accessed with the after() method, overwriting the
        welcome message.
        """
        # a status message about the failure to load audio
        self.status_message.config(text = "Audio load failed. Either " + \
        "pygame is not installed, or sound folder is corrupted.")

    def images_failed(self):
        """
        If images couldn't be loaded on init, this method gets called after
        a 30-second delay, exiting the program.
        """
        self.parent.destroy() # destroys the tkinter window, exiting the game

def main():
    root = Tk() # Create a Tk object from tkinter.
    chess = Chess(root) # Make my game inherit from that object.
    root.mainloop() # Run the main loop.
    mixer.music.stop()

if __name__ == '__main__':
    main()
