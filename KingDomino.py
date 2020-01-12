import math
import random
from parse import parse

# Preparing the game,
# - Shuffled, 24,36, or 48 Dominoes, from file
# - Players, 2,3, or 4, with some kings -> (not really needed?)
# - Kingdoms for each player, 1-2, (definitely)
# - a Game, some mechanism to dictate the game, king is K

# Load the Dominoes
def load_dominoes(filename):
    res = []
    with open(filename,'r') as f:
        textlines = f.readlines()
        for line in textlines:
            res+= Domino(line)
    if not all(res):
        raise ValueError("There is a domino parsing error")
    if len(res) != 48:
        raise ValueError("There is an incorrect number of dominoes in this set")
    return res
# Shuffle the Dominoes
def shuffle_dominoes(dominoes):
    random.shuffle(dominoes)
    return dominoes

# Cut the Dominoes, 12 24 48
def cut_dominoes(dominoes,players):
    if not (players>=2 and players<=4):
        raise ValueError("The number of players is inappropriate for this game")
    return dominoes[: (players)*12 ]

class Domino(object):
    def __init__(self,domino_str):
        self.index = None 
        self.crowns = None 
        self.land1 = None 
        self.land2 = None 

        r = parse("{index}:{land1}+{land2}({crowns})",domino_str)
        if r is None:
            r = parse("{index}:{land1}+{land2}",domino_str)
        if r is not None:
            for key,value in r.named.items():
                self.__setattr__(key,value)
    def getChunks(self):
        return (Chunk(self.land1,0),Chunk(self.land2,self.crowns))


class Chunk(object):
    def __init__(self,land_type,crowns):
        self.land_type = land_type[0]
        self.land_name = land_type
        self.crowns = crowns

class Kingdom(object):
    #   0
    # 3 K 1
    #   2
    #  01 
    # 5WF2
    #  43
    # 0,0 is at the top left, like a spreadsheet
    def __init__(self,player_num,color):
        self.player_num = player_num
        self.color = color
        self.map = [ x[:] for x in [[None]*9]*9 ]
        self.map[4][4] = Chunk("King's Castle",0)
    def display_name(self):
        return self.color+" Kingdom"
    def getValidPerimeter(self):
        pass
    def getTrueSize(self):
        # These values will always be something, 
        # because there is a castle
        top,bottom,left,right = [None]*4

        for i,row in enumerate(self.map):
            # Grab only one row that has something in it
            top = i if top is None and any(row) else top  
            # Just keep grabbing the next row that has something in it
            bottom = j if any(row) else bottom
            for j,chunk in enumerate(row):
                # keep the first chunk, move left if there's a chunk further left
                left = j if (left is None or j<left) and chunk is not None else left 
                
                # keep moving to the right if it's there
                right = j if chunk is not None else right 
        
        # for one castle, the indices are the same, with size (1,1)
        # for three x three castles, the indices are 0 _ 2, the difference is 2, with size 3
        # always add an extra 1
        return (bottom-top+1,right-left+1)

class GAME_STATE(object):
    PICK_DOMINO,PLACE_DOMINO,DONE_TURN,DONE_GAME = range(1)

class Game(object):
    def init_players(self,num_players):
        # num_players will be between 2 and 4, no more no less
        num_players = 2 if num_players<2 else int(num_players)
        self.num_players = 4 if num_players>4 else num_players
        self.curr_player = 1 # starts at ONE, 1 2 3 4
    def init_dominoes(self,filename):
        dominoes = load_dominoes(filename)
        dominoes = shuffle_dominoes(dominoes)
        dominoes = cut_dominoes(dominoes,self.num_players)
        self.dominoes = dominoes
    def init_kingdoms(self, colors):
        if not len(colors)==self.num_players:
            raise ValueError('Incorrect number of colors for this game')
        if not (all(map(lambda x:type(x)==str,colors)) and len(colors)==len(set(colors)) ):
            raise ValueError('Not all colors are unique strings')
        self.kingdoms = [ Kingdom(i+1,k) for i,k in enumerate(colors) ]
    def init_game_state(self):
        self.state = GAME_STATE.PICK_DOMINO
        

    def next_player_num(self):
        return (self.curr_player)%self.num_players+1
    def get_curr_player(self):
        return self.curr_player
    
def run_test():
    game = Game()
    game.init_players(2)

if __name__=='__main__':
    game = Game()
    run_test()