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

try:
    from tkinter import *
except:
    print("The tkinter module is not installed. Please install it and try again.")
try:
    from tkinter import filedialog
except:
    print("The tkinter/filedialog module is not installed. Please install it and try again.")
try:
    from tkinter import messagebox
except:
    print("The tkinter/messagebox module is not installed. Please install it and try again.")
try:
    from tkinter import colorchooser
except:
    print("The tkinter/colorchooser module is not installed. Please install it and try again.")
try:
    from pygame import mixer
except:
    print("The pygame/mixer module is not installed. Please install it and try again.")
try:
    from PIL import Image, ImageTk
except:
    print("The Pillow module is not installed. Please install it and try again.")
from random import *
import sys
import time
import os

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
        range8 = range(8) # generate a range(8) object and save it
        
        # look one space ahead
        loc = self.location[0] + str(int(self.location[1])+self.direction)
        if len(loc) == 2: # if there's no '-' sign in the location
            # and it's on the board
            if int(loc[0]) in range8 and int(loc[1]) in range8:
                if Chess.all_squares.get(loc).piece is None: # and empty
                    self.moveset.add(loc) # add it
        # look another space ahead and do the same thing
        loc = loc[0]+str(int(loc[1])+self.direction)
        if len(loc) == 2:
            if int(loc[0]) in range8 and int(loc[1]) in range8:
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
            if int(loc[0]) in range8 and int(loc[1]) in range8:
                # if there's a piece
                if Chess.all_squares.get(loc).piece is not None:
                    # and it's an enemy
                    if Chess.all_squares.get(loc).piece.color is not self.color:
                        self.moveset.add(loc) # it's a valid move
                elif int(loc[0]) in range8 and \
                int(loc[1])-self.direction in range8: # no piece there
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
            if int(loc[0]) in range8 and int(loc[1]) in range8:
                # and there's a piece there
                if Chess.all_squares.get(loc).piece is not None:
                    # and the piece is an enemy
                    if Chess.all_squares.get(loc).piece.color is not self.color:
                        self.moveset.add(loc) # add the location
                elif int(loc[0]) in range8 and \
                int(loc[1])-self.direction in range8: # no piece there
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
        parent (Tk): the root Tk object
        argvs (dictionary): a dictionary of switch:argument from the command
            line. Switches are of the form "*light" and arguments are of the
            form "blue".
        all_squares (dictionary): a class variable (not member variable) of
            the Chess class. The keys are two-character strings describing
            the location of an object on the board, and the values are Squares
            on the board.
        frame (Frame): a tkinter Frame that holds the visible game
        menubar (Menu): the complete menu bar
        filemenu (Menu): the "file" menu cascade
        settingsmenu (Menu): the "settings" menu cascade
        uimenu (Menu): the "ui" menu cascade under settings
        opponentmenu (Menu): the "opponent" menu cascade under settings
        audiomenu (Menu): the "audio" menu cascade under settings
        boardmenu (Menu): the "board" menu cascade
        navmenu (Menu): the "navigation" menu cascade
        castlemenu (Menu): the "castling" menu cascade
        helpmenu (Menu): the "help" menu cascade
        mode (string): "easy" for easy AI play, "hard" for hard AI play, and
            "human" for 2P matches
        status_message (Label): a tkinter Label that displays the appropriate
            message when a player wins
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
        replaying (boolean): True if the game is in the middle of replaying a move
        light_square_color (string): a string like "blue" or "#0000ff", for color
        dark_square_color (string): a string like "blue" or "#0000ff", for color
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
        sound_folder (string): Folder containing the sound files.
        icon_folder (string): Folder containing the icon files.
        audio (boolean): True if the user wants sound effects, False otherwise.
        movelist (list): a list of moves, in the form of "0077" for moving from
            top left corner to bottom right corner, or "wl" for white
            castling queenside
        savename (string): the current filename for the active game. Is blank
            after starting a new game.
        replaycounter (int): an int that tells us what move we're on, to keep track
            of where we are within the movelist
        screen_size (int): the width and height of the canvas, in pixels
        unsaved_changes (boolean): True if there are new moves in the movelist in
            memory that have not yet been saved to disk
    """
    def __init__(self, parent):
    
        parent.protocol("WM_DELETE_WINDOW", self.quit) # redirects the OS's 'x' close button to self.quit()
        parent.title("Chess") # title for the window
        try: # try to load an img for the window's icon (top left corner of title bar)
            parent.tk.call('wm', 'iconphoto', parent._w, ImageTk.PhotoImage(Image.open("ico.png")))
        except: # if it fails
            pass # leave the user alone
        self.parent = parent
        
        # look for argv options and rejoin into a string, then lowercase,
        # then split along ' *', then discard the first item
        # for each string in that, the chars to the left of the FIRST space are a dictionary key,
        # those to the right are the value - using partition() instead of split() allows
        # arguments with spaces, which filenames sometimes include
        self.argvs = {pair.partition(' ')[0]:pair.partition(' ')[2]
        for pair in (' '.join(sys.argv)).lower().split(' *')[1:]}
        # switches and commands:
        # *iconfolder folder
        # *audiofolder folder
        # *audio on off
        # *blackui click drag
        # *whiteui click drag
        # *opponent easy hard human
        # *size int
        # *light color
        # *dark color
        # *savefile file
        
        # Here's the frame:
        self.frame = Frame(parent)
        self.frame.pack()
                
        self.screen_size = 400

        self.audio = True
        tempaudio = self.argvs.get('audio') # look for an audio argv
        if tempaudio: # if it exists
            if tempaudio == "off": # and it says off
                self.audio = False # turn off audio
                
        self.last_source = self.chosen_piece = True # these can safely be checked and approved with an 'if'
        
        # Menu bar!
        self.menubar = Menu(parent)
        
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="New", command=self.new_game, underline=0, accelerator="Ctrl+N")
        self.filemenu.add_command(label="Save", command=self.save_plain, underline=0, accelerator="Ctrl+S")
        self.filemenu.add_command(label="Save As...", command=self.save_as, underline=0, accelerator="Ctrl+Shift+S")
        self.filemenu.add_command(label="Open...", command=self.load, underline=0, accelerator="Ctrl+O")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit", command=self.quit, underline=0, accelerator="Ctrl+Q")
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        
        self.settingsmenu = Menu(self.menubar, tearoff=0)
        self.uimenu = Menu(self.settingsmenu, tearoff=0)
        self.uimenu.add_command(label="Black", command=self.black_ui_toggle, underline=0)
        self.uimenu.add_command(label="White", command=self.white_ui_toggle, underline=0)
        self.opponentmenu = Menu(self.settingsmenu, tearoff=0)
        # lambda functions! all these do is define an inline function that calls self.set_opponent with a parameter
        self.opponentmenu.add_command(label="Easy AI", command=(lambda: self.set_opponent("easy")), state=DISABLED)
        self.opponentmenu.add_command(label="Hard AI", command=(lambda: self.set_opponent("hard")))
        self.opponentmenu.add_command(label="Human", command=(lambda: self.set_opponent("human")))
        self.audiomenu = Menu(self.settingsmenu, tearoff=0)
        self.audiomenu.add_command(label="On/off", command=self.audio_toggle, underline=0, accelerator="Ctrl+A")
        self.audiomenu.add_command(label="SFX folder...", command=self.audio_from_folder, underline=0, accelerator="Ctrl+U")
        self.boardmenu = Menu(self.settingsmenu, tearoff=0)
        self.boardmenu.add_command(label="Icons...", command=self.icons_from_folder, underline=0, accelerator="Ctrl+I")
        self.boardmenu.add_command(label="Size...", command=self.choose_board_size)
        self.boardmenu.add_command(label="Light squares...", command=(lambda: self.set_square_color('light')))
        self.boardmenu.add_command(label="Dark squares...", command=(lambda: self.set_square_color('dark')))
        self.boardmenu.add_command(label="Refresh", command=(lambda: self.set_board_size(Label(), self.screen_size)), underline=0, accelerator="F5")
        self.settingsmenu.add_cascade(label="UI", menu=self.uimenu)
        self.settingsmenu.add_cascade(label="Opponent", menu=self.opponentmenu)
        self.settingsmenu.add_cascade(label="Audio", menu=self.audiomenu)
        self.settingsmenu.add_cascade(label="Board", menu=self.boardmenu)
        self.menubar.add_cascade(label="Settings", menu=self.settingsmenu)
        
        self.navmenu = Menu(self.menubar, tearoff=0)
        self.navmenu.add_command(label="Step back (undo)", command=self.step_back, underline=0, accelerator="Ctrl+←")
        self.navmenu.add_command(label="Step forward (redo)", command=self.step_forward, underline=0, accelerator="Ctrl+→")
        self.navmenu.add_command(label="Beginning of match", command=self.step_start, underline=0, accelerator="Ctrl+↑")
        self.navmenu.add_command(label="End of match", command=self.step_end, underline=0, accelerator="Ctrl+↓")
        self.menubar.add_cascade(label="Navigation", menu=self.navmenu)
                
        self.castlemenu = Menu(self.menubar, tearoff=0)
        self.castlemenu.add_command(label="Black queenside", command=self.castle_black_left, underline=0)
        self.castlemenu.add_command(label="Black kingside", command=self.castle_black_right, underline=0)
        self.castlemenu.add_separator()
        self.castlemenu.add_command(label="White queenside", command=self.castle_white_left, underline=0)
        self.castlemenu.add_command(label="White kingside", command=self.castle_white_right, underline=0)
        self.menubar.add_cascade(label="Castle", menu=self.castlemenu)
        
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="View help", command=self.help, underline=0, accelerator="F1")
        self.helpmenu.add_command(label="About", command=self.about, underline=0)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        
        parent.config(menu=self.menubar)
        
        # The game starts on easy mode without making the player press a button.
        self.mode = "easy"
        tempopponent = self.argvs.get('opponent') # look for the opponent switch
        if tempopponent: # if the value wasn't None,
            self.set_opponent(tempopponent) # set the opponent

        # Status message. When the game ends, the result is described here.
        self.status_message = Label(self.frame, text = "Welcome to Chess!")
        self.status_message.grid(row=1, column = 0)
        
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
        self.sound_filenames = ("ui_toggle.ogg", "audio_on.ogg", "select_piece.ogg",
        "move_piece.ogg", "computer_move.ogg", "castle.ogg", "undo.ogg",
        "torpedo.ogg", "explosion.ogg", "game_start.ogg")
        try: # here, we're going to try enabling audio with pygame
            mixer.init(buffer=512) # initialize the mixer
            try: # first we'll look into the command line
                self.sound_folder = self.argvs.get('audiofolder') # try to get the folder from argvs
                # so now we check to make sure every single audio file is
                # present and can be loaded. it's either this or using
                # try/except every time a sound is played.
                for file in self.sound_filenames:
                    mixer.music.load(os.path.join(self.sound_folder, file))
            except: # well, something failed in the command line attempt. either
            # there was no command line argv given there, or the folder was
            # missing, or one of the files was missing. so now we try the
            # default sound folder, checking it for every needed file.
                self.sound_folder = "sfx"
                for file in self.sound_filenames:
                    mixer.music.load(os.path.join(self.sound_folder, file))
            # if we've gotten this far, then an audio load was successful
            self.parent.bind("<Control-a>", self.audio_toggle) # bind buttons
            self.parent.bind("<Control-A>", self.audio_toggle)
            self.audiomenu.entryconfig(0, state=NORMAL)
        except: # couldn't load audio for some reason. either pygame isn't
        # installed on the user's machine, or it couldn't find an audio folder.
            self.audio = False # we'll disable audio
            self.audiomenu.entryconfig(0, state=DISABLED)
            # and we'll give the user a message telling them what happened
            self.parent.after(0, self.audio_failed)

        # now we'll load the piece icons
        try:
            try:
                self.load_icons(self.argvs.get('iconfolder'))
            except:
                self.load_icons("piece_icons")
        except:
            self.castlemenu.entryconfig(0, state=DISABLED)
            self.castlemenu.entryconfig(1, state=DISABLED)
            self.castlemenu.entryconfig(3, state=DISABLED)
            self.castlemenu.entryconfig(4, state=DISABLED)
            messagebox.showerror(title="Error", message=''.join(("Couldn't find images. Provide a command-line argument ",
            "or default directory ('piece_icons' under the current directory) with valid images. Click OK ",
            "to exit the program.")))
            self.parent.after(1, self.parent.destroy)
            return
        # this organizes the piece icons into an easily-accessed dictionary.
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
        
        self.unsaved_changes = False # they just started the app, so there are no unsaved changes
        self.replaying = False # indicate that we're not currently replaying - important for castle functions
        self.light_square_color = 'white'
        self.dark_square_color = 'gray35'
        
        # Draws the board, which involves reinitialization of match-specific
        # variables.
        self.new_game()
        
        # go through the blackui, whiteui, light, and dark switches
        for argument in ['blackui', 'whiteui', 'light', 'dark']:
            temp = self.argvs.get(argument) # assign that switch's value to a local var
            if temp: # if it wasn't None,
                if argument == 'blackui' and temp == 'drag': # if it was blackui and drag,
                    self.black_ui_toggle() # switch black ui
                elif argument == 'whiteui' and temp == 'drag': #  if it was whiteui and drag,
                    self.white_ui_toggle() # switch white ui
                else: # the only other items in the list are 'light' and 'dark', so...
                    self.set_square_color(argument, temp) # set those squares to that color
        
        tempboard = self.argvs.get('size') # look for the size switch
        if tempboard: # if the value wasn't None,
            try:
                tempboard = int(tempboard) # turn it into an int
                tempsuppressaudio = self.audio
                if tempsuppressaudio:
                    self.audio = False
                parent.after(1, lambda: self.set_board_size(Label(), tempboard)) # pass it in, with a dummy widget to destroy
                if tempsuppressaudio:
                    self.audio = True
                    
            except:
                pass # or not -_-
        
        tempfile = self.argvs.get('savefile') # look for the savefile switch
        if tempfile: # if the value wasn't None,
            self.load('init', tempfile) # tell load that it was an 'init' load and pass it the filename
            self.step_end() # and go to the most recent step of the replay

    def draw_board(self, *args):
        """
        Creates the game, wiping any previous conditions.
        Parameter:
            *args: maybe it was called with a keyboard shortcut
        """
        # This generates the board. Rectangles are saved to a 2D array.
        self.board = Canvas(self.frame, width=self.screen_size, height = self.screen_size)
        self.last_source = None
        
        range8 = range(8) # make a range(8) object and save it
        
        self.squares = [] # this is a 2D list of black/white squares
        for row in range8:
            self.squares.append([])
            for column in range8:
                if (row+column)%2 == 0:
                    color = self.light_square_color
                else:
                    color = self.dark_square_color
                try: # this might not work if the user gave an invalid color in a command line arg
                    self.squares[row].append(self.board.create_rectangle(row*(self.screen_size//8),
                        column*(self.screen_size//8),row*(self.screen_size//8)+(self.screen_size//8),
                        column*(self.screen_size//8)+(self.screen_size//8), fill = color))
                except: # if the color was invalid,
                    if color == self.light_square_color: # if it was light
                        color = self.light_square_color = 'white' # replace invalid light with white
                    else: # if it was dark
                        color = self.dark_square_color = 'gray35' # replace invalid dark with gray35
                    self.squares[row].append(self.board.create_rectangle(row*(self.screen_size//8),
                        column*(self.screen_size//8),row*(self.screen_size//8)+(self.screen_size//8),
                        column*(self.screen_size//8)+(self.screen_size//8), fill = color))

        self.board.grid(row=0, column=0)

        # Make a dictionary of location:Square.
        Chess.all_squares = {str(row)+str(column):Square(str(row)+str(column))
            for row in range8 for column in range8}

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
        self.extra_black_queens = [Queen("black", "88") for i in range8]

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
        self.extra_white_queens = [Queen("white", "88") for i in range8]

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

        for i in range8:
            self.all_pieces.append(self.extra_black_queens[i])

        self.all_pieces += [self.white_pawn_1, self.white_pawn_2,
        self.white_pawn_3, self.white_pawn_4, self.white_pawn_5,
        self.white_pawn_6, self.white_pawn_7, self.white_pawn_8,
        self.white_rook_1, self.white_knight_1, self.white_bishop_1,
        self.white_queen, self.white_king, self.white_bishop_2,
        self.white_knight_2, self.white_rook_2]

        for i in range8:
            self.all_pieces.append(self.extra_white_queens[i])

        self.square_overlay = [] # a list of all the piece icons or transparent
        # images that can rest on any given square
        for row in range8:
            self.square_overlay.append([])
            for column in range8:
                self.square_overlay[row].append \
                (self.board.create_image(row*(self.screen_size//8),column*(self.screen_size//8),
                anchor=NW,image=None))

        # this is the image that can float around the board, used when a player
        # is using the click-and-drag interface
        self.dragged_piece = self.board.create_image((self.screen_size//8),(self.screen_size//8), image=self.piece_pics.get("transparent_square"))

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
        self.parent.bind("<Control-s>", self.save_plain) # differs from uppercase version
        self.parent.bind("<Control-u>", self.audio_from_folder)
        self.parent.bind("<Control-i>", self.icons_from_folder)
        self.parent.bind("<Control-q>", self.quit)
        self.parent.bind("<Control-o>", self.load)
        self.parent.bind("<Control-n>", self.new_game)
        self.parent.bind("<Control-S>", self.save_as) # differs from lowercase version
        self.parent.bind("<Control-U>", self.audio_from_folder)
        self.parent.bind("<Control-I>", self.icons_from_folder)
        self.parent.bind("<Control-Q>", self.quit)
        self.parent.bind("<Control-O>", self.load)
        self.parent.bind("<Control-N>", self.new_game)
        
        self.parent.bind("<F1>", self.help)
        self.parent.bind("<Control-Left>", self.step_back)
        self.parent.bind("<Control-Up>", self.step_start)
        self.parent.bind("<Control-Right>", self.step_forward)
        self.parent.bind("<Control-Down>", self.step_end)
        self.parent.bind("<F5>", lambda x: self.set_board_size(Label(), self.screen_size))
        
        if self.audio: # if audio is on
            mixer.music.load(os.path.join(self.sound_folder, "game_start.ogg"))
            mixer.music.play() # play 'game_start'
            
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
    
    def choose_board_size(self):
        """
        This method will change the size of the board, then redraw the icons to fit.
        The user will choose the board size with a slider (Scale widget).
        """
        sizewindow = Toplevel()
        sizewindow.title("Board size")
        try: # try to load an img for the window's icon (top left corner of title bar)
            sizewindow.tk.call('wm', 'iconphoto', sizewindow._w, ImageTk.PhotoImage(Image.open("ico.png")))
        except: # if it fails
            pass # leave the user alone
            
        for width in range(200, 1000, 100): # inspect a series of widths
            if width < (0.35 * self.parent.winfo_screenwidth()): # to find a window size about a third of their screen
                use = width # use the biggest appropriate size
        sizewindow.geometry(str(use) +"x145") # define a window size
        # create a Scale widget
        sizescale = Scale(sizewindow, from_=200, to=2200, orient=HORIZONTAL, length=(use-6), resolution=40, tickinterval=200)
        sizescale.set(self.screen_size) # set it to the current game board size
        sizescale.grid(row=0, column=0, columnspan=5) # and grid it
        
        for res in range(200, 2001, 40): # inspect a series of resolutions
            # to find a game board size that's appropriate for the user's monitor
            if res < (0.8 * min(self.parent.winfo_screenwidth(), self.parent.winfo_screenheight())):
                use = str(res) # use the biggest appropriate size
        
        recommendation = Label(sizewindow, text="Recommended setting: " + use) # tell the user the recommendation
        recommendation.grid(row=1, column=0, columnspan=5) # grid the resolution
        # an 'ok' button that, on click, sends the current window and the chosen size to set_board_size()
        ok = Button(sizewindow, text="\nOK\n", width=15, height=3, command=lambda: self.set_board_size(sizewindow, sizescale.get()))
        ok.grid(row=2, column=1) # grid the ok button
        cancel = Button(sizewindow, text="\nCancel\n", width=15, height=3, command=sizewindow.destroy) # cancel button
        cancel.grid(row=2, column=3) # grid the cancel button
    
    def set_board_size(self, topwindow, size):
        """
        Sets the board size with the specified value.
        Parameters:
            topwindow (widget): a widget that this method will destroy
            size (int): the new size of the board
        """
        if size not in range(200, 2001): # if the user provided an invalid screen size, via argv
            return # don't use it
        self.screen_size = size # save the new size
        
        self.parent.geometry("".join((str(size+4),"x",str(size+25)))) # set the window size to match the board
        if len(self.movelist) == 0 or self.replaycounter ==0: # if the movelist is empty or we're at the start
            try:
                self.board.destroy() # destroy it if it's there
            except:
                pass # if not, fine
            self.draw_board() # and redraw it
        else: # if there are moves to do,
            self.replaycounter +=1 # advance the replay counter by 1
            tempsuppressaudio = self.audio # note if we have to suppress audio
            if tempsuppressaudio: # if we do,
                self.audio = False # suppress it
            self.step_back() # and go 'back' to there, which puts us at the same place
            if tempsuppressaudio: # if we did,
                self.audio = True # turn it back on
        
        self.load_icons(self.icon_folder) # reload the icons for the new size
        self.refresh_images() # and refresh them
        
        topwindow.destroy() # destroy the dialog box where we chose this

    def load_icons(self, directory):
        """
        This loads piece icons from a given directory.
        Parameter:
            directory (string): a string with the directory path
        """
        files = os.listdir(directory) # get a listing of the files in this directory
        for file in files: # look through the files
            file = file.lower() # make the file all lowercase
            # when a file is found, join the directory with a slash with the name, open as an image, resize it, and make it a PhotoImage for tkinter
            if "black" in file: # if a file says black
                if "king" in file: # and king, it's the black king
                    self.black_king_gif = ImageTk.PhotoImage(Image.open(os.path.join(directory, file)).resize(((self.screen_size//8),(self.screen_size//8))))
                elif "queen" in file: # and queen, it's the black queen
                    self.black_queen_gif = ImageTk.PhotoImage(Image.open(os.path.join(directory, file)).resize(((self.screen_size//8),(self.screen_size//8))))
                elif "rook" in file: # and rook, it's the black rook
                    self.black_rook_gif = ImageTk.PhotoImage(Image.open(os.path.join(directory, file)).resize(((self.screen_size//8),(self.screen_size//8))))
                elif "bishop" in file: # and bishop, it's the black bishop
                    self.black_bishop_gif = ImageTk.PhotoImage(Image.open(os.path.join(directory, file)).resize(((self.screen_size//8),(self.screen_size//8))))
                elif "knight" in file: # and knight, it's the black knight
                    self.black_knight_gif = ImageTk.PhotoImage(Image.open(os.path.join(directory, file)).resize(((self.screen_size//8),(self.screen_size//8))))
                elif "pawn" in file: # and pawn, it's the black pawn
                    self.black_pawn_gif = ImageTk.PhotoImage(Image.open(os.path.join(directory, file)).resize(((self.screen_size//8),(self.screen_size//8))))
            elif "white" in file: # if a file says white
                if "king" in file: # and king, it's the white king
                    self.white_king_gif = ImageTk.PhotoImage(Image.open(os.path.join(directory, file)).resize(((self.screen_size//8),(self.screen_size//8))))
                elif "queen" in file: # and queen, it's the white queen
                    self.white_queen_gif = ImageTk.PhotoImage(Image.open(os.path.join(directory, file)).resize(((self.screen_size//8),(self.screen_size//8))))
                elif "rook" in file: # and rook, it's the white rook
                    self.white_rook_gif = ImageTk.PhotoImage(Image.open(os.path.join(directory, file)).resize(((self.screen_size//8),(self.screen_size//8))))
                elif "bishop" in file: # and bishop, it's the white bishop
                    self.white_bishop_gif = ImageTk.PhotoImage(Image.open(os.path.join(directory, file)).resize(((self.screen_size//8),(self.screen_size//8))))
                elif "knight" in file: # and knight, it's the white knight
                    self.white_knight_gif = ImageTk.PhotoImage(Image.open(os.path.join(directory, file)).resize(((self.screen_size//8),(self.screen_size//8))))
                elif "pawn" in file: # and pawn, it's the white pawn
                    self.white_pawn_gif = ImageTk.PhotoImage(Image.open(os.path.join(directory, file)).resize(((self.screen_size//8),(self.screen_size//8))))
            elif "transparent" in file: # if the file says transparent, it's the transparent square
                self.transparent_square_gif = ImageTk.PhotoImage(Image.open(os.path.join(directory, file)).resize(((self.screen_size//8),(self.screen_size//8))))
        
        # save the icon folder, as we may need to revert to it later
        self.icon_folder = directory
        
        # this organizes the piece icons into an easily-accessed dictionary.
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
    
    def set_opponent(self, opponent):
        """
        Sets the opponent mode to 'easy', 'hard', or 'human', then pops an info box.
        Parameter:
            opponent (string): the mode to be changed to
        """
        self.mode = opponent # set the mode to the given opponent
        for i in range(3): # go through 0 to 3
            self.opponentmenu.entryconfig(i, state=NORMAL) # make those opponentmenu ids NORMAL
        if opponent == "easy": # if easy was selected
            self.opponentmenu.entryconfig(0, state=DISABLED) # disable
        elif opponent == "hard": # if hard was selected
            self.opponentmenu.entryconfig(1, state=DISABLED) # disable
        else: # otherwise
            self.opponentmenu.entryconfig(2, state=DISABLED) # disable human
        messagebox.showinfo(title="Opponent changed", message="Opponent mode changed to " + opponent + ".") # and note such
    
    def new_game(self, *args):
        """
        Starts a new game, reinitializing the save name, move list, and replay counter.
        Paramter:
            *args: may or may not include an event
        """
        # if there are unsaved changes and user confirms, save (will ask for filename if necessary)
        if self.unsaved_changes:
            temp = messagebox.askyesnocancel(title="Unsaved changes", \
            message="There are unsaved changes to your game. Save now?")
            if temp == None: # if they cancel
                return # then return
            if temp: # if they didn't cancel
                if not self.save_plain(): # but then they canceled the save itself
                    return # that's a return
        
        try:
            self.board.destroy() # destroy it if it's there
        except:
            pass # if not, fine
        self.draw_board() # then make a new one
        
        self.savename = "" # a save name will need to be chosen
        self.movelist = [] # a fresh movelist
        self.replaycounter = 0 # start from the beginning of a new match
        self.unsaved_changes = False

        # Set a status message.
        self.status_message.config(text = "Welcome to Chess!")
        
    def step_back(self, *args):
        """
        Move back one step in a replay. Nothing ever actually moves backwards - it works
        by going to the beginning and stepping forward all the way until one move prior to
        where it was.
        Paramter:
            *args: may or may not include an event
        """
        # if there are no loaded moves, or we're already at the the very beginning
        if len(self.movelist) == 0 or self.replaycounter == 0:
            return # return and do nothing
        count = self.replaycounter - 1 # decrement the replay counter by 1
        self.step_start() # go to the beginning
        for i in range(count): # go forward that number of times
            self.step_forward(wait=True)
        if self.audio: # if audio is on
            mixer.music.load(os.path.join(self.sound_folder, "undo.ogg"))
            mixer.music.play() # play the 'undo' sound
        self.check_castles()
        self.refresh_highlighting()
        self.refresh_images()
        
    def step_forward(self, *args, **kwargs):
        """
        Move forward one step in a replay.
        Parameter:
            *args: may or may not include an event
        """
        # if the movelist is empty or we're at the end of the replay (counter
        # for next move matches length of list)
        if len(self.movelist) == 0 or len(self.movelist) == self.replaycounter:
            return # don't do anything
        
        if self.audio: # if audio is on,
            self.audio = allow = False # turn it off and remember
        else: # otherwise,
            allow = True # set a permissive flag
        
        do_move = self.movelist[self.replaycounter] # save the next string in the movelist
        self.replaying = True # tell the castle functions we're replaying, not really playing
        if do_move == "bl": # if it's 'bl',
            self.castle_black_left() # castle black left
        elif do_move == "br": # if it's 'br',
            self.castle_black_right() # castle black right
        elif do_move == "wl": # if it's 'wl',
            self.castle_white_left() # castle white left
        elif do_move == "wr": # if it's 'wr',
            self.castle_white_right() # castle white right
        else: # if it's not a castle, it's a regular move
            self.move(Chess.all_squares.get(do_move[0:2]).piece, do_move[2:]) # do the move
        self.replaying = False # ready to play for real again
        
        self.replaycounter += 1 # increase the counter for the next move
        if not allow: # if audio was suppressed,
            self.audio = True # turn it back on
        if not kwargs.get('wait'): # if we weren't told to wait til the end,
            self.check_castles() # check castles now
            self.refresh_images() # refresh images now
            self.refresh_highlighting() # refresh highlighting now
        
    def step_start(self, *args):
        """
        Goes to the beginning of a replay.
        Parameter:
            *args: may or may not include an event
        """
        try:
            self.board.destroy() # destroy the board if it's there
        except:
            pass # if not, fine
        self.draw_board() # redraw it
        self.replaycounter = 0 # start from the beginning of a replay
    
    def step_end(self, *args):
        """
        Goes to the end of a replay.
        Parameter:
            *args: may or may not include an event
        """
        if len(self.movelist) == 0: # if the movelist is empty
            return # do nothing
        while len(self.movelist) > self.replaycounter: # while we're not at the end of the movelist
            self.step_forward(wait=True) # step forward
        self.check_castles()
        self.refresh_highlighting()
        self.refresh_images()
        
    def help(self, *args):
        """
        Launches the Help content.
        Parameter:
            *args: may or may not include an event
        """
        helpfile = os.path.join(os.getcwd(),os.path.join("Chess Help", "Chess.html"))
        try:
            os.startfile(helpfile)
        except:
            messagebox.showerror(title='Help file not found',
            message=''.join(("The help file wasn't accessible. Please make sure that ",
            helpfile, " exists and that you have read permission for it.")))
        
    def about(self):
        """
        Launches a little window with the version number and my name.
        """
        about = Toplevel() # make a new window
        about.title("About") # title it
        about.geometry("200x150") # size it
        spacer = Label(about, text="\t ") # make a spacer to move the content to the right by a bit
        spacer.grid(row=0, column=0, rowspan=2) # put the spacer at the top
        msg = Label(about, text="\n\n\nChess version 9\nBy David Muller\n\n") # make a message
        msg.grid(row=0, column=1) # grid it
        close = Button(about, text="Close Window", command=about.destroy) # make a button
        close.grid(row=1, column=1) # grid it
    
    def save_plain(self, *args):
        """
        A plain save function. If there's no preexisting file name,
        uses save_as() instead.
        Parameter:
            *args: may include an event
        """
        if self.savename: # if there's a name
            self.save(self.savename) # then use it
        elif self.save_as(): # else, use save_as instead
            return True # successful save returns True
        return False # else, return False
        
    def save_as(self, *args):
        """
        A save as function, which asks for a name and only retains it if it was given
        (canceling makes empty string, which isn't saved).
        Parameter:
            *args: may include an event
        """
        temp = filedialog.asksaveasfilename(defaultextension=".txt", \
        filetypes=(('Text files', '.txt'),('All files', '.*'))) # ask for a name
        if temp: # if we got one,
            self.savename = temp # retain it
            self.save(temp) # and pass it to save()
            return True
        return False
    
    def save(self, filename):
        """
        Does the actual saving business of writing a file with the given name.
        Parameter:
            filename (string): the name of the file to write
        """
        try: # write the movelist to a file with the specified name
            with open(filename, 'w', encoding = 'utf-8-sig') as output:
                for item in self.movelist:
                    output.write(item + "\n")
            self.unsaved_changes = False # they just saved, so there are no unsaved changes
        except: # if that doesn't work for some reason, say so
            messagebox.showerror(title="Error", \
            message="Error saving file. Ensure that there is room and you have write permission.")
            
    def load(self, *args):
        """
        Loads a game from a file on the computer.
        Parameter:
            *args: may be nothing, 'init' and a filename, or an event
        """
        # if there are unsaved changes and the user wants to save,
        if self.unsaved_changes:
            temp = messagebox.askyesnocancel(title="Unsaved changes", \
            message="There are unsaved changes to your game. Save now?")
            if temp == None:
                return
            if temp:
                if not self.save_plain(): # if the user chose yes but then canceled the save
                    return # just return
                # give them a save_plain(). this is how all programs work: if user wants a
                # separate file, they have to use save_as(). if i used save_as() for this,
                # user would get confused when asked to overwrite the file they were using.
        
        try:
            args # first, see if there are any args
            filename = args[1] # then see if there are two, and if so, grab the second one
        except: # if a filename wasn't given,
            filename = filedialog.askopenfilename(defaultextension=".txt", \
            filetypes=(('Text files', '.txt'),('All files', '.*'))) # ask for a name
            if not filename: # if they hit cancel, returning an empty string
                return # just return
                
        try:
            self.board.destroy() # destroy it if it's there
        except:
            pass # if not, fine
        self.draw_board() # basically, start a new game
        # and load the specified save file into a movelist
        try: # open the specified file and write the contents to the list
            movelist = [] # create a blank movelist
            with open(filename, 'r', encoding = 'utf-8-sig') as file:
                for line in file:
                    movelist.append(line[:-1])
                # the text file appears to end with a blank line, but that's really just the
                # \n of the previous line, so there's no extraneous empty item at the end of the list.
            self.movelist = movelist # replace the existing movelist with the loaded one
            self.replaycounter = 0 # start from the beginning of a new match
            self.unsaved_changes = False
            if messagebox.askyesno(title="Load successful", message="Game loaded. Go to the most recent move?"):
                self.step_end()
        except: # if that doesn't work for some reason, say so
            messagebox.showerror(title="Error", \
            message="Error opening file. Ensure that there is room and you have write permission.")
        
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
            self.castlemenu.entryconfig(0, state=NORMAL)
        else:
            self.castlemenu.entryconfig(0, state=DISABLED)
        if(not self.black_rook_2.moved and not self.black_king.moved and
        self.black_king.location != "88" and \
        self.white_king.location != "88" and
        self.player is self.black_player and
        Chess.all_squares.get("50").piece is None and
        Chess.all_squares.get("60").piece is None):
            self.castlemenu.entryconfig(1, state=NORMAL)
        else:
            self.castlemenu.entryconfig(1, state=DISABLED)
        if(not self.white_rook_1.moved and not self.white_king.moved and
        self.black_king.location != "88" and \
        self.white_king.location != "88" and
        self.player is self.white_player and
        Chess.all_squares.get("17").piece is None and
        Chess.all_squares.get("27").piece is None and
        Chess.all_squares.get("37").piece is None):
            self.castlemenu.entryconfig(3, state=NORMAL)
        else:
            self.castlemenu.entryconfig(3, state=DISABLED)
        if(not self.white_rook_2.moved and not self.white_king.moved and
        self.black_king.location != "88" and \
        self.white_king.location != "88" and
        self.player is self.white_player and
        Chess.all_squares.get("57").piece is None and
        Chess.all_squares.get("67").piece is None):
            self.castlemenu.entryconfig(4, state=NORMAL)
        else:
            self.castlemenu.entryconfig(4, state=DISABLED)

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

        # truncate and write the move in the movelist
        self.movelist = self.movelist[:self.replaycounter]
        self.replaycounter += 1
        self.movelist.append(piece_to_move.location + move)
        self.move(piece_to_move, move) # carry out the move
        self.unsaved_changes = True # note that there are unsaved changes to this game
        self.check_castles() # check castling buttons
        # if audio is on and the AI didn't just win
        if self.audio and self.white_king.location != "88":
            mixer.music.load(os.path.join(self.sound_folder, "computer_move.ogg"))
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
            try: # try to sample that set
                piece_to_move = sample(safe_pieces, 1)[0] # pick another piece
                # and another move
                move = sample(piece_to_move.moveset & safe_moves, 1)[0]
            except: # if there are no safe pieces, it'll just use a living piece
                piece_to_move = sample(living_pieces, 1)[0] # pick a random piece
                move = sample(piece_to_move.moveset, 1)[0] # and a random move

        # make a set of pairs of pieces for comparison
        piece_pairs = ((self.black_knight_1,self.white_knight_1),
        (self.black_knight_2,self.white_knight_2),
        (self.black_bishop_1,self.white_bishop_1),
        (self.black_bishop_2,self.white_bishop_2),
        (self.black_rook_1,self.white_rook_1),
        (self.black_rook_2,self.white_rook_2),
        (self.black_queen,self.white_queen),
        (self.black_king,self.white_king))
        
        for pair in piece_pairs:
            decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
            enemy_moves, pair[0], pair[1])
            if decision[0]: # if there's a capture or escape
                # if there's a capture or the current plan is to escape with a
                # lower-priority piece or the moving piece isn't a knight
                if decision[1] or Chess.all_squares.get(move).piece is None or \
                piece_to_move.type != pair[0].type:
                    piece_to_move = decision[2] # use the returned piece
                    move = decision[3] # and use the returned move
        
        # truncate and write the move in the movelist
        self.movelist = self.movelist[:self.replaycounter]
        self.replaycounter += 1
        # write the move in the movelist
        self.movelist.append(piece_to_move.location + move)
        self.move(piece_to_move, move) # move
        self.unsaved_changes = True # note that there are unsaved changes to this game
        self.check_castles() # check castling buttons
        # if there's audio and the AI didn't just win
        if self.audio and self.white_king.location != "88":
            mixer.music.load(os.path.join(self.sound_folder, "computer_move.ogg"))
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
        click = str(event.x//(self.screen_size//8)) + str(event.y//(self.screen_size//8))
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
        click = str(event.x//(self.screen_size//8)) + str(event.y//(self.screen_size//8))
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
        self.choose_target(str(event.x//(self.screen_size//8)) + str(event.y//(self.screen_size//8)))
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
            mixer.music.load(os.path.join(self.sound_folder, "select_piece.ogg"))
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
                    color = self.light_square_color
                else:
                    color = self.dark_square_color
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
            self.movelist = self.movelist[:self.replaycounter]
            self.replaycounter += 1
            # write the move in the movelist
            self.movelist.append(self.chosen_piece.location + click)
            self.move(self.chosen_piece, click) # move the piece
            self.unsaved_changes = True # note that there are unsaved changes to this game
            # if black hasn't lost
            if self.black_king.location != "88":
                delay = 0
                # if audio is on and white hasn't lost
                if self.audio and self.white_king.location != "88":
                    delay = 1000 # set a 1000ms delay
                    mixer.music.load(os.path.join(self.sound_folder, "move_piece.ogg"))
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
        self.last_source = chosen_piece.location # this piece is the last source
        self.last_target = destination # its destination is the last target
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
            in (-2,2):
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

        #if not self.replaying:
        #    self.check_castles() # check the castle buttons
        Chess.all_squares.get(destination).piece = target_piece \
        = chosen_piece # put chosen piece into target and destination pieces
        # original location is now empty
        Chess.all_squares.get(original_location).piece = None
        # set the chosen piece's location to the destination
        chosen_piece.location = destination
        #if not self.replaying:
        #    self.check_castles()
        #    self.refresh_images() # refresh the images
        if self.player is self.white_player: # if it was white's turn
            self.player = self.black_player # now it's black's
        else: # if it was black's turn
            self.player = self.white_player # now it's white's
        if not self.replaying:
            self.refresh_highlighting()
            self.check_castles()
            self.refresh_images()
        if self.black_king.location != "88" and self.white_king.location \
        != "88": # if the game continues
            if self.player.mode == "click": # if it's click mode
                self.board.bind("<Button-1>", self.click_click) # bind that
            else: # otherwise
                self.board.bind("<Button-1>", self.click_hold) # bind drag

    def refresh_highlighting(self):
        """
        Resets the squares to their original colors, sets the proper message for
        whose turn it is, then highlights the most last move (if applicable).
        """
        for row in range(8): # go by row
            for column in range(8): # and column
                if (row+column)%2 == 0: # and every other square
                    color = self.light_square_color # should be white
                else:
                    color = self.dark_square_color # or black
                # recolor the board
                self.board.itemconfig(self.squares[row][column], fill=color)
        if self.player is self.white_player: # if white to go
            color = "dark" # 'dark' color prefix
            self.status_message.config(text = "White's turn.") # announce white
        else: # if black to go
            color = "" # no color prefix
            self.status_message.config(text = "Black's turn.") # announce black
        if self.last_source != None and self.chosen_piece != None:
            # color the last source with a variety of blue
            self.board.itemconfig(self.squares[int(self.last_source[0])]
                [int(self.last_source[1])], fill=color+"blue")
            # color the last target with a variety of green
            self.board.itemconfig(self.squares[int(self.last_target[0])]
                [int(self.last_target[1])], fill=color+"green")
        
    def game_end(self, winner):
        """
        Handles end-of-game actions, including messages, event unbindings,
        and sound effects.
        Parameters:
            winner (string): "Black" or "White", describing the winner
        """
        self.status_message.config(text = winner + " wins!") # announce the win
        self.board.unbind("<Button-1>") # unbind the mouse
        self.castlemenu.entryconfig(0, state=DISABLED)
        self.castlemenu.entryconfig(1, state=DISABLED)
        self.castlemenu.entryconfig(3, state=DISABLED)
        self.castlemenu.entryconfig(4, state=DISABLED)
        if self.audio: # if audio is on
            mixer.music.load(os.path.join(self.sound_folder, "torpedo.ogg"))
            mixer.music.play() # fire torpedo
            time.sleep(1) # wait 1sec
            mixer.music.play() # fire again
            time.sleep(1) # wait 1sec
            mixer.music.play() # and again
            time.sleep(1) # wait 1sec
            mixer.music.load(os.path.join(self.sound_folder, "explosion.ogg"))
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
        if not self.replaying: # only do these things during actual play - not during replays
            self.movelist = self.movelist[:self.replaycounter]
            # write the move in the movelist
            self.movelist.append("bl")
            self.unsaved_changes = True # note that there are unsaved changes to this game
            self.replaycounter += 1
        self.safe_pawns() # sets the current player's pawns to safe
        # color the board with black and white squares
        for row in range(8):
            for column in range(8):
                if (row+column)%2 == 0:
                    color = self.light_square_color
                else:
                    color = self.dark_square_color
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
            mixer.music.load(os.path.join(self.sound_folder, "castle.ogg"))
            mixer.music.play() # play the 'castle' sound

    def castle_black_right(self):
        """
        Castles at black kingside.
        """
        if not self.replaying: # only do these things during actual play - not during replays
            self.movelist = self.movelist[:self.replaycounter]
            # write the move in the movelist
            self.movelist.append("br")
            self.unsaved_changes = True # note that there are unsaved changes to this game
            self.replaycounter += 1
        self.safe_pawns() # sets the current player's pawns to safe
        # color the board with black and white squares
        for row in range(8):
            for column in range(8):
                if (row+column)%2 == 0:
                    color = self.light_square_color
                else:
                    color = self.dark_square_color
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
            mixer.music.load(os.path.join(self.sound_folder, "castle.ogg"))
            mixer.music.play() # play the 'castle' sound

    def castle_white_left(self):
        """
        Castles at white queenside.
        """
        if not self.replaying:
            self.movelist = self.movelist[:self.replaycounter]
            # write the move in the movelist
            self.movelist.append("wl")
            self.unsaved_changes = True # note that there are unsaved changes to this game
            self.replaycounter += 1
        self.safe_pawns() # sets the current player's pawns to safe
        # color the board with black and white squares
        for row in range(8):
            for column in range(8):
                if (row+column)%2 == 0:
                    color = self.light_square_color
                else:
                    color = self.dark_square_color
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
            mixer.music.load(os.path.join(self.sound_folder, "castle.ogg"))
            mixer.music.play() # and play the 'castle' sound
        else: # if audio is off
            delay = 0 # set a delay of 0
        if not self.replaying: # only do these things during actual play - not during replays
            if self.mode == "easy": # if it's on easy mode
                self.parent.after(delay,self.easy_move) # AI makes an easy move
            if self.mode == "hard": # if it's on hard mode
                self.parent.after(delay,self.hard_move) # AI makes a hard move
        self.status_message.config(text = "White castled kingside! " + \
        "Black's turn.") # announce the event

    def castle_white_right(self):
        """
        Castles at white kingside.
        """
        # truncate and write the move in the movelist
        if not self.replaying: # only do these things during actual play - not during replays
            self.movelist = self.movelist[:self.replaycounter]
            self.unsaved_changes = True
            self.movelist.append("wr")
            self.replaycounter += 1
        
        self.safe_pawns() # sets the current player's pawns to safe
        # color the board with black and white squares
        for row in range(8):
            for column in range(8):
                if (row+column)%2 == 0:
                    color = self.light_square_color
                else:
                    color = self.dark_square_color
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
            mixer.music.load(os.path.join(self.sound_folder, "castle.ogg"))
            mixer.music.play() # and play the 'castle' sound
        else: # if audio is off
            delay = 0 # set a delay of 0
        if not self.replaying: # only do these things during actual play - not during replays
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
            # if it's their turn and the game isn't over
            if self.player is self.black_player and \
            self.black_king.location != "88" and \
            self.white_king.location != "88":
                # bind click_hold() to the mouse button
                self.board.bind("<Button-1>", self.click_hold)
            self.choose_target(None) # in effect, clears the first_click attr

        else: # if the player is in drag mode
            self.black_player.mode = "click" # switch to click mode
            # if it's their turn and the game isn't over
            if self.player is self.black_player and \
            self.black_king.location != "88" and \
            self.white_king.location != "88":
                # bind click_click() to the mouse button
                self.board.bind("<Button-1>", self.click_click)
        
        messagebox.showinfo(title="UI mode changed", message="Black UI mode is now click/" + \
        self.black_player.mode + ".") # alert the user that the UI mode changed
        
        if self.audio: # if audio is on
            mixer.music.load(os.path.join(self.sound_folder, "ui_toggle.ogg"))
            mixer.music.play() # play the 'ui_toggle' sound

    def white_ui_toggle(self):
        """
        Switches between the "click/click" move functionality and the
        "click/drag" move functionality for the white player.
        """
        if self.white_player.mode is "click": # if the player is in click mode
            self.white_player.mode = "drag" # switch to drag mode
            # if it's their turn and the game isn't over
            if self.player is self.white_player and \
            self.black_king.location != "88" and \
            self.white_king.location != "88":
                # bind click_hold() to the mouse button
                self.board.bind("<Button-1>", self.click_hold)
            self.choose_target(None) # in effect, clears the first_click attr

        else: # if the player is in drag mode
            self.white_player.mode = "click" # switch to click mode
            # if it's their turn and the game isn't over
            if self.player is self.white_player and \
            self.black_king.location != "88" and \
            self.white_king.location != "88":
                # bind click_click() to the mouse button
                self.board.bind("<Button-1>", self.click_click)

        messagebox.showinfo(title="UI mode changed", message="White UI mode is now click/" + \
        self.white_player.mode + ".") # alert the user that the UI mode changed
        
        if self.audio: # if audio is on
            mixer.music.load(os.path.join(self.sound_folder, "ui_toggle.ogg"))
            mixer.music.play() # play the 'ui_toggle' sound

    def audio_toggle(self, *args):
        """
        Switches between audio mode and silent mode, with a message.
        Parameter:
            *args: may or may not include an event
        """
        if self.audio: # if audio is on
            self.audio = False # turn it off
            mixer.music.stop() # stop all sounds
            # and announce such
            messagebox.showinfo(title="Audio", message="Audio deactivated.")
        else: # otherwise
            self.audio = True # turn it on
            mixer.music.load(os.path.join(self.sound_folder, "audio_on.ogg"))
            mixer.music.play() # play the 'audio_on' sound
            # and announce such
            messagebox.showinfo(title="Audio", message="Audio activated.")

    def set_square_color(self, *args):
        """
        Sets the color of light or dark squares.
        Parameters:
            *args:
                [0] should be squaretype, 'light' or 'dark'
                [1] may or may not exist, to preselect a color (for argv use)
        """
        squaretype = args[0]
        if len(args) > 1: # if there are multiple arguments
            temp = args[1] # we'll have been passed squaretype and a valid color like 'blue'
        else:
            temp = colorchooser.askcolor()[1] # if not, pop a chooser
        if temp: # if a color was chosen
            if squaretype=="light": # change the light squares'
                self.light_square_color = temp # color
            else: # change the dark squares'
                self.dark_square_color = temp # color
            if len(self.movelist) == 0: # if we're at the beginning of the match
                try:
                    self.board.destroy() # destroy the board if it's there
                except:
                    pass # if not, fine
                self.draw_board() # draw it
            else: # if there are moves,
                self.replaycounter +=1 # increment the replay counter
                self.step_back() # and go 'back' to there
    
    def audio_from_folder(self, *args):
        """
        Attempts to load audio from a specified folder. If that fails, attempts
        to load audio from the previous folder.
        Parameter:
            *args: may or may not include an event
        """
        try:
            # initialize the mixer, since the user might have started the game
            # with a missing default sound folder, intending to choose one
            # at runtime
            mixer.init(buffer=512)
            # save the previous folder, just in case
            previous_sound = self.sound_folder
            try: # let's try the entered folder
                temp = filedialog.askdirectory() # ask for a directory
                if not temp: # if they canceled,
                    return # we're done
                self.sound_folder = temp # get the name
                for file in self.sound_filenames:
                    mixer.music.load(os.path.join(self.sound_folder, file))
                messagebox.showinfo(title="Audio", message="Audio loaded from: " + self.sound_folder) # success message
            except: # entered folder was no good
                messagebox.showerror(title="Audio", message="Unable to load audio " + \
                "from entered sound folder (absent or corrupted).") # failure message
                # now try the previous sound folder. We don't need to try the
                # default folder because either the previous one was fine or
                # the default was attempted already.
                self.sound_folder = previous_sound
                for file in self.sound_filenames:
                    mixer.music.load(os.path.join(self.sound_folder, "ui_toggle.ogg"))
            # success, with some sort of audio. Bind the audio hotkey.
            self.parent.bind("<Control-a>", self.audio_toggle)
            self.parent.bind("<Control-A>", self.audio_toggle)
            self.audiomenu.entryconfig(0, state=NORMAL)
        except: # audio failed
            self.audio = False # turn off audio
            self.audiomenu.entryconfig(0, state=DISABLED)
            # inform the user of what happened
            messagebox.showerror(title="Error", message="Unable to load audio. " + \
                "Either the entered sound folder, previous sound folder, " + \
                "and default sound folder are absent or corrupted, " + \
                "or pygame is not installed.")

    def icons_from_folder(self, *args):
        """
        Attempts to load icons from a specified folder. If that fails, attempts
        to load icons from the previous folder.
        Parameter:
            *args: may or may not include an event
        """
        dir = filedialog.askdirectory()
        if not dir:
            return
        try:
            self.load_icons(dir)
        except:
            self.load_icons(self.icon_folder)
            messagebox.showerror(title="Error", message="Couldn't load from the chosen folder. Make sure all " + \
            "files are present and properly named.")
        self.refresh_images()
        
    def audio_failed(self):
        """
        Display the audio failure status message. It's in a separate method
        so that it can be accessed with the after() method.
        """
        # a status message about the failure to load audio
        messagebox.showerror(title="Error", message="Audio load failed. Either " + \
        "pygame is not installed, or sound folder is corrupted.")

    def quit(self, *args):
        """
        A quit function with a yesno prompt or yesnocancel prompt for unsaved changes.
        Parameter:
            *args: allows this to be called with or without an event
        """
        try:
            self.unsaved_changes # look at unsaved changes
        except: # if there were none due to a failed start that prompted self.audio_failed
            self.parent.destroy() # you can click 'x' without waiting 30sec, with no error
            return # and return
        if self.unsaved_changes: # if there are unsaved changes
            # ask if they want to save
            temp = messagebox.askyesnocancel(title="Unsaved changes", \
            message="There are unsaved changes to your game. Save before quitting?")
            if temp == None: # if they picked cancel
                return # stop doing anything
            if temp: # if they picked Yes (No would be False)
                if not self.save_plain(): # if the user chose yes but then canceled the save
                    return # just return
        else: # if there are no unsaved changes, just confirm the quit
            if not messagebox.askyesno("Quit", "Really quit?"): # if user clicks no
                return # just return
        
        self.parent.destroy() # destroys the tkinter window, exiting the game

def main():
    root = Tk() # Create a Tk object from tkinter.
    chess = Chess(root) # Make my game inherit from that object.
    root.mainloop() # Run the main loop.
    mixer.music.stop()
    
if __name__ == '__main__':
    main()