import math
import random
from parse import parse
from itertools import combinations,permutations
import itertools

ORIENTATION_ORDER = [(-1,0),(0,1),(1,0),(0,-1)]

# Preparing the game,
# - Shuffled, 24,36, or 48 Dominoes, from file
# - Players, 2,3, or 4, with some kings -> (not really needed?)
# - Kingdoms for each player, 1-2, (definitely)
# - a Game, some mechanism to dictate the game, king is K

# Playing the game
# - Begin with a set of 3-4 dominoes for each round
# - For each Kingdom:
#   - Choose from the set
#   - Place domino, unless there is no valid space
# - Game ends when there are no more dominoes left

# Load the Dominoes
def load_dominoes(filename):
    res = []
    with open(filename,'r') as f:
        textlines = f.readlines()
        for line in textlines:
            res.append(Domino(line))
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

def get_valid_placements(kingdom,domino):
    # Returns an array of dictionaries containing kingdom locations, with 
    # orientations
    # Possible orientations are represented by
    #  0   Where 0 is up, 1 is right, 2 is down, 3 is left
    # 3W1  
    #  2   
    #  ie. if orientation 0 is chosen, for the 2nd chunk, on a domino WF:
    #     W
    #   ->F<- with F at the location chosen
    result = []
    relative_size = kingdom.get_true_size()
    valid_locations = kingdom.get_valid_locations()
    for x,y,adjacents in valid_locations:
        # adjacents represents the surrounding chunks in ORIENTATION_ORDER
        # x,y is the location of the spot
        orientations = []
        # add orientations
        for i,adj in enumerate(adjacents):
            c1,c2 = i,i+4
            if adj is None:
                if domino.land1 in adjacents or 'K' in adjacents:
                    orientations.append(c1)
                if domino.land2 in adjacents or 'K' in adjacents:
                    orientations.append(c2)
        result.append( (x,y,sorted(orientations)) )
    return result

class Domino(object):
    def __init__(self,domino_str):
        self.index = None 
        self.crowns = 0 
        self.land1 = None 
        self.land2 = None 

        r = parse("{index}:{land1}+{land2}({crowns})",domino_str)
        if r is None:
            r = parse("{index}:{land1}+{land2}",domino_str)
        if r is not None:
            for key,value in r.named.items():
                self.__setattr__(key,value)
    def __str__(self):
        return "{}:{}+{}({})".format(self.index,self.land1,self.land2,self.crowns)
    def get_chunks(self):
        return (Chunk(self.land1,0),Chunk(self.land2,self.crowns))

class Chunk(object):
    def __init__(self,land_type,crowns):
        self.land_type = land_type[0]
        self.land_name = land_type
        self.crowns = crowns
    def __str__(self):
        return self.land_type+str(self.crowns)

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
        """Returns the name of this kingdom"""
        return self.color+" Kingdom"
    def get_valid_locations(self):
        """Determines all empty adjacent chunk locations on the domino map, returns list of (row,col) points"""
        res = []
        for i,row in enumerate(self.map):
            for j,chunk in enumerate(row):
                if chunk is None: # No chunk in this spot
                    # needs one adjacent chunk and one empty spot
                    adjacents = 0
                    adjacent_names = [None]*4
                    for f,(x,y) in enumerate(ORIENTATION_ORDER):
                        try:
                            if self.map[i+x][j+y] != None:
                                adjacents+=1
                                adjacent_names[f] = (self.map[i+x][j+y].land_type)
                        except Exception as e:
                            pass
                    if adjacents>0 and adjacents<4:
                        res.append((i,j,adjacent_names))
        return res
    def get_true_size(self):
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

    def to_ascii(self):
        return " \n".join([ (" ".join(map(lambda x: "--" if x is None else str(x),row))) for row in self.map ])+"\n\n"

class GAME_STATE(object):
    PICK_DOMINO,PLACE_DOMINO,DONE_TURN,DONE_GAME = range(4)

class Game(object):
    def init_players(self,num_players):
        # num_players will be between 2 and 4, no more no less
        num_players = 2 if num_players<2 else int(num_players)
        self.num_players = 4 if num_players>4 else num_players
        self.curr_player = 1 # starts at ONE, 1 2 3 4
        self.round_num = 1
    def init_dominoes(self,filename):
        dominoes = load_dominoes(filename)
        dominoes = shuffle_dominoes(dominoes)
        dominoes = cut_dominoes(dominoes,self.num_players)
        self.dominoes = dominoes
        self.pickable_dominoes = []
    def init_kingdoms(self, colors):
        # 3 kingdoms if 3 players, 4 for 2 or 4
        if not ((len(colors)==3 or len(colors)==4) and len(colors)%2==self.num_players%2 ):
            raise ValueError('Incorrect number of colors for this game')
        if not (all(map(lambda x:type(x)==str,colors)) and len(colors)==len(set(colors)) ):
            raise ValueError('Not all colors are unique strings')
        if self.num_players==3 or self.num_players==4:
            self.kingdoms = [ Kingdom(i+1,k) for i,k in enumerate(colors) ]
        elif self.num_players==2:
            self.kingdoms = [ Kingdom(i%2+1,k) for i,k in enumerate(colors) ]
    def init_game_state(self):
        self.state = GAME_STATE.PICK_DOMINO
        
    def ascii_game_state(self):
        res =  ""
        res += "King Domino - {} players, Player {}'s turn \n".format(self.num_players,self.curr_player)
        res += " ".join(map(str,self.pickable_dominoes)) + "\n\n"
        for kingdom in self.kingdoms:
            res += "{} for Player {}".format(kingdom.display_name(),kingdom.player_num) +"\n"
            res += kingdom.to_ascii()
        return res
    
    
    def set_pickable_dominoes(self):
        num_pickables = len(self.kingdoms)
        if len(self.pickable_dominoes)==0:
            self.pickable_dominoes = sorted(self.dominoes[:num_pickables], key=lambda x:int(x.index) )
            self.dominoes = self.dominoes[num_pickables:]
    def pick_domino(self,index):
        if index<len(self.pickable_dominoes) and self.state==GAME_STATE.PICK_DOMINO:
            self.state==GAME_STATE.PLACE_DOMINO
            self.curr_domino = self.pickable_dominoes.pop(index)
            return self.curr_domino
    def place_curr_domino(self,index):
        if self.curr_domino is not None and self.state==GAME_STATE.PICK_DOMINO:
            self.state==GAME_STATE.DONE_TURN
            # TODO: Must implement from here


    def next_player_num(self):
        return (self.curr_player)%self.num_players+1
    def get_curr_player(self):
        return self.curr_player
    
def run_test():
    game = Game()
    game.init_players(2)
    game.init_kingdoms(['Blue','Purple','Red','Green'])
    game.init_game_state()
    game.init_dominoes('test_dominoes.txt')

    # print map(str, sorted(game.dominoes[:4], key=(lambda x:int(x.index))) )
    game.set_pickable_dominoes()
    print game.ascii_game_state()
    print game.kingdoms[0].get_valid_locations()
    print get_valid_placements(game.kingdoms[0],Domino('12:W+F(3)'))

if __name__=='__main__':
    game = Game()
    run_test()