unicode_pieces = {' ':' ', 'r':'♜', 'n':'♞', 'b':'♝', 'q':'♕', 'k':'♚', 'p':'♟', 'R':'♖', 'N':'♘', 'B':'♗', 'Q':'♛', 'K':'♔', 'P':'♙'}
chess9_to_iccf_castles = {'wl':'5131', 'wr':'5171', 'bl':'5838', 'br':'5878'}
promotions = 'PQRBN'

def export_move(model, s_row, s_column, d_row, d_column, piece):
    if self.piece in 'Pp': # only needs disambiguation on captures, including en passant
        pass
    elif self.piece in 'Nn':
        pass
    elif self.piece in 'Kk':
        pass
    else:
        if self.piece in 'BbQq':
            pass
        elif self.piece in 'RrQq':
            pass
    
    
    def to_SAN(self):
        pass
        
    def to_FAN(self):
        pass
    
    def to_LAN(self):
        pass
    
    def to_MAN(self):
        pass
    
    def to_RAN(self):
        pass
    
    def to_CRAN(self):
        pass
    
def export_castle(move):
    pass

def new_game():
    return [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
       ['p' for i in range(8)],
       [' ' for i in range(8)],
       [' ' for i in range(8)],
       [' ' for i in range(8)],
       [' ' for i in range(8)],
       ['P' for i in range(8)],
       ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']]

def chess9_to_iccf_full(moves):
    return [chess9_to_iccf_move(move) if len(move)==4 else chess9_to_iccf_castles[move] for move in moves]

# no iccf_to_chess9_full yet because castle indicators require knowledge of the game board

def chess9_to_iccf_move(move):
    return '{}{}{}{}'.format(int(move[0])+1, 8-int(move[1]), int(move[2])+1, 8-int(move[3]))

def iccf_to_chess9_move(move):
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
    if model[7][4]=='K':
        if move==(7,4,7,2,0):
            model[7][3] = 'R'
            model[7][0] = ' '
            # export notations to result here
        elif move==(7,4,7,6,0):
            model[7][5] = 'R'
            model[7][7] = ' '
    elif model[0][4]=='k':
        if move==(0,4,0,2,0):
            model[0][3] = 'r'
            model[0][0] = ' '
        elif move==(0,4,0,6,0):
            model[0][5] = 'r'
            model[0][7] = ' '
    piece = model[src_row][src_col]
    if promo: # if a promotion is indicated, do so
        piece = promotions[promo] if piece.isupper() else promotions[promo].lower()
    if src_col != dst_col and model[dst_row][dst_col] == ' ': # for en passant
        if piece=='P': # white pawn
            model[dst_row+1][dst_col] = ' ' # blank out lower square
        if piece=='p': # black pawn
            model[dst_row-1][dst_col] = ' ' # blank out upper square
    model[dst_row][dst_col] = piece # move the piece
    model[src_row][src_col] = ' ' # blank out the source square
    # export notations to result here


def print_board(name=None, icons=False):
    representation = (
                     ('═'*15).join('╔╗') + '\n' +
                     '\n'.join(' '.join(row if not icons else (unicode_pieces[item] for item in row)).join('║║') for row in model) +
                     '\n' + ('═'*15).join('╚╝') + '\n'
                     )
    if name:
        with open(name, 'a', encoding='utf-8') as output:
            output.write(representation + '\n')
    else:
        print(representation)


result=[]


    
'''
if __name__ == '__main__':
    result.append(input()[-4:])
    while 1:
        try:
            a = input()
        except EOFError:
            break
        else:
            if a:
                result.append(a)
            else:
                break'''

'''
186 ║
187 ╗
188 ╝
200 ╚
201 ╔
205 ═
'''


#m = ['6775', '1112', '7563', '2011', 'wl', 'wr', 'bl', 'br']
#print(*chess9_to_iccf(m), sep='\n')
model = new_game() # populate the model as a new game
while 1:
    try:
        user_in = input()
    except EOFError:
        break
    if not user_in:
        break
    else:
        do_move(user_in)
        print_board()

'''
import chess_notation as cn
just translate every chess9 move to iccf
change step_forward to ### if do_move == "5838" and not black_king.moved: # if it's 'bl', ### etc. for castling
change step_forward to add ### do_move = cn.iccf_to_chess9_move(do_move) # switch to internal format ### for regular move
'''