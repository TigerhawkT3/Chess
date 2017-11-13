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
import re
import codecs
import itertools
argvs = dict(pair.split(maxsplit=1) for pair in (' '.join(sys.argv)).lower().split(' *')[1:])
unicode_pieces = {' ':' ', 'r':'♜', 'n':'♞', 'b':'♝', 'q':'♕', 'k':'♚', 'p':'♟', 'R':'♖', 'N':'♘', 'B':'♗', 'Q':'♛', 'K':'♔', 'P':'♙'}
#unicode_pieces = {' ':' ', 'r':'♖', 'n':'♘', 'b':'♗', 'q':'♛', 'k':'♔', 'p':'♙', 'R':'♖', 'N':'♘', 'B':'♗', 'Q':'♛', 'K':'♔', 'P':'♙'}
chess11_to_iccf_castles = {'wl':'5131', 'wr':'5171', 'bl':'5838', 'br':'5878'}
promotions = 'PQRBN'
descriptive_files = ['QR', 'QN', 'QB', 'Q', 'K', 'KB', 'KN', 'KR']
result=[]

def export_move(model, s_row, s_column, d_row, d_column, piece, capture='', enpassant=False, promotion=0, included='', extra=''):
    """
    Returns a list containing all notations for this move.
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
        if difference and d_column-difference in range(8) and model[s_row][d_column-difference]==piece:
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
    
    if len(places) > 1:
        for row,col in places:
            if col != s_column:
                file = 'abcdefgh'[s_column]
        for row,col in places:
            if row != s_row and not file:
                rank = '87654321'[s_row]
    if piece in 'Pp' and capture:
        file = 'abcdefgh'[s_column]
    
    notations = []
        
    notations.append((piece.upper() if piece not in 'Pp' else '') +
            file +
            rank +
           ('x' if capture or enpassant else '') +
            'abcdefgh'[d_column] +
            '87654321'[d_row] +
           (promotions[promotion] if promotion else '') +
           included)
    notations.append((unicode_pieces[piece] if piece not in 'Pp' else '') +
            file +
            rank +
           ('x' if capture or enpassant else '') +
            'abcdefgh'[d_column] +
            '87654321'[d_row] +
           (unicode_pieces[promotions[promotion] if piece.isupper() else promotions[promotion].lower()] if promotion else '') +
           included)
    notations.append((piece.upper() if piece not in 'Pp' else '') +
            'abcdefgh'[s_column] +
            '87654321'[s_row] +
            ('x' if capture or enpassant else '-') +
            'abcdefgh'[d_column] +
            '87654321'[d_row] +
           (promotions[promotion] if promotion else '') +
           included)
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
           included)
    notations.append((piece.upper() if piece not in 'Pp' else '') +
             file +
             rank +
            ((':' + (capture.upper() if not enpassant else 'p' if piece=='P' else 'P')) if capture or enpassant else '') +
             'abcdefgh'[d_column] +
             '87654321'[d_row] +
            (promotions[promotion] if promotion else '') +
           included)
    notations.append('abcdefgh'[s_column] +
             '87654321'[s_row] +
             'abcdefgh'[d_column] +
             '87654321'[d_row] +
            (capture.lower() if not enpassant else 'E') +
            (promotions[promotion] if promotion else ''))
# descriptive notation - doesn't work well
#    notations.append(descriptive_files[s_column] +
#            ('87654321'[s_row] if piece.isupper() else '12345678'[s_row]) +
#            piece.upper() +
#            ('x' if capture else '-') +
#            descriptive_files[d_column] +
#            ('87654321'[d_row] if piece.isupper() else '12345678'[d_row]) +
#            (capture.upper() if not enpassant else 'P') +
#            (promotions[promotion].join('()') if promotion else '') +
#            included)
    notations.append('ABCDEFGH'[s_column] +
                  '87654321'[s_row] +
                  '-' +
                  'ABCDEFGH'[d_column] +
                  '87654321'[d_row] +
                 (promotions[promotion].join('()') if promotion else ''))
    notations.append('{}{}{}{}{}'.format(s_column+1, 8-s_row, d_column+1, 8-d_row, promotion if promotion else ''))
    notations.append(extra)
    
    return notations
    
def export_castle(move, included, extra):
    """
    Returns a list with all notations for castles, in the following order:
    SAN FAN LAN MAN RAN CRAN Smith Descriptive Coordinate ICCF
    Parameter:
        move (str): the two-character string representing the castle location
        included (str): the sort of comments that are included with moves
        extra (str): the sort of comments that are separate from moves
    """
    # descriptive is 'O-O-O'+included or 'O-O'+included
    return {'bl':['0-0-0'+included, '0-0-0'+included, '0-0-0'+included, '0-0-0', '0-0-0'+included, '0-0-0'+included, 'e8c8C', 'E8-C8', '5838', extra],
            'br':['0-0'+included, '0-0'+included, '0-0'+included, '0-0', '0-0'+included, '0-0'+included, 'e8g8c', 'E8-G8', '5878', extra],
            'wl':['0-0-0'+included, '0-0-0'+included, '0-0-0'+included, '0-0-0', '0-0-0'+included, '0-0-0'+included, 'e1c1C', 'E1-C1', '5131', extra],
            'wr':['0-0'+included, '0-0'+included, '0-0'+included, '0-0', '0-0'+included, '0-0'+included, 'e1g1c', 'E1-G1', '5171', extra]}[move]
            # san, fan, lan, man, ran, cran, smith, descriptive REMOVED, coordinate, iccf, extra comments
    
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

def chess11_to_iccf_full(moves):
    """
    Returns a list of moves in ICCF notation, converted from the given chess11 moves.
    Parameter:
        moves (list): a list of moves in chess11 notation
    """
    return list(map(chess11_to_iccf_move, moves))

def chess11_to_iccf_move(move):
    """
    Returns a move in ICCF notation, converted from the given chess11 move.
    Parameter:
        move (str): a move in chess11 notation
    """
    return '{}{}{}{}{}'.format(int(move[0])+1, 8-int(move[1]), int(move[2])+1, 8-int(move[3]), move[4:5]) if len(move)>2 else chess11_to_iccf_castles[move]

# for full iccf to chess11 moves, use return value from do_move

def iccf_to_chess11_move(move):
    """
    Returns a move in chess11 notation, converted from the given ICCF move. No castling.
    Parameter:
        move (str): a move in ICCF notation
    """
    r = re.match(r'([1-8]{4})([0-4]?)([+=#-]*)\s*(.*)', move)
    a,b,c,d = r.group(1)
    return '{}{}{}{}{}'.format(int(a)-1, 8-int(b), int(c)-1, 8-int(d), r.group(2) or '')

def iccf_to_model_move(move):
    '''
    Accepts a move in ICCF format and returns a model-friendly source row, source column,
    destination row, destination column, and pawn promotion value (or 0 if no promotion).
    The promotion value is 0:nothing, 1:queen, 2:rook, 3:bishop, 4:knight.
    '''
    r = re.match(r'([1-8]{4})([0-4]?)([+=#-]*)\s*(.*)', move)
    a,b,c,d = map(int, r.group(1))
    if r.group(2):
        promote = int(r.group(2))
    else:
        promote = 0
    included = r.group(3) or ''
    extra = r.group(4) or ''
    return 8-b, a-1, 8-d, c-1, promote, included, extra
    
def do_move(move):
    '''
    Accepts a move in ICCF format and carries it out on the model.
    Castling:
    ICCF   model
    5131 > 74720
    5171 > 74760
    5838 > 04020
    5878 > 04060
    
    Returns the appropriate chess11 move.
    '''
    chess11_move = iccf_to_chess11_move(move)
    move = iccf_to_model_move(move)
    src_row, src_col, dst_row, dst_col, promo, included, extra = move
    castling = False
    piece = model[src_row][src_col]
    if model[7][4]=='K':
        if move[:4]==(7,4,7,2):
            castling = True
            result.append(export_castle('wl', included, extra))
            model[7][3] = 'R'
            model[7][0] = ' '
            chess11_move = 'wl'
        elif move[:4]==(7,4,7,6):
            castling = True
            result.append(export_castle('wr', included, extra))
            model[7][5] = 'R'
            model[7][7] = ' '
            chess11_move = 'wr'
    if model[0][4]=='k':
        if move[:4]==(0,4,0,2):
            castling = True
            result.append(export_castle('bl', included, extra))
            model[0][3] = 'r'
            model[0][0] = ' '
            chess11_move = 'bl'
        elif move[:4]==(0,4,0,6):
            castling = True
            result.append(export_castle('br', included, extra))
            model[0][5] = 'r'
            model[0][7] = ' '
            chess11_move = 'br'
    if src_col != dst_col and model[dst_row][dst_col] == ' ' and piece in 'Pp':
        enpassant = True
    else:
        enpassant = False
    if not castling:
        result.append(export_move(model, src_row, src_col, dst_row, dst_col, piece, model[dst_row][dst_col].strip(), enpassant, promo, included, extra))
    if promo: # if a promotion is indicated, do so
        piece = promotions[promo] if piece.isupper() else promotions[promo].lower()
    if enpassant: # for en passant
        if piece=='P': # white pawn
            model[dst_row+1][dst_col] = ' ' # blank out lower square
        else: # black pawn
            model[dst_row-1][dst_col] = ' ' # blank out upper square
    model[dst_row][dst_col] = piece # move the piece
    model[src_row][src_col] = ' ' # blank out the source square
    return chess11_move

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
        except UnicodeEncodeError: # redirect to file from cmd.exe
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
            except UnicodeEncodeError: # printing directly to cmd.exe or powershell.exe
                icons = False
                print(lineend.join(' '.join(row).join('║║') for row in model), end=lineend)
            else: # all characters work
                icons = True
            finally:
                print(('═'*15).join('╚╝') + lineend, end=lineend)
    else:
        showboard = False
        lineend = '\n'

    while 1:
        try:
            user_in = input()
        except EOFError:
            break
        if not user_in:
            break
        else:
            _ = do_move(user_in)
            if showboard:
                print(get_board(icons=icons, end=lineend), end=lineend)

    if argvs.get('notations', '0').lower() not in ('off', '0', 'no'):
        if argvs.get('board', '0').lower() in ('off', '0', 'no'):
            try:
                print('╚\r', end='')
            except UnicodeEncodeError:
                sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
                lineend='\r\n'
        # removed descriptive from between smith and coord
        result = [['SAN', 'FAN', 'LAN', 'MAN', 'RAN', 'CRAN', 'Smith', 'Coord', 'ICCF', 'Comments']] + result
        align = argvs.get('align')
        if align:
            widths = [max(map(len, column))+(int(align) if align.isdigit() else 2) for column in itertools.zip_longest(*result, fillvalue='')]
            delimiter = ''
        else:
            widths = [0 for i in range(len(result[0]))]
            delimiter = '\t'
        for line in result:
            try:
                print(delimiter.join(item.ljust(widths[idx]) for idx,item in enumerate(line)).strip(' '), end=lineend)
            except UnicodeEncodeError:
                print(line[0].ljust(widths[0]), ''.ljust(widths[1]), *(item.ljust(widths[idx+2]) if idx<(len(result[0])-2) else item.strip() for idx,item in enumerate(line[2:])), sep=delimiter, end=lineend)