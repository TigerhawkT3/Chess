#-------------------------------------------------------------------------------
# Name:        Chess Notation
# Purpose:     Simulate a game of chess and produce notations for each move in many common formats.
#
# Author:      David Muller
#
# Created:     08/13/2015
# Copyright:   (c) David Muller 2015
# Licence:     <your license>
# Notes:       To produce correct results when redirecting this module's output boards to a file
#              in Windows Powershell, set the output to UTF-8 by running the following command (in PS):
#
#              $OutputEncoding = [Console]::OutputEncoding = (new-object System.Text.UTF8Encoding $false)
#-------------------------------------------------------------------------------

import sys
import codecs
argvs = dict(pair.split(maxsplit=1) for pair in (' '.join(sys.argv)).lower().split(' *')[1:])
unicode_pieces = {' ':' ', 'r':'♜', 'n':'♞', 'b':'♝', 'q':'♕', 'k':'♚', 'p':'♟', 'R':'♖', 'N':'♘', 'B':'♗', 'Q':'♛', 'K':'♔', 'P':'♙'}
chess9_to_iccf_castles = {'wl':'5131', 'wr':'5171', 'bl':'5838', 'br':'5878'}
promotions = 'PQRBN'
descriptive_files = ['QR', 'QN', 'QB', 'Q', 'K', 'KB', 'KN', 'KR']
result=[]

def export_move(model, s_row, s_column, d_row, d_column, piece, capture='', enpassant=False, promotion=0, comment=''):
    """
    Returns a tab-delimited string containing all notations for this move.
    Parameters:
        model (list): the current model of the game board
        s_row (int): the source row, 0 at the top and 7 at the bottom
        s_column (int): the source column, 0 at the left and 7 at the right
        d_row (int): the destination row, 0 at the top and 7 at the bottom
        d_column (int): the destination column, 0 at the left and 7 at the right
        piece (str): the moving piece type, e.g. 'p', 'Q'
        capture (str): captured piece type, e.g. 'p', 'Q', etc., or 'E' for smith en passant
        enpassant (str): 'E' if it's an en passant capture, else ''
        promotion (int): the promotion, 0,1,2,3,4 for none,queen,rook,bishop,knight
        comment (str): the text of any comments for this move
    """
    places = [] # for disambiguation
    rank = '' # for disambiguation
    file = '' # for disambiguation
    
    if piece in 'Pp': # only needs disambiguation on captures, including en passant
        difference = s_column - d_column
        if difference and model[s_row][d_column-difference]==piece:
            places.append((s_row, d_column-difference))
    elif piece in 'Nn':
        for row,col in [(-2,-1), (-1,-2), (1,-2), (2,-1),
                       (-2,1), (-1,2), (1,2), (2,1)]:
            if d_row-row in range(8) and d_column-col in range(8) and model[d_row-row][d_column-col] == piece and (d_row-row, d_column-col) != (s_row, s_column):
                places.append((d_row-row, d_column-col))
    elif piece in 'Kk':
        for row,col in [(-1,-1), (-1,0), (-1,1),
                        (0,-1), (0,1),
                        (1,-1), (1,0), (1,-1)]:
            if d_row-row in range(8) and d_column-col in range(8) and model[d_row-row][d_column-col] == piece and (d_row-row, d_column-col) != (s_row, s_column):
                places.append((d_row-row, d_column-col))
    else:
        if piece in 'BbQq':
            for difference in range(1, min(d_row, d_column)+1): # up left
                if model[d_row-difference][d_column-difference] == piece:
                    places.append((d_row-difference, d_column-difference))
                    break
                elif model[d_row-difference][d_column-difference] != ' ':
                    break
            for difference in range(1, 8-max(d_row, d_column)): # down right
                if model[d_row+difference][d_column+difference] == piece:
                    places.append((d_row+difference, d_column+difference))
                    break
                elif model[d_row+difference][d_column+difference] != ' ':
                    break
            for difference in range(1, min(7-d_row, d_column)+1): # down left
                if model[d_row+difference][d_column-difference] == piece:
                    places.append((d_row+difference, d_column-difference))
                    break
                elif model[d_row+difference][d_column-difference] != ' ':
                    break
            for difference in range(1, min(d_row, 7-d_column)+1): # up right
                if model[d_row-difference][d_column+difference] == piece:
                    places.append((d_row-difference, d_column+difference))
                    break
                elif model[d_row-difference][d_column+difference] != ' ':
                    break
            
        if piece in 'RrQq':
            for column in range(d_column-1, -1, -1): # left
                if model[d_row][column] == piece:
                    places.append((d_row, column))
                    break
                elif model[d_row][column] != ' ':
                    break
            for column in range(d_column+1, 8): # right
                if model[d_row][column] == piece:
                    places.append((d_row, column))
                    break
                elif model[d_row][column] != ' ':
                    break
            for row in range(d_row-1, -1, -1): # up
                if model[row][d_column] == piece:
                    places.append((row, d_column))
                    break
                elif model[row][d_column] != ' ':
                    break
            for row in range(d_row+1, 8): # down
                if model[row][d_column] == piece:
                    places.append((row, d_column))
                    break
                elif model[row][d_column] != ' ':
                    break
        
    for row,col in places:
        if col != s_column:
            file = 'abcdefgh'[s_column]
        else:
            rank = '87654321'[s_row]
    
    notations = []
    
    notations.append((piece.upper() if piece not in 'Pp' else '') +
            file +
            rank +
           ('x' if capture or enpassant else '') +
            'abcdefgh'[d_column] +
            '87654321'[d_row] +
           (promotions[promotion] if promotion else '') +
           ('+' if comment.startswith('+') else ''))
    notations.append((unicode_pieces[piece] if piece not in 'Pp' else '') +
            file +
            rank +
           ('x' if capture or enpassant else '') +
            'abcdefgh'[d_column] +
            '87654321'[d_row] +
           (unicode_pieces[promotions[promotion] if piece.isupper() else promotions[promotion].lower()] if promotion else '') +
           ('+' if comment.startswith('+') else ''))
    notations.append((piece.upper() if piece not in 'Pp' else '') +
            'abcdefgh'[s_column] +
            '87654321'[s_row] +
            ('x' if capture or enpassant else '-') +
            'abcdefgh'[d_column] +
            '87654321'[d_row] +
           (promotions[promotion] if promotion else '') +
           ('+' if comment.startswith('+') else ''))
    notations.append((piece.upper() if piece not in 'Pp' else '') +
            file +
            rank +
            'abcdefgh'[d_column] +
            '87654321'[d_row] +
           (promotions[promotion] if promotion else ''))
    notations.append((piece.upper() if piece not in 'Pp' else '') +
            'abcdefgh'[s_column] +
            '87654321'[s_row] +
           (('x' + (capture.upper() if not enpassant else 'p' if piece=='P' else 'P')) if capture or enpassant else '-') +
            'abcdefgh'[d_column] +
            '87654321'[d_row] +
           (promotions[promotion] if promotion else '') +
           ('+' if comment.startswith('+') else ''))
    notations.append((piece.upper() if piece not in 'Pp' else '') +
             file +
             rank +
            ((':' + (capture.upper() if not enpassant else 'p' if piece=='P' else 'P')) if capture or enpassant else '') +
             'abcdefgh'[d_column] +
             '87654321'[d_row] +
            (promotions[promotion] if promotion else '') +
            ('+' if comment.startswith('+') else ''))
    notations.append('abcdefgh'[s_column] +
             '87654321'[s_row] +
             'abcdefgh'[d_column] +
             '87654321'[d_row] +
            (capture.lower() if not enpassant else 'E') +
            (promotions[promotion] if promotion else ''))
    notations.append(descriptive_files[s_column] +
            ('87654321'[s_row] if piece.isupper() else '12345678'[s_row]) +
            piece.upper() +
            ('x' if capture else '-') +
            descriptive_files[d_column] +
            ('87654321'[d_row] if piece.isupper() else '12345678'[d_row]) +
            (capture.upper() if not enpassant else 'P') +
            (promotions[promotion].join('()') if promotion else '') +
            ('+' if comment.startswith('+') else ''))
    notations.append('ABCDEFGH'[s_column] +
                  '87654321'[s_row] +
                  '-' +
                  'ABCDEFGH'[d_column] +
                  '87654321'[d_row] +
                 (promotions[promotion].join('()') if promotion else ''))
    notations.append('{}{}{}{}{}'.format(s_column+1, 8-s_row, d_column+1, 8-d_row, promotion if promotion else ''))
    notations.append(comment[1:] if comment.startswith('+') else comment)
    
    return '\t'.join(notations)
    
def export_castle(move):
    """
    Returns a tab-delimited string with all notations for castles, in the following order:
    SAN FAN LAN MAN RAN CRAN Smith Descriptive Coordinate ICCF
    Parameter:
        move (str): the two-character string representing the castle location
    """
    return {'bl':'0-0-0\t0-0-0\t0-0-0\t0-0-0\t0-0-0\t0-0-0\te8c8C\tO-O-O\tE8-C8\t5838',
            'br':'0-0\t0-0\t0-0\t0-0\t0-0\t0-0\te8g8c\tO-O\tE8-G8\t5878',
            'wl':'0-0-0\t0-0-0\t0-0-0\t0-0-0\t0-0-0\t0-0-0\te1c1C\tO-O-O\tE1-C1\t5131',
            'wr':'0-0\t0-0\t0-0\t0-0\t0-0\t0-0\te1g1c\tO-O\tE1-G1\t5171'}[move]
            # san, fan, lan, man, ran, cran, smith, descriptive, coordinate, iccf
    
def new_game():
    """
    Returns a 2D list representing the game board.
    """
    return [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
       ['p' for i in range(8)],
       [' ' for i in range(8)],
       [' ' for i in range(8)],
       [' ' for i in range(8)],
       [' ' for i in range(8)],
       ['P' for i in range(8)],
       ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']]

def chess9_to_iccf_full(moves):
    """
    Returns a list of moves in ICCF notation, converted from the given chess9 moves. No castling.
    Parameter:
        moves (list): a list of moves in chess9 notation
    """
    return [chess9_to_iccf_move(move) if len(move)==4 else chess9_to_iccf_castles[move] for move in moves]

# no iccf_to_chess9_full yet because castle indicators require knowledge of the game board

def chess9_to_iccf_move(move):
    """
    Returns a move in ICCF notation, converted from the given chess9 move. No castling.
    Parameter:
        move (str): a move in chess9 notation
    """
    return '{}{}{}{}'.format(int(move[0])+1, 8-int(move[1]), int(move[2])+1, 8-int(move[3]))

def iccf_to_chess9_move(move):
    """
    Returns a move in chess9 notation, converted from the given ICCF move. No castling.
    Parameter:
        move (str): a move in ICCF notation
    """
    return '{}{}{}{}'.format(int(move[0])-1, 8-int(move[1]), int(move[2])-1, 8-int(move[3]))

def iccf_to_model_move(move):
    '''
    Accepts a move in ICCF format and returns a model-friendly source row, source column,
    destination row, destination column, and pawn promotion value (or 0 if no promotion).
    The promotion value is 0:nothing, 1:queen, 2:rook, 3:bishop, 4:knight.
    '''
    if move[4:5].isdigit():
        promote = int(move[4])
        comments = move[5:]
    else:
        promote = 0
        comments = move[4:]
    return 8-int(move[1]), int(move[0])-1, 8-int(move[3]), int(move[2])-1, promote, comments
    
def do_move(move):
    '''
    Accepts a move in ICCF format and carries it out on the model.
    Castling:
    ICCF   model
    5131 > 74720
    5171 > 74760
    5838 > 04020
    5878 > 04060
    Promotion:
    
    '''
    move = iccf_to_model_move(move)
    src_row, src_col, dst_row, dst_col, promo, comments = move
    castling = False
    if model[7][4]=='K':
        if move==(7,4,7,2,0):
            castling = True
            result.append(export_castle('wl'))
            model[7][3] = 'R'
            model[7][0] = ' '
        elif move==(7,4,7,6,0):
            castling = True
            result.append(export_castle('wr'))
            model[7][5] = 'R'
            model[7][7] = ' '
    elif model[0][4]=='k':
        if move==(0,4,0,2,0):
            castling = True
            result.append(export_castle('bl'))
            model[0][3] = 'r'
            model[0][0] = ' '
        elif move==(0,4,0,6,0):
            castling = True
            result.append(export_castle('br'))
            model[0][5] = 'r'
            model[0][7] = ' '
    piece = model[src_row][src_col]
    if src_col != dst_col and model[dst_row][dst_col] == ' ' and piece in 'Pp':
        enpassant = True
    else:
        enpassant = False
    if not castling:
        result.append(export_move(model, src_row, src_col, dst_row, dst_col, piece, model[dst_row][dst_col].strip(), enpassant, promo, comments))
    if promo: # if a promotion is indicated, do so
        piece = promotions[promo] if piece.isupper() else promotions[promo].lower()
    if enpassant: # for en passant
        if piece=='P': # white pawn
            model[dst_row+1][dst_col] = ' ' # blank out lower square
        else: # black pawn
            model[dst_row-1][dst_col] = ' ' # blank out upper square
    model[dst_row][dst_col] = piece # move the piece
    model[src_row][src_col] = ' ' # blank out the source square
    # export notations to result here


def get_board(border=True, end='\n', icons=False):
    """
    Prints the current model as a board, using alt+186 ║, alt+187 ╗, alt+188 ╝,
    alt+200 ╚, alt+201 ╔, and alt+205 ═ to frame the board.
    Parameters:
        border (bool): indicates that a border should be drawn with unicode box-drawing characters
        icons (bool): indicates that unicode icons should be used instead of strings -
            must be used with name, because consoles can't handle the Unicode icons
    """
    return (
            (('═' if border else '=')*15).join(('╔' if border else '/') + ('╗' if border else '\\')) + lineend +
            lineend.join(' '.join(row if not icons else (unicode_pieces[item] for item in row)).join('║║' if border else '||') for row in model) +
            lineend + (('═' if border else '=')*15).join(('╚' if border else '\\') + ('╝' if border else '/')) + lineend
           )

model = new_game() # populate the model as a new game

if __name__ == '__main__':
    if argvs.get('board', '0').lower() not in ('off', '0', 'no'):
        showboard = True
        try:
            print(('═'*15).join('╔╗'))
        except UnicodeEncodeError:
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
            icons = True
            lineend='\r\n'
            print(('═'*15).join('╔╗') + '\r\n' +
                   lineend.join(' '.join(unicode_pieces[item] for item in row).join('║║') for row in model) +
                   lineend + ('═'*15).join('╚╝') + lineend, end=lineend
                 )
        else:
            lineend='\n'
            try:
                print(lineend.join(' '.join(unicode_pieces[item] for item in row).join('║║') for row in model), end=lineend)
            except UnicodeEncodeError:
                icons = False
                print(lineend.join(' '.join(row).join('║║') for row in model), end=lineend)
            else:
                icons = True
            finally:
                print(('═'*15).join('╚╝') + lineend, end=lineend)
    else:
        showboard = False

    while 1:
        try:
            user_in = input()
        except EOFError:
            break
        if not user_in:
            break
        else:
            do_move(user_in)
            if showboard:
                print(get_board(icons=icons, end=lineend), end=lineend)

    if argvs.get('notations', '0').lower() not in ('off', '0', 'no'):
        print('SAN\tFAN\tLAN\tMAN\tRAN\tCRAN\tSmith\tDescriptive\tCoord\tICCF\tComments', end=lineend)
        for line in result:
            try:
                print(line, end=lineend)
            except UnicodeEncodeError:
                print(line.split('\t')[0] + '\t\t' + '\t'.join(line.split('\t')[2:]), end=lineend)
                    
'''
import chess_notation as cn
just translate every chess9 move to iccf
change step_forward to ### if do_move == "5838" and not black_king.moved: # if it's 'bl', ### etc. for castling
change step_forward to add ### do_move = cn.iccf_to_chess9_move(do_move) # switch to internal format ### for regular move
'''