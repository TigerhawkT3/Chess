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
        self.color = color
        self.location = location

    def add_if_okay(self, num1, num2):
        """
        This method is used for pieces whose movesets extend until they hit
        a piece: queens, rooks, bishops.
        Parameters:
            num1 (string): the x value of the move, from "0" to "7"
            num2 (string): the y value of the move, from "0" to "7"
        """
        if num1 not in range(8) or num2 not in range(8):
            return False
        loc = str(num1) + str(num2)
        contents = Chess.all_squares.get(str(num1)+str(num2)).piece
        if contents is None:
            self.moveset.add(loc)
            return True
        else:
            if contents.color is not self.color:
                self.moveset.add(loc)
            return False

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
        if color == "white":
            self.direction = -1
        self.moved = False
        self.vulnerable = False
        self.type = self.color + "_pawn"

    def generate_moveset(self):
        """
        Generates a moveset for this piece. Pawns can move ahead one space. If
        it's their first move, they can move ahead two spaces. If there's an
        enemy to their front-left or front-right, they can move and capture. If
        an enemy pawn's first move brings them adjacent to the pawn in question,
        the enemy pawn can be captured by moving to the front-left or
        front-right.
        """
        self.moveset = set()
        loc = self.location[0] + str(int(self.location[1])+self.direction)
        if len(loc) == 2:
            if int(loc[0]) in range(8) and int(loc[1]) in range(8):
                if Chess.all_squares.get(loc).piece is None:
                    self.moveset.add(loc)
        loc = loc[0]+str(int(loc[1])+self.direction)
        if len(loc) == 2:
            if int(loc[0]) in range(8) and int(loc[1]) in range(8):
                if not self.moved and Chess.all_squares.get(loc).piece is None \
                and Chess.all_squares.get(loc[0]+ \
                str(int(loc[1])-self.direction)).piece is None:
                    self.moveset.add(loc)
        loc = str(int(self.location[0])-1) + \
        str(int(self.location[1])+self.direction)
        if len(loc) == 2:
            if int(loc[0]) in range(8) and int(loc[1]) in range(8):
                if Chess.all_squares.get(loc).piece is not None:
                    if Chess.all_squares.get(loc).piece.color is not self.color:
                        self.moveset.add(loc)
                elif int(loc[0]) in range(8) and \
                int(loc[1])-self.direction in range(8):
                    if Chess.all_squares.get \
                (loc[0]+str(int(loc[1])-self.direction)).piece is not None:
                        if "pawn" in Chess.all_squares.get \
                        (loc[0]+str(int(loc[1])-self.direction)).piece.type:
                            if Chess.all_squares.get \
                            (loc[0]+str(int(loc[1])-self.direction)) \
                            .piece.vulnerable:
                                self.moveset.add(loc)
        loc = str(int(self.location[0])+1) + \
        str(int(self.location[1])+self.direction)
        if len(loc) == 2:
            if int(loc[0]) in range(8) and int(loc[1]) in range(8):
                if Chess.all_squares.get(loc).piece is not None:
                    if Chess.all_squares.get(loc).piece.color is not self.color:
                        self.moveset.add(loc)
                elif int(loc[0]) in range(8) and \
                int(loc[1])-self.direction in range(8):
                    if Chess.all_squares.get \
                    (loc[0]+str(int(loc[1])-self.direction)).piece is not None:
                        if "pawn" in Chess.all_squares.get \
                        (loc[0]+str(int(loc[1])-self.direction)).piece.type:
                            if Chess.all_squares.get\
                            (loc[0]+str(int(loc[1])-self.direction)) \
                            .piece.vulnerable:
                                self.moveset.add(loc)

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
        self.moved = False
        self.type = self.color + "_rook"

    def generate_moveset(self):
        """
        Generates a moveset for this piece. Rooks can move in straight lines
        horizontally or vertically until they reach a piece. If the piece
        is an enemy, that space is a valid move for the rook.
        """
        self.moveset = set()
        for num in range((int(self.location[1])+1),8):
            if not self.add_if_okay(int(self.location[0]), num):
                break
        for num in range((int(self.location[0])+1),8):
            if not self.add_if_okay(num, int(self.location[1])):
                break
        for num in range((int(self.location[1])-1),-1,-1):
            if not self.add_if_okay(int(self.location[0]), num):
                break
        for num in range((int(self.location[0])-1),-1,-1):
            if not self.add_if_okay(num, int(self.location[1])):
                break

class Knight(Piece):
    """
    An object of this class represents a knight piece.
    Attributes:
        type (string): a string describing the piece with its color and type
        moveset (set): a set of locations where this piece may move
    """
    def __init__(self, color, location):
        super().__init__(color, location)
        self.type = self.color + "_knight"

    def generate_moveset(self):
        """
        Generates a moveset for this piece. Knights can move to a predetermined
        set of locations relative to their current position. If a location is
        off the board or occupied by an allied piece, that location is not
        included in the moveset.
        """
        self.moveset = {str(int(self.location[0])-2)+ \
        str(int(self.location[1])-1),
        str(int(self.location[0])-2)+str(int(self.location[1])+1),
        str(int(self.location[0])-1)+str(int(self.location[1])-2),
        str(int(self.location[0])-1)+str(int(self.location[1])+2),
        str(int(self.location[0])+1)+str(int(self.location[1])-2),
        str(int(self.location[0])+1)+str(int(self.location[1])+2),
        str(int(self.location[0])+2)+str(int(self.location[1])-1),
        str(int(self.location[0])+2)+str(int(self.location[1])+1)}

        occupied = set()
        for place in self.moveset:
            if len(place) != 2:
                occupied.add(place)
                continue
            if int(place[0]) not in range(8) or int(place[1]) not in range(8):
                occupied.add(place)
                continue
            occupier = Chess.all_squares.get(place).piece
            if occupier is not None:
                if occupier.color is self.color:
                    occupied.add(place)
        self.moveset -= occupied

class Bishop(Piece):
    """
    An object of this class represents a bishop piece.
    Attributes:
        type (string): a string describing the piece with its color and type
        moveset (set): a set of locations where this piece may move
    """
    def __init__(self, color, location):
        super().__init__(color, location)
        self.type = self.color + "_bishop"

    def generate_moveset(self):
        """
        Generates a moveset for this piece. Bishops can move in diagonal lines
        until they reach a piece. If the piece is an enemy, that space is a
        valid move for the bishop.
        """
        self.moveset = set()
        other = int(self.location[0]) + 1
        for num in range((int(self.location[1])+1),8):
            if not self.add_if_okay(other, num):
                break
            other += 1
        other = int(self.location[1]) - 1
        for num in range((int(self.location[0])+1),8):
            if not self.add_if_okay(num, other):
                break
            other -= 1
        other = int(self.location[0]) - 1
        for num in range((int(self.location[1])-1),-1,-1):
            if not self.add_if_okay(other, num):
                break
            other -= 1
        other = int(self.location[1]) + 1
        for num in range((int(self.location[0])-1),-1,-1):
            if not self.add_if_okay(num, other):
                break
            other += 1

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
        self.type = self.color + "_king"

    def generate_moveset(self):
        """
        Generates a moveset for this piece. Kings can move to a predetermined
        set of locations relative to their current position. If a location is
        off the board or occupied by an allied piece, that location is not
        included in the moveset.
        """
        self.moveset = {str(int(self.location[0])-1)+ \
        str(int(self.location[1])-1),
        str(int(self.location[0])-1)+str(int(self.location[1])),
        str(int(self.location[0])-1)+str(int(self.location[1])+1),
        str(int(self.location[0]))+str(int(self.location[1])-1),
        str(int(self.location[0]))+str(int(self.location[1])+1),
        str(int(self.location[0])+1)+str(int(self.location[1])-1),
        str(int(self.location[0])+1)+str(int(self.location[1])),
        str(int(self.location[0])+1)+str(int(self.location[1])+1)}

        occupied = set()
        for place in self.moveset:
            if len(place) != 2:
                occupied.add(place)
                continue
            if int(place[0]) not in range(8) or int(place[1]) not in range(8):
                occupied.add(place)
                continue
            occupier = Chess.all_squares.get(place).piece
            if occupier is not None:
                if occupier.color is self.color:
                    occupied.add(place)
        self.moveset -= occupied

class Queen(Piece):
    """
    An object of this class represents a queen piece.
    Attributes:
        type (string): a string describing the piece with its color and type
        moveset (set): a set of locations where this piece may move
    """
    def __init__(self, color, location):
        super().__init__(color, location)
        self.type = self.color + "_queen"

    def generate_moveset(self):
        """
        Generates a moveset for this piece. Queens can move in diagonal,
        horizontal, or vertical lines until they reach a piece. If the piece is
        an enemy, that space is a valid move for the queen.
        """
        self.moveset = set()
        other = int(self.location[0]) + 1
        for num in range((int(self.location[1])+1),8):
            if not self.add_if_okay(other, num):
                break
            other += 1
        other = int(self.location[1]) - 1
        for num in range((int(self.location[0])+1),8):
            if not self.add_if_okay(num, other):
                break
            other -= 1
        other = int(self.location[0]) - 1
        for num in range((int(self.location[1])-1),-1,-1):
            if not self.add_if_okay(other, num):
                break
            other -= 1
        other = int(self.location[1]) + 1
        for num in range((int(self.location[0])-1),-1,-1):
            if not self.add_if_okay(num, other):
                break
            other += 1
        for num in range((int(self.location[1])+1),8):
            if not self.add_if_okay(int(self.location[0]), num):
                break
        for num in range((int(self.location[0])+1),8):
            if not self.add_if_okay(num, int(self.location[1])):
                break
        for num in range((int(self.location[1])-1),-1,-1):
            if not self.add_if_okay(int(self.location[0]), num):
                break
        for num in range((int(self.location[0])-1),-1,-1):
            if not self.add_if_okay(num, int(self.location[1])):
                break

class Square(object):
    """
    An object of this class represents a square on the board.
    Attributes:
        location (string): a string representing the square's location
        piece (Piece): the Piece object "resting" on that Square object
    """
    def __init__(self, location):
        self.location = location
        self.piece = None

class Chess(object):

    """
    An object of this class represents a Chess game, with easy mode
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
            dragged around in click-drag mode.
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
        self.name_here = Label(self.frame, text = "Filename for load/save: ")
        self.name_here.grid(row=5, column=0, sticky="E")

        # Text box for entering a file name
        self.text_box = Entry(self.frame, width=32, justify=RIGHT)
        self.text_box.grid(row=5, column=1, sticky="E")

        # Set a default file name
        self.text_box.delete(0, END)
        self.text_box.insert(0, "savechess")

        # '.txt' label
        self.txt_label = Label(self.frame, text = ".txt")
        self.txt_label.grid(row=5, column=2, sticky="W")

        # Game instructions.
        self.instructions = Label(self.frame, \
        text="Ctrl + ... (S)ave | (L)oad | " + \
        "(E)asy manual AI move | (H)ard manual AI move")
        self.instructions.grid(row=6, column = 0, columnspan = 3)

        # Create the two players, white and black.
        self.white_player = Player("white")
        self.black_player = Player("black")

        self.black_king_gif = PhotoImage(file="piece_icons/black_king.gif")
        self.black_queen_gif = PhotoImage(file="piece_icons/black_queen.gif")
        self.black_rook_gif = PhotoImage(file="piece_icons/black_rook.gif")
        self.black_bishop_gif = PhotoImage(file="piece_icons/black_bishop.gif")
        self.black_knight_gif = PhotoImage(file="piece_icons/black_knight.gif")
        self.black_pawn_gif = PhotoImage(file="piece_icons/black_pawn.gif")

        self.white_king_gif = PhotoImage(file="piece_icons/white_king.gif")
        self.white_queen_gif = PhotoImage(file="piece_icons/white_queen.gif")
        self.white_rook_gif = PhotoImage(file="piece_icons/white_rook.gif")
        self.white_bishop_gif = PhotoImage(file="piece_icons/white_bishop.gif")
        self.white_knight_gif = PhotoImage(file="piece_icons/white_knight.gif")
        self.white_pawn_gif = PhotoImage(file="piece_icons/white_pawn.gif")

        self.transparent_square_gif = \
        PhotoImage(file="piece_icons/transparent_square.gif")

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

        self.squares = []
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

        self.white_promotions = 0
        self.black_promotions = 0

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

        self.all_pieces = [self.black_rook_1, self.black_knight_1,
        self.black_bishop_1, self.black_queen, self.black_king,
        self.black_bishop_2, self.black_knight_2, self.black_rook_2,
        self.black_pawn_1, self.black_pawn_2, self.black_pawn_3,
        self.black_pawn_4, self.black_pawn_5, self.black_pawn_6,
        self.black_pawn_7, self.black_pawn_8]

        for i in range(8):
            self.all_pieces.append(self.extra_black_queens[i])

        self.all_pieces += [self.white_pawn_1, self.white_pawn_2, self.white_pawn_3,
        self.white_pawn_4, self.white_pawn_5, self.white_pawn_6,
        self.white_pawn_7, self.white_pawn_8, self.white_rook_1,
        self.white_knight_1, self.white_bishop_1, self.white_queen,
        self.white_king, self.white_bishop_2, self.white_knight_2,
        self.white_rook_2]

        for i in range(8):
            self.all_pieces.append(self.extra_white_queens[i])

        self.square_overlay = []
        for row in range(8):
            self.square_overlay.append([])
            for column in range(8):
                self.square_overlay[row].append \
                (self.board.create_image(row*50,column*50,
                anchor=NW,image=None))

        self.dragged_piece = self.board.create_image(50,50, \
        image=self.piece_pics.get("transparent_square"))

        self.refresh_images()

        # Now generate initial movesets.
        self.generate_all_movesets()

        # Bind the left mouse button to the new board.
        if self.white_player.mode == "click":
            self.board.bind("<Button-1>", self.click_click)
        else:
            self.board.bind("<Button-1>", self.click_hold)

        self.parent.bind("<Control-e>", self.easy_step)
        self.parent.bind("<Control-h>", self.hard_step)
        self.parent.bind("<Control-s>", self.save)
        self.parent.bind("<Control-l>", self.load)
        self.parent.bind("<Control-E>", self.easy_step)
        self.parent.bind("<Control-H>", self.hard_step)
        self.parent.bind("<Control-S>", self.save)
        self.parent.bind("<Control-L>", self.load)

        # Set a status message.
        self.status_message.config(text = "Welcome to Chess!")

        # Make sure the first player is white.
        self.player = self.white_player

        # Checks if any castling moves are available.
        # At this point, they won't be.
        self.check_castles()

        # When this is True, clicking the mouse on a square does move
        # highlighting and stuff. When it's False, clicking the mouse on a
        # square moves the selected piece to the clicked square.
        self.first_click = True

        self.last_ai_piece = self.black_king

    def easy_step(self, event):
        """
        If it's currently black's turn, this tells the easy AI to make one move.
        """
        if self.player is self.black_player and \
        self.black_king.location != "88" \
        and self.white_king.location != "88":
            self.easy_move()
            self.status_message.config(text = "Easy AI moved for Black! " + \
            "White's turn.")
        else:
            self.status_message.config(text = "It must be Black's " + \
            "turn for that.")

    def hard_step(self, event):
        """
        If it's currently black's turn, this tells the hard AI to make one move.
        """
        if self.player is self.black_player and \
        self.black_king.location != "88" \
        and self.white_king.location != "88":
            self.hard_move()
            self.status_message.config(text = "Hard AI moved for Black! " + \
            "White's turn.")
        else:
            self.status_message.config(text = "It must be Black's " + \
            "turn for that.")

    def save(self, event):
        """
        Saves the current game state to a file. The name is whatever was entered
        into the text box. If nothing was entered, it's given the default name
        "savechess.txt" in the current working directory. Click/drag UI options
        are included.
        """
        savelist = []

        savelist.append(self.player.color)
        savelist.append(self.black_player.mode)
        savelist.append(self.black_promotions)
        savelist.append(self.white_player.mode)
        savelist.append(self.white_promotions)

        for piece in range(48):
            savelist.append(self.all_pieces[piece].location)

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

        savelist.append(self.black_rook_1.moved)
        savelist.append(self.black_rook_2.moved)
        savelist.append(self.black_king.moved)
        savelist.append(self.white_rook_1.moved)
        savelist.append(self.white_rook_2.moved)
        savelist.append(self.white_king.moved)

        savelist.append(self.mode)

        filename = self.text_box.get() + ".txt"
        if filename == ".txt":
            filename = "savechess.txt"
            self.text_box.insert(0, "savechess")
        try:
            with open(filename, 'w', encoding = 'utf-8-sig') as output:
                for item in savelist:
                    output.write(str(item) + "\n")
        except:
            self.status_message.config(text = "Error saving file.")
        else:
            self.status_message.config(text = "File saved as " + filename + \
            ".")

    def load(self, event):
        """
        Looks for a file with a name matching whatever was entered in the text
        box. If nothing is in the text box, it looks for a file called
        "savechess.txt" in the current working directory. If a file is found,
        its data are used to restore a save state. Click/drag UI options are
        included.
        """
        savelist = []
        filename = self.text_box.get() + ".txt"
        if filename == ".txt":
            filename = "savechess.txt"
            self.text_box.insert(0, "savechess")
        try:
            with open(filename, 'r', encoding = 'utf-8-sig') as file:
                for line in file:
                    savelist.append(line[:-1])
        except:
            self.status_message.config(text = "Save file not found.")
            return

        if savelist[-1] == "easy":
            self.new_easy()
        elif savelist[-1] == "hard":
            self.new_hard()
        else:
            self.new_human()

        Chess.all_squares = {str(row)+str(column):Square(str(row)+str(column))
            for row in range(8) for column in range(8)}

        if savelist[0] == "black":
            self.player = self.black_player
        else:
            self.player = self.white_player
        if self.black_player.mode != savelist[1]:
            self.black_ui_toggle()
        self.black_player.mode = savelist[1]
        self.black_promotions = int(savelist[2])
        if self.white_player.mode != savelist[3]:
            self.white_ui_toggle()
        self.white_player.mode = savelist[3]
        self.white_promotions = int(savelist[4])

        for piece in range(48):
            self.all_pieces[piece].location = savelist[piece+5]
            if self.all_pieces[piece].location != "88":
                Chess.all_squares.get(savelist[piece+5]).piece = \
                self.all_pieces[piece]

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

        self.black_rook_1.moved = (savelist[85] == "True")
        self.black_rook_2.moved = (savelist[86] == "True")
        self.black_king.moved = (savelist[87] == "True")
        self.white_rook_1.moved = (savelist[88] == "True")
        self.white_rook_2.moved = (savelist[89] == "True")
        self.white_king.moved = (savelist[90] == "True")

        if self.player.mode == "click":
            self.board.bind("<Button-1>", self.click_click)
        else:
            self.board.bind("<Button-1>", self.click_hold)

        if self.player is self.black_player:
            self.status_message.config(text = "File loaded from " + \
            filename + "! Black's turn.")
        else:
            self.status_message.config(text = "File loaded from " + \
            filename + "! White's turn.")

        if self.black_king.location == "88":
            self.board.unbind("<Button-1>")
            self.status_message.config(text = "White wins!")
        if self.white_king.location == "88":
            self.board.unbind("<Button-1>")
            self.status_message.config(text = "Black wins!")

        self.check_castles()
        self.refresh_images()

    def check_castles(self):
        """
        Checks if anyone can castle, then makes the appropriate buttons
            available.
        """
        # if the castling area is empty, it's that player's turn, and the rook
        # and king haven't moved, enable. else, disable. if the game is over,
        # the buttons are disabled in move().
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
        # Pick a piece
        # Pick a valid move for that piece
        # Carry it out
        living_pieces = {self.black_rook_1, self.black_knight_1,
        self.black_bishop_1, self.black_queen, self.black_king,
        self.black_bishop_2, self.black_knight_2, self.black_rook_2,
        self.black_pawn_1, self.black_pawn_2, self.black_pawn_3,
        self.black_pawn_4, self.black_pawn_5, self.black_pawn_6,
        self.black_pawn_7, self.black_pawn_8}
        for extra in self.extra_black_queens:
            living_pieces.add(extra)

        dead_pieces = set()
        self.generate_all_movesets()
        for piece in living_pieces:
            if piece.location == "88" or len(piece.moveset) == 0:
                dead_pieces.add(piece)
        living_pieces -= dead_pieces

        piece_to_move = sample(living_pieces, 1)[0]
        move = sample(piece_to_move.moveset, 1)[0]

        for piece in living_pieces:
            if self.white_king.location in piece.moveset:
                piece_to_move = piece
                move = self.white_king.location

        self.board.itemconfig(self.squares[int(piece_to_move.location[0])]
            [int(piece_to_move.location[1])], fill="darkblue")
        self.board.itemconfig(self.squares[int(move[0])]
            [int(move[1])], fill="darkgreen")

        self.move(piece_to_move, move)
        self.check_castles()

    def hard_move(self):
        """
        Tries to capture valuable pieces. Defends valuable pieces by capturing
        the threat or by fleeing. Tries to avoid moving the king too much or
        moving the same piece back and forth repeatedly.
        """
        living_pieces = {self.black_rook_1, self.black_knight_1,
        self.black_bishop_1, self.black_queen, self.black_king,
        self.black_bishop_2, self.black_knight_2, self.black_rook_2,
        self.black_pawn_1, self.black_pawn_2, self.black_pawn_3,
        self.black_pawn_4, self.black_pawn_5, self.black_pawn_6,
        self.black_pawn_7, self.black_pawn_8}
        for extra in self.extra_black_queens:
            living_pieces.add(extra)

        dead_pieces = set()
        self.generate_all_movesets()
        for piece in living_pieces:
            if piece.location == "88" or len(piece.moveset) == 0:
                dead_pieces.add(piece)
        living_pieces -= dead_pieces

        piece_to_move = sample(living_pieces, 1)[0]
        move = sample(piece_to_move.moveset, 1)[0]

        enemy_pieces = {self.white_rook_1, self.white_knight_1,
        self.white_bishop_1, self.white_queen, self.white_king,
        self.white_bishop_2, self.white_knight_2, self.white_rook_2,
        self.white_pawn_1, self.white_pawn_2, self.white_pawn_3,
        self.white_pawn_4, self.white_pawn_5, self.white_pawn_6,
        self.white_pawn_7, self.white_pawn_8}
        for extra in self.extra_white_queens:
            enemy_pieces.add(extra)

        dead_enemies = set()
        for piece in enemy_pieces:
            if piece.location == "88" or len(piece.moveset) == 0:
                dead_enemies.add(piece)
        enemy_pieces -= dead_enemies

        enemy_moves = set()
        for piece in enemy_pieces:
            enemy_moves |= piece.moveset

        safe_moves = set()
        safe_pieces = set()
        for piece in living_pieces:
            if len(piece.moveset - enemy_moves) > 0:
                safe_moves |= piece.moveset - enemy_moves
                safe_pieces.add(piece)

        while (move not in safe_moves and len(safe_moves) > 5) or \
        (piece_to_move is self.black_king and randint(0,9) in range(9)):
            piece_to_move = sample(safe_pieces, 1)[0]
            move = sample(piece_to_move.moveset & safe_moves, 1)[0]

        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.black_king, self.white_king)
        if decision[0]:
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_king":
                piece_to_move = decision[2]
                move = decision[3]

        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.black_knight_1, self.white_knight_1)
        if decision[0]:
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_knight":
                piece_to_move = decision[2]
                move = decision[3]

        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.black_knight_2, self.white_knight_2)
        if decision[0]:
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_knight":
                piece_to_move = decision[2]
                move = decision[3]

        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.black_bishop_1, self.white_bishop_1)
        if decision[0]:
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_bishop":
                piece_to_move = decision[2]
                move = decision[3]

        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.black_bishop_2, self.white_bishop_2)
        if decision[0]:
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_bishop":
                piece_to_move = decision[2]
                move = decision[3]

        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.black_rook_1, self.white_rook_1)
        if decision[0]:
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_rook":
                piece_to_move = decision[2]
                move = decision[3]

        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.black_rook_2, self.white_rook_2)
        if decision[0]:
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_rook":
                piece_to_move = decision[2]
                move = decision[3]

        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.black_queen, self.white_queen)
        if decision[0]:
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_queen":
                piece_to_move = decision[2]
                move = decision[3]

        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.extra_black_queens[1], self.extra_white_queens[1])
        if decision[0]:
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_queen":
                piece_to_move = decision[2]
                move = decision[3]

        decision = self.piece_priority(living_pieces, safe_moves, enemy_pieces,
        enemy_moves, self.black_king, self.white_king)
        if decision[0]:
            if decision[1] or Chess.all_squares.get(move).piece is None or \
            piece_to_move.type != "black_king":
                piece_to_move = decision[2]
                move = decision[3]

        self.board.itemconfig(self.squares[int(piece_to_move.location[0])]
            [int(piece_to_move.location[1])], fill="darkblue")
        self.board.itemconfig(self.squares[int(move[0])]
            [int(move[1])], fill="darkgreen")

        self.move(piece_to_move, move)
        self.check_castles()

    def piece_priority(self, living_pieces, safe_moves, enemy_pieces,
    enemy_moves, check_ally, check_enemy):
        """
        Determines which move is the most important. Tries to capture first. If
        there's nothing to capture, avoids being captured if necessary. If a
        piece is in danger but it may be safely rescued by capturing an enemy
        piece (even if it's a less-valuable piece), it uses that strategy.
        """
        for piece in living_pieces:
            if check_enemy.location in piece.moveset:
                return [True, True, piece, check_enemy.location]

        if check_ally.location in enemy_moves:
            for enemy in enemy_pieces:
                if enemy.location in safe_moves:
                    for piece in living_pieces:
                        if enemy.location in piece.moveset:
                            return[True, True, piece, enemy.location]
            for loc in check_ally.moveset:
                if loc not in enemy_moves:
                    if ((check_ally is self.last_ai_piece and loc == \
                    self.last_source) and len(check_ally.moveset) > 1):
                        continue
                    return [True, False, check_ally, loc]

        return [False, False]

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

        if self.first_click:
            if not self.choose_piece(token):
                return
            self.first_click = False
        else:
            self.choose_target(click)
            self.first_click = True

    def click_hold(self, event):
        """
        Indicates which piece a player wants to move.
        Parameter:
            event (sequence): data describing the input. In this case, it's
                just mouse cursor coordinates when the mouse was left-clicked.
        """
        click = str(event.x//50) + str(event.y//50)
        token = Chess.all_squares.get(click).piece
        if not self.choose_piece(token):
            return
        self.board.itemconfig(self.square_overlay[int(click[0])]
        [int(click[1])], image=self.piece_pics.get("transparent_square"))
        self.board.itemconfig(self.dragged_piece, image=self.piece_pics.get
        (self.chosen_piece.type))
        self.board.coords(self.dragged_piece, event.x, event.y)
        self.board.bind("<B1-Motion>", self.click_drag)
        self.board.bind("<ButtonRelease-1>", self.click_release)
        self.board.itemconfig(self.square_overlay[event.x//50][event.y//50],
                    image=self.piece_pics.get("transparent_square"))

    def click_drag(self, event):
        """
        Visually drags a piece across the board.
        Parameter:
            event (sequence): data describing the input. In this case, it's
                just mouse cursor coordinates when the mouse moved, while the
                left mouse button was held down.
        """
        self.board.coords(self.dragged_piece, event.x, event.y)

    def click_release(self, event):
        """
        Indicates which square a player wants to move to. Humans only.
        Parameter:
            event (sequence): data describing the input. In this case, it's
            just mouse cursor coordinates when the left mouse button was
            released.
        """
        self.board.itemconfig(self.dragged_piece, image=self.piece_pics.get
        ("transparent_square"))
        self.choose_target(str(event.x//50) + str(event.y//50))
        self.board.unbind("<B1-Motion>")
        self.board.unbind("<ButtonRelease-1>")
        self.refresh_images()

    def choose_piece(self, token):
        """
        Chooses a piece to move. Humans only.
        Parameter:
            token (Piece): the piece that the player wants to select
        """
        if token is None:
            return False
        if token.color != self.player.color:
            return False
        self.chosen_piece = token
        token.generate_moveset()
        if len(token.moveset) == 0:
            return False
        if self.player is self.white_player:
            color = ""
        else:
            color = "dark"
        self.board.itemconfig(self.squares[int(token.location[0])]
        [int(token.location[1])], fill=color+"blue")
        for move in token.moveset:
            self.board.itemconfig(self.squares[int(move[0])][int(move[1])],
            fill=color+"green")
        return True

    def choose_target(self, click):
        """
        Moves a chosen piece to the selected square, if possible. Humans only.
        Parameter:
            click (string): a string representing the location of the selected
                destination square
        """
        for row in range(8):
            for column in range(8):
                if (row+column)%2 == 0:
                    color = 'white'
                else:
                    color = 'black'
                self.board.itemconfig(self.squares[row][column], fill=color)
        if self.player is self.white_player:
            color = "dark"
        else:
            color = ""
        if self.last_source is not None and self.last_target is not None:
            self.board.itemconfig(self.squares[int(self.last_source[0])]
                [int(self.last_source[1])], fill=color+"blue")
            self.board.itemconfig(self.squares[int(self.last_target[0])]
                [int(self.last_target[1])], fill=color+"green")
        if click in self.chosen_piece.moveset:
            self.move(self.chosen_piece, click)
            if self.mode == "easy" and self.black_king.location != "88":
                self.easy_move()
            if self.mode == "hard" and self.black_king.location != "88":
                self.hard_move()
            self.check_castles()

    def move(self, chosen_piece, destination):
        """
        Carries out a player's move (human or computer), with win logic.
        Parameters:
            chosen_piece (Piece): the Piece that the player (human or AI) is
                moving
            destination (string): the string representation of the destination
                square
        """
        if self.last_source is not None and self.last_target is not None:
            for row in range(8):
                for column in range(8):
                    if (row+column)%2 == 0:
                        color = 'white'
                    else:
                        color = 'black'
                    self.board.itemconfig(self.squares[row][column], fill=color)
        self.last_source = chosen_piece.location
        self.last_target = destination
        if self.player is self.white_player:
            color = ""
            self.status_message.config(text = "Black's turn.")
        else:
            color = "dark"
            self.status_message.config(text = "White's turn.")
        self.board.itemconfig(self.squares[int(self.last_source[0])]
            [int(self.last_source[1])], fill=color+"blue")
        self.board.itemconfig(self.squares[int(self.last_target[0])]
            [int(self.last_target[1])], fill=color+"green")

        self.safe_pawns()
        target_piece = Chess.all_squares.get(destination).piece
        original_location = chosen_piece.location
        if hasattr(chosen_piece, "moved"):
                if "pawn" in chosen_piece.type:
                    if int(destination[1]) - int(chosen_piece.location[1]) \
                    in range(-2,3,4):
                        chosen_piece.vulnerable = True
                chosen_piece.moved = True
        if "pawn" in chosen_piece.type:
            behind = Chess.all_squares.get(destination[0] +
            str(int(destination[1])-chosen_piece.direction)).piece
            if behind is not None:
                if "pawn" in behind.type:
                    if behind.vulnerable:
                        behind.location = "88"
                        Chess.all_squares.get(destination[0] +
                        str(int(destination[1])-chosen_piece.direction)) \
                        .piece = None
            if destination[1] == "0":
                chosen_piece.location = "88"
                if target_piece is not None:
                    target_piece.location = "88"
                target_piece = Chess.all_squares.get(destination).piece = \
                self.extra_white_queens[self.white_promotions]
                target_piece.location = destination
                self.white_promotions += 1
                chosen_piece = target_piece
            if destination[1] == "7":
                chosen_piece.location = "88"
                if target_piece is not None:
                    target_piece.location = "88"
                target_piece = Chess.all_squares.get(destination).piece= \
                self.extra_black_queens[self.black_promotions]
                target_piece.location = destination
                self.black_promotions += 1
                chosen_piece = target_piece
        if target_piece is not None:
            Chess.all_squares.get(original_location).piece = None
            target_piece.location = "88"
            if self.black_king.location == "88":
                target_piece = chosen_piece
                self.status_message.config(text = "White wins!")
                self.board.unbind("<Button-1>")
                self.castle_black_left_button.config(state=DISABLED)
                self.castle_black_right_button.config(state=DISABLED)
                self.castle_white_left_button.config(state=DISABLED)
                self.castle_white_right_button.config(state=DISABLED)
            if self.white_king.location == "88":
                target_piece = chosen_piece
                self.status_message.config(text = "Black wins!")
                self.board.unbind("<Button-1>")
                self.castle_black_left_button.config(state=DISABLED)
                self.castle_black_right_button.config(state=DISABLED)
                self.castle_white_left_button.config(state=DISABLED)
                self.castle_white_right_button.config(state=DISABLED)
            self.check_castles()
            Chess.all_squares.get(destination).piece = target_piece \
            = chosen_piece
        Chess.all_squares.get(original_location).piece = None
        chosen_piece.location = destination
        Chess.all_squares.get(chosen_piece.location).piece = target_piece \
        = chosen_piece
        self.refresh_images()
        if self.player is self.white_player:
            self.player = self.black_player
        else:
            self.player = self.white_player
        if self.black_king.location != "88" and self.white_king.location \
        != "88":
            if self.player.mode == "click":
                self.board.bind("<Button-1>", self.click_click)
            else:
                self.board.bind("<Button-1>", self.click_hold)

    def safe_pawns(self):
        """
        When a player starts their turn, all of their pieces start out as not
        vulnerable.
        """
        if self.player.color == "white":
            self.white_pawn_1.vulnerable = False
            self.white_pawn_2.vulnerable = False
            self.white_pawn_3.vulnerable = False
            self.white_pawn_4.vulnerable = False
            self.white_pawn_5.vulnerable = False
            self.white_pawn_6.vulnerable = False
            self.white_pawn_7.vulnerable = False
            self.white_pawn_8.vulnerable = False
        else:
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
        self.safe_pawns()
        for row in range(8):
            for column in range(8):
                if (row+column)%2 == 0:
                    color = 'white'
                else:
                    color = 'black'
                self.board.itemconfig(self.squares[row][column], fill=color)
        self.board.itemconfig(self.squares[3][0], fill="darkblue")
        self.board.itemconfig(self.squares[2][0], fill="darkgreen")
        Chess.all_squares.get("00").piece = None
        Chess.all_squares.get("20").piece = self.black_king
        Chess.all_squares.get("30").piece = self.black_rook_1
        Chess.all_squares.get("40").piece = None
        self.black_king.location = "20"
        self.black_king.moved = True
        self.black_rook_1.location = "30"
        self.black_rook_1.moved = True
        self.player = self.white_player
        self.check_castles()
        self.refresh_images()
        self.status_message.config(text = "Black castled queenside! " + \
        "White's turn.")

    def castle_black_right(self):
        """
        Castles at black kingside.
        """
        self.safe_pawns()
        for row in range(8):
            for column in range(8):
                if (row+column)%2 == 0:
                    color = 'white'
                else:
                    color = 'black'
                self.board.itemconfig(self.squares[row][column], fill=color)
        self.board.itemconfig(self.squares[5][0], fill="darkblue")
        self.board.itemconfig(self.squares[6][0], fill="darkgreen")
        Chess.all_squares.get("40").piece = None
        Chess.all_squares.get("50").piece = self.black_rook_2
        Chess.all_squares.get("60").piece = self.black_king
        Chess.all_squares.get("70").piece = None
        self.black_rook_2.location = "50"
        self.black_rook_2.moved = True
        self.black_king.location = "60"
        self.black_king.moved = True
        self.player = self.white_player
        self.check_castles()
        self.refresh_images()
        self.status_message.config(text = "Black castled kingside! " + \
        "White's turn.")

    def castle_white_left(self):
        """
        Castles at white queenside.
        """
        self.safe_pawns()
        for row in range(8):
            for column in range(8):
                if (row+column)%2 == 0:
                    color = 'white'
                else:
                    color = 'black'
                self.board.itemconfig(self.squares[row][column], fill=color)
        self.board.itemconfig(self.squares[3][7], fill="blue")
        self.board.itemconfig(self.squares[2][7], fill="green")
        Chess.all_squares.get("07").piece = None
        Chess.all_squares.get("27").piece = self.white_king
        Chess.all_squares.get("37").piece = self.white_rook_1
        Chess.all_squares.get("47").piece = None
        self.white_king.location = "27"
        self.white_king.moved = True
        self.white_rook_1.location = "37"
        self.white_rook_1.moved = True
        self.player = self.black_player
        self.check_castles()
        self.refresh_images()
        if self.mode == "easy":
            self.easy_move()
        if self.mode == "hard":
            self.hard_move()
        self.status_message.config(text = "White castled queenside! " + \
        "Black's turn.")

    def castle_white_right(self):
        """
        Castles at white kingside.
        """
        self.safe_pawns()
        for row in range(8):
            for column in range(8):
                if (row+column)%2 == 0:
                    color = 'white'
                else:
                    color = 'black'
                self.board.itemconfig(self.squares[row][column], fill=color)
        self.board.itemconfig(self.squares[5][7], fill="blue")
        self.board.itemconfig(self.squares[6][7], fill="green")
        Chess.all_squares.get("47").piece = None
        Chess.all_squares.get("57").piece = self.white_rook_2
        Chess.all_squares.get("67").piece = self.white_king
        Chess.all_squares.get("77").piece = None
        self.white_rook_2.location = "57"
        self.white_rook_2.moved = True
        self.white_king.location = "67"
        self.white_king.moved = True
        self.player = self.black_player
        self.check_castles()
        self.refresh_images()
        if self.mode == "easy":
            self.easy_move()
        if self.mode == "hard":
            self.hard_move()
        self.status_message.config(text = "White castled kingside! " + \
        "Black's turn.")

    def refresh_images(self):
        """
        Looks at each Square. If the Square contains a Piece, the proper
        square_overlay cell has its image set to that piece's image. If the
        Square doesn't contain a Piece, the proper square_overlay cell has its
        image set to the transparent image.
        """
        for row in range(8):
            for column in range(8):
                drawpiece = Chess.all_squares.get(str(row)+str(column)).piece
                if drawpiece is not None:
                    self.board.itemconfig(self.square_overlay[row][column],
                    image=self.piece_pics.get(drawpiece.type))
                else:
                    self.board.itemconfig(self.square_overlay[row][column],
                    image=self.piece_pics.get("transparent_square"))

    def black_ui_toggle(self):
        """
        Switches between the "click/click" move functionality and the
        "click/drag" move functionality for the black player.
        """
        if self.black_player.mode == "click":
            self.black_player.mode = "drag"
            self.black_click_button.config(text = "Active mode:\nclick/drag")
            if self.player is self.black_player and \
            self.black_king.location != "88" and \
            self.white_king.location != "88":
                self.board.bind("<Button-1>", self.click_hold)
        else:
            self.black_player.mode = "click"
            self.black_click_button.config(text = "Active mode:\nclick/click")
            if self.player is self.black_player and \
            self.black_king.location != "88" and \
            self.white_king.location != "88":
                self.board.bind("<Button-1>", self.click_click)

    def white_ui_toggle(self):
        """
        Switches between the "click/click" move functionality and the
        "click/drag" move functionality for the white player.
        """
        if self.white_player.mode is "click":
            self.white_player.mode = "drag"
            self.white_click_button.config(text = "Active mode:\nclick/drag")
            if self.player is self.white_player and \
            self.black_king.location != "88" and \
            self.white_king.location != "88":
                self.board.bind("<Button-1>", self.click_hold)
        else:
            self.white_player.mode = "click"
            self.white_click_button.config(text = "Active mode:\nclick/click")
            if self.player is self.white_player and \
            self.black_king.location != "88" and \
            self.white_king.location != "88":
                self.board.bind("<Button-1>", self.click_click)

def main():
    root = Tk() # Create a Tk object from tkinter.
    chess = Chess(root) # Make my game inherit from that object.
    root.mainloop() # Run the main loop.

if __name__ == '__main__':
    main()
