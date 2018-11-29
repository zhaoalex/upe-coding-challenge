import requests
import sys

url = 'http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com'
direcs = {
    'UP': (0, -1),
    'LEFT': (-1, 0),
    'DOWN': (0, 1),
    'RIGHT': (1, 0)
}
backtrack = {
    'UP': 'DOWN',
    'LEFT': 'RIGHT',
    'DOWN': 'UP',
    'RIGHT': 'LEFT'
}

class Challenge:
    def __init__(self):
        self.token_param = {}
        self.game = {}
    
    # start the challenge
    def start_challenge(self):
        # get our token
        form_data = {'uid': '904907409'}
        self.token_param = requests.post(url + '/session', data=form_data).json()

        print("Obtained token: {}".format(self.token_param['token']))

        # begin playing games
        is_finished = False
        while True:
            is_finished = self.get_game_info()
            if is_finished:
                print("Challenge complete!")
                return

            # set up maze matrix
            maze = [[False for x in range(self.game['maze_size'][0])] for y in range(self.game['maze_size'][1])]
            self.play_level(maze, self.game['current_location'][0], self.game['current_location'][1])

            print("Level complete!")

    # returns True if challenge is finished, False if not
    # we only need to check this at the start of each new level
    def get_game_info(self):
        self.game = requests.get(url + '/game', params=self.token_param).json()

        # check status
        if self.game['status'] == 'NONE':
            print("Status is NONE, aka session has expired or does not exist")
            sys.exit(1)
        elif self.game['status'] == 'GAME_OVER':
            print("Status is GAME_OVER, aka we lost :(")
            sys.exit(1)
        elif self.game['status'] == 'FINISHED':
            return True
        
        print("Completed {levels_completed}/{total_levels} levels. " \
            "New level: size {maze_size}, starting at {current_location}.".format(**self.game))

        return False

    # our matrix will be: False for unvisited, True for visited (or wall)
    # note: format will be maze[y][x] because that's the internal format
    def play_level(self, maze, x, y):
        # print("({0}, {1}): {2}".format(x, y, maze[y][x]))
        # self.get_game_info() # wastes a lot of time on needless network calls: for debugging only
        
        # try to move in every direction
        for direction, offset in direcs.items():
            newX = x + offset[0]
            newY = y + offset[1]
            # only move to new loc if it's valid
            if self.is_valid(maze, newX, newY):
                result = self.move(direction)
                # we shouldn't have an OUT_OF_BOUNDS case here
                # but even if we do, it keeps us in the same location so we should be good
                if result == 'END':
                    return True
                elif result == 'WALL':
                    maze[newY][newX] = True # a wall is marked as True as well!
                elif result == 'SUCCESS':
                    maze[newY][newX] = True
                    # try and keep going; if we returned True at any point, we already solved the maze!
                    if self.play_level(maze, newX, newY):
                        return True
                    # otherwise, we backtrack
                    self.move(backtrack[direction])
            
        # visited locations return False!
        return False

    # returns True if current loc is valid (in bounds and unvisited)
    def is_valid(self, maze, x, y):
        return x >= 0 and x < self.game['maze_size'][0] and y >= 0 and y < self.game['maze_size'][1] and not maze[y][x]

    # moves us and returns the result of our move
    def move(self, direction):
        form_data = {'action': direction}
        res = requests.post(url + '/game', data=form_data, params=self.token_param).json()
        return res['result']

# start the challenge :)
if __name__ == "__main__":
    c = Challenge()
    c.start_challenge()
