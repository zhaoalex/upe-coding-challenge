#!/usr/bin/python3
import requests
import sys

url = 'http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com'
# stores the offset values for moving in a given direction
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

token_param = {}
game = {}

def start_challenge():
    global token_param

    # get our token
    form_data = {'uid': '904907409'}
    token_param = requests.post(url + '/session', data=form_data).json()
    print("Obtained token: {}".format(token_param['token']))

    # begin playing games and NEVER STOP until we finish
    while True:
        if update_game_info(): # will also check for completeness
            print("Completed all levels. Challenge complete!")
            return

        # set up 2D maze matrix (start w/ all False for unvisited)
        maze = [[False for x in range(game['maze_size'][0])] for y in range(game['maze_size'][1])]
        play_level(maze, game['current_location'][0], game['current_location'][1])

        print("Level complete!")

# returns True if challenge is finished, False if not
# we only need to check this at the start of each new level
def update_game_info():
    global game

    game = requests.get(url + '/game', params=token_param).json()

    # check status
    if game['status'] == 'NONE':
        print("Status is NONE, i.e. session has expired or does not exist")
        sys.exit(1)
    elif game['status'] == 'GAME_OVER':
        print("Status is GAME_OVER, i.e. we lost :(")
        sys.exit(1)
    elif game['status'] == 'FINISHED':
        return True
    
    print("Completed {levels_completed}/{total_levels} levels. " \
        "New level: size {maze_size}, starting at {current_location}.".format(**game))

    return False

# our matrix will be: False for unvisited, True for visited (or wall)
# note: format will be maze[y][x] because that's the given format
def play_level(maze, x, y):
    # try to move in every direction
    for direction, offset in direcs.items():
        newX = x + offset[0]
        newY = y + offset[1]
        # only move to new loc if it's valid
        if is_valid(maze, newX, newY):
            result = move(direction)
            # we shouldn't have an OUT_OF_BOUNDS case here since we checked validity
            if result == 'END':
                return True
            elif result == 'WALL':
                maze[newY][newX] = True # a wall is marked as True as well
            elif result == 'SUCCESS':
                maze[newY][newX] = True
                # try and keep going; if we returned True at any point, we solved the maze!
                if play_level(maze, newX, newY):
                    return True
                # otherwise, we backtrack
                move(backtrack[direction])
        
    # we haven't solved the maze after checking every direc, so return false
    return False

# returns True if current loc is valid (in bounds and unvisited)
def is_valid(maze, x, y):
    return x >= 0 and x < game['maze_size'][0] and y >= 0 and y < game['maze_size'][1] and not maze[y][x]

# moves us and returns the result of our move
def move(direction):
    form_data = {'action': direction}
    res = requests.post(url + '/game', data=form_data, params=token_param).json()
    return res['result']

# start the challenge :)
if __name__ == "__main__":
    start_challenge()
