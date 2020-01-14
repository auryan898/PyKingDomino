import math
import random
from parse import parse
from itertools import combinations,permutations
import itertools

ORIENTATION_ORDER = [(-1,0),(0,1),(1,0),(0,-1)]
DOMINO_ORIENTATIONS = "1st-up 1st-right 1st-down 1st-left 2nd-up 2nd-right 2nd-down 2nd-left".split(" ")

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
        if orientations:
            result.append( (x,y,sorted(orientations)) )
    return result

def valid_input(func,question):
    choice = None
    while choice is None:
        choice = raw_input(question)
        if not func(choice):
            print "That wasn't a valid choice"
            choice=None
    return choice

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
        self.crowns = int(self.crowns)
    def __str__(self):
        return "{}:{}+{}({})".format(self.index,self.land1,self.land2,self.crowns)
    def get_chunks(self):
        return (Chunk(self.land1,0),Chunk(self.land2,self.crowns))

class Chunk(object):
    def __init__(self,land_type,crowns=0):
        self.land_type = land_type[0]
        self.land_name = land_type
        self.crowns = int(crowns)
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
        self.old_domino = None
    def display_name(self):
        """Returns the name of this kingdom"""
        return self.color+" Kingdom"
    def get_valid_locations(self):
        """Determines all empty adjacent chunk locations on the domino map, returns list of (row,col) points"""
        res = []
        top,right,bottom,left = self.get_true_size()
        height,width = bottom-top+1 , right-left+1 # the true height and width
        if height>5 or width>5 or height<1 or width<1:
            raise RuntimeError("Invalid height and width of kingdom, this game is broken")
        r_height, r_width = 5-height, 5-width # remaining space in each direction
        limits = ( top-r_height, right+r_width, bottom+r_height, left-r_width )
        if limits[0]<0 or limits[3]<0 or limits[1]>8 or limits[2]>8:
            raise RuntimeError("Invalid size limits of kingdom, this game is broken: {}\n{}".format(zip(limits,['top','right','bottom','left']),self.to_ascii()))
        # print top,right,bottom,left
        for i,row in enumerate(self.map):
            for j,chunk in enumerate(row):
                if chunk is None: # No chunk in this spot
                    # needs one adjacent chunk and one empty spot
                    adjacents = 0
                    adjacent_names = [None]*4
                    for f,(x,y) in enumerate(ORIENTATION_ORDER):
                        x1,y1 = i+x, j+y
                        if y1>limits[1] or y1<limits[3] or x1>limits[2] or x1<limits[0]:
                            adjacents+=1
                            adjacent_names[f] = ('XX')
                            # print x1,y1
                            # pass
                        elif self.map[i+x][j+y] != None:
                            adjacents+=1
                            adjacent_names[f] = (self.map[i+x][j+y].land_type)
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
            bottom = i if any(row) else bottom
            for j,chunk in enumerate(row):
                # keep the first chunk, move left if there's a chunk further left
                left = j if (left is None or j<left) and chunk is not None else left 
                
                # keep moving to the right if it's there
                right = j if chunk is not None and j>right else right 
        
        # for one castle, the indices are the same, with size (1,1)
        # for three x three castles, the indices are 0 _ 2, the difference is 2, with size 3
        # always add an extra 1
        return (top,right,bottom,left)
    def get_curr_placements(self):
        return get_valid_placements(self,self.old_domino)
    def place_old_domino(self,placements,location_i,orientation_i):
        """updates the map with old_domino in its placement and nulls old_domino"""
        x,y,orientations = placements[location_i]
        orientation = orientations[orientation_i]
        chunk1,chunk2 = self.old_domino.get_chunks()

        if orientation>=4: 
            chunk1,chunk2 = chunk1,chunk2 # Swap chunks if higher orientation
            orientation-=4 # adjust orientation appropriately
        off_x,off_y = ORIENTATION_ORDER[orientation]
        if self.map[x][y] is not None or self.map[x+off_x][y+off_y] is not None:
            raise RuntimeError("Your game is broken, fix Kingdom.place_old_domino or 'placements' logic")
        self.map[x][y] = chunk1
        self.map[x+off_x][y+off_y] = chunk2
        self.old_domino = None
    def get_stats(self):
        sum_crowns = 0
        sum_tiles = 0
        # Discover chunks of the same type that are adjacent to each other, 
        # there could be a few of these separate regions
        res = [] # Contains lists of chunks belonging to the same 'region'
        copy_map = [ [ chunk for chunk in row ] for row in self.map ]
        for i,row in enumerate(copy_map):
            for j,chunk in enumerate(row):
                if chunk is not None:
                    # print str(chunk)
                    adjacents = [] # get the adjacent matching chunks' locations centered around (i,j)
                    for x,y in ORIENTATION_ORDER:
                        try:
                            if copy_map[i+x][j+y] is not None and copy_map[i+x][j+y].land_type==chunk.land_type:
                                adjacents.append((i+x,j+y,copy_map[i+x][j+y].crowns)) # If matching adjacent
                                # print "matched adjacent {}".format((i+x,j+y,copy_map[i+x][j+y].crowns)) # DEBUG
                                
                        except Exception as e:
                            pass
                    adjacents.append((i,j,chunk.crowns)) # adjacents contains all chunks
                    # print adjacents
                    for r_index, region in enumerate(res):
                        if any(map(lambda x: x in region,adjacents)): # if any adjacent in region
                            # print "Matched Adjacent to Region"
                            res[r_index] = list(set(region+adjacents)) # add adjacents to this region
                            adjacents = None
                            break
                    if adjacents is not None: # This is a unique chunk
                        # print "Found Unique Chunk"
                        res.append(adjacents)
        #---
        # Iterate over the res and calculate the crowns x tiles to be added to the sum
        # print res
        for region in res:
            crowns = sum(map(lambda (x,y,c):int(c),region))
            sum_crowns += crowns*len(region) # the crowns x tiles
            sum_tiles  += len(region)
        return sum_crowns,sum_tiles

    def to_ascii(self):
        res = "   "+" ".join([ " {}".format(i) for i in range(9) ])+"\n"
        res+=" \n".join([ " {} ".format(i)+(" ".join(map(lambda x: "--" if x is None else str(x),row))) for i,row in enumerate(self.map) ])+"\n\n"
        return res

class GAME_STATE(object):
    PICK_DOMINO,PLACE_DOMINO,DONE_TURN,DONE_GAME = range(4)

class Game(object):
    def init_players(self,num_players):
        # num_players will be between 2 and 4, no more no less
        num_players = 2 if num_players<2 else int(num_players)
        self.num_players = 4 if num_players>4 else num_players
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
        res += "King Domino - {} players \n".format(self.num_players)
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
    def pick_domino(self,kingdom,index):
        if index<len(self.pickable_dominoes):
            self.state=GAME_STATE.PLACE_DOMINO
            kingdom.old_domino = self.pickable_dominoes.pop(index)

    def get_winners(self):
        res = []
        crowns,tiles = 0,0
        for kingdom in self.kingdoms:
            c,t = kingdom.get_stats()
            if c>crowns or (c==crowns and t>tiles):
                crowns,tiles = c,t
        
        # add up the tied kingdoms
        for kingdom in self.kingdoms:
            c,t = kingdom.get_stats()
            if c==crowns and t==tiles:
                res.append(kingdom)
        return res
    def get_pickable_options(self):
        return enumerate(self.pickable_dominoes)
    
    def ascii_run(self):
        self.init_players(int(raw_input("how many players? ")))
        num_p = self.num_players
        print ""
        colors = []
        for i in range(3 if num_p==3 else 4):
            ind = i%2 if num_p==2 else i
            colors.append( valid_input(lambda x: type(x)==str,"Which color of kingdom {} for Player {}? ".format(i+1, ind+1)) )
        print ""
        self.init_kingdoms(colors)
        self.init_game_state()
        self.init_dominoes('test_dominoes.txt') # TODO: choose better dominoes file?
        
        print "King Domino!!! \nBegin the game!\n"
        playable = True
        while playable: # TODO: You gotta do one more round of placements for the end
            # each iteration is a round of gameplay
            print "ROUND {}".format(self.round_num)
            print "Grabbing a new set of dominoes for gameplay...\n"
            self.set_pickable_dominoes()
            
            for kingdom in (self.kingdoms):

                print "{}: Player {}'s turn".format(kingdom.display_name(),kingdom.player_num)

                if kingdom.old_domino is not None and type(kingdom.old_domino)==Domino: # This won't run the first time around
                    placements = kingdom.get_curr_placements()  
                    print "First, you place your old domino somewhere {}".format(str(kingdom.old_domino))
                    print "This is your board: \n"+kingdom.to_ascii() # TODO: show the possible placements on board
                    if len(placements)==0: 
                        print "But you have no possible placements for this domino piece \n So you lose this piece."
                    else:
                        print "The dominoes you will choose from are:"
                        print " | ".join([ "[{}] {}+{}({})".format(i, d.land1, d.land2, d.crowns) for i,d in enumerate(self.pickable_dominoes) ]) + "\n"
                        print "Possible placement locations include: \n"+ ", ".join([ "[{}] ({},{})".format(i,x,y) for i,(x,y,o) in enumerate(placements) ])
                        print ""
                        choice1 = valid_input(lambda x: x.isdigit() and int(x)<len(placements) and int(x)>=0,"Which do you choose? " )
                        choice1 = int(choice1)

                        print "Now you must choose an orientation of this domino"
                        print "Choose the domino's direction to point toward for either the 1st half, or 2nd half (which has the crowns)" # TODO: create ascii diagram of orientation explanation
                        print ""
                        print "Possible orientations include: \n"+ ", ".join([ "[{}] ({})".format(i,DOMINO_ORIENTATIONS[o]) for i,o in enumerate(placements[choice1][2]) ]) # TODO: make a better orientation options display
                        
                        choice2 = valid_input(lambda x: x.isdigit() and int(x)<len(placements[choice1][2]) and int(x)>=0,"Which do you choose? " )
                        choice2 = int(choice2)

                        kingdom.place_old_domino(placements,choice1,choice2)
                    kingdom.old_domino = None
                    print ""
                    print "This is now your board: \n"+kingdom.to_ascii() # TODO: just make a better ascii board

                options = self.pickable_dominoes               
                if len(options)>0:
                    print "Now you choose a new domino."
                    print "The dominoes you can choose from are:"
                    print " | ".join([ "[{}] {}+{}({})".format(i, d.land1, d.land2, d.crowns) for i,d in enumerate(options) ]) + "\n"
                    
                    choice = valid_input(lambda x : x.isdigit() and int(x)>=0 and int(x)<len(options),"Which do you choose? ")
                    # print ""
                    self.pick_domino(kingdom,int(choice)) 
                    print "You chose "+str(kingdom.old_domino)+"\n\n"
                else:
                    playable=False
            self.round_num+=1
        print "Now the game has ended!!!\n We now decide upon the winner."
        kingdoms = self.get_winners()
        for kingdom in self.kingdoms:
            c,t = kingdom.get_stats()
            print "The {}, ruled by Player {} has {} crowns and {} tiles.".format(kingdom.display_name(),kingdom.player_num,c,t)
            print kingdom.to_ascii()
            print ""
        if len(kingdoms)==1:
            kingdom = kingdoms[0]
            crowns,tiles = kingdom.get_stats()
            win_message = "The greatest kingdom is the {}, so Player {} wins with {} crowns, and {} tiles!"
            print win_message.format(kingdom.display_name(),kingdom.player_num,crowns,tiles)
        if len(kingdoms)>1:
            print "AMAZINGGG!!!!!! We have multiple winners!!!!"
            print "The Greatest Kingdoms of the land are:"
            win_message = "The {}, belonging to Player {}, tieing with {} crowns, and {} tiles!"
            for kingdom in kingdoms:
                crowns,tiles = kingdom.get_stats()
                print win_message.format(kingdom.display_name(),kingdom.player_num,crowns,tiles)
        print "Good show old sport. :)"

def run_test():
    game = Game()
    game.init_players(2)
    game.init_kingdoms(['Blue','Purple','Red','Green'])
    game.init_game_state()
    game.init_dominoes('test_dominoes.txt')

    # print map(str, sorted(game.dominoes[:4], key=(lambda x:int(x.index))) )
    game.set_pickable_dominoes()
    game.kingdoms[0].map[4][5] = Chunk('A',0)
    game.kingdoms[0].map[4][6] = Chunk('W',3)
    # print game.ascii_game_state()


    # print game.kingdoms[0].get_valid_locations()
    # print get_valid_placements(game.kingdoms[0],Domino('12:W+F(3)'))
    # print game.kingdoms[0].get_stats()
    k1 = Kingdom(3,'Gr')
    tests = {
        (2,2,'F'),
        (2,3,'W'),
        (5,1,'G'),
        (5,2,'F'),
        (3,2,'L'),
        (4,2,'G'),
        (4,3,'L'),
        (3,3,'W'),
        (3,4,'F'),
        (3,5,'L'),
        (4,4,'K'),
        (5,3,'W'),
        (5,4,'W'),
    }
    for r,c,n in tests:
        k1.map[r][c] = Chunk(n,1)
    print k1.to_ascii()
    print k1.get_true_size()
    print k1.get_stats()
if __name__=='__main__':
    # valid_input = lambda x,y:0
    game = Game()
    game.ascii_run()
    # run_test()