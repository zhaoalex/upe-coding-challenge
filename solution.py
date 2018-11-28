import requests
import sys
from collections import namedtuple

url = 'http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com'
Node = namedtuple("Node", "x y dir")

class Challenge:
    def __init__(self):
        self.token_param = None
        self.game = None # holds info about current game
    
    def start_challenge(self):
        # get our token
        form_data = {'uid': '904907409'}
        r = requests.post(url + '/session', data=form_data)
        self.token_param = r.json()

        print("Obtained token: " + self.token_param['token'])

        # begin playing games
        is_finished = False
        while True:
            is_finished = self.get_game_info()
            if is_finished == True:
                print("Challenge complete!")
                sys.exit(0)
            
            # set up maze matrix
            maze = [[0 for x in range(self.game['maze_size'][0])] for y in range(self.game['maze_size'][1])]
            self.play_level(self.game['current_location'][0], self.game['current_location'][1], self.game['maze_size'][0], self.game['maze_size'][1], maze)

    # returns True if challenge is finished, False if not
    # we'll only check this at the start of each new level
    def get_game_info(self):
        r = requests.get(url + '/game', params=self.token_param)
        self.game = r.json()

        print(self.game)

        # check status
        if self.game['status'] == 'NONE':
            print("Status is NONE, aka session has expired or does not exist")
            sys.exit(1)
        elif self.game['status'] == 'GAME_OVER':
            print("Status is GAME_OVER, aka we went out of bounds")
            sys.exit(1)
        elif self.game['status'] == 'FINISHED':
            return True
        
        return False


    # our matrix will be: 0 for unvisited, 1 for visited
    # we have a stack of "nodes" (x, y, dir)
    def play_level(self, x, y, maze_width, maze_height, maze):
        print("Starting level")
        x = self.game['current_location'][0]
        y = self.game['current_location'][1]
        stack = []
        stack.append((x, y, 0))

        # i.e. while stack isn't empty
        while not stack:
            








    
    # direction is UP, DOWN, LEFT, or RIGHT
    def move(self, direction):
        form_data = {'action': direction}
        r = requests.post(url + '/game', data=form_data, params=self.token_param)
        res = r.json()

        # if res['result'] == 'OUT_OF_BOUNDS':




# start the challenge
c = Challenge()
c.start_challenge()
