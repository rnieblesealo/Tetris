#Tetris by Rafa with absolutely ZERO StackOverflow ;) (And in the console! :o)

import numpy as np
import sys, os, msvcrt

from random import randint
from blocks import BLOCKS

class Block:
    pos = None
    rot = None
    bounds = None
    shape = None
    current_shape = None #current shape
    
    def __init__(self, shape, pos) -> None:
        self.pos = pos
        self.rot = 0
        self.bounds = (len(shape[0]), len(shape[0][0]))
        self.shape = shape
        self.current_shape = self.shape[self.rot]
            
    def can_move(self, grid, dir):
        for y in range(self.bounds[1]):
            for x in range(self.bounds[0]):
                #empty blocks shouldn't be considered; they're empty space anyways!
                #NOTE this function works by considering the current shape as-is on its template and comparing it to its FILLED parts on the grid
                if self.current_shape[y][x] == EMPTY:
                    continue
                
                pos_x = x + self.pos[0]
                pos_y = y + self.pos[1]

                next_x = pos_x + dir[0]
                next_y = pos_y + dir[1]
                
                #NOTE position is relative to individual blocks; NOT whole shape
                is_within_bounds = (next_x >= 0 and next_x < SIZE[0]) and (next_y >= 0 and next_y < SIZE[1])   
                
                if not is_within_bounds:
                    return False
                
                #a tile is valid if it has nothing in front of it towards dir
                is_valid_tile = ((x + dir[0] < self.bounds[0] and y + dir[1] < self.bounds[1]) and (self.current_shape[y + dir[1]][x + dir[0]] != FULL)) or (x + dir[0] == self.bounds[0] or y + dir[1] == self.bounds[1])

                if not is_valid_tile:
                    continue

                is_valid_move = grid[pos_y + dir[1]][pos_x + dir[0]] == EMPTY
                
                if not is_valid_move:
                    return False
        return True

    def can_rotate(self, grid):
        #block can be rotated if all tiles on grid match current shape (this means no tiles overlap w/rotated tile)        
        for y in range(self.bounds[1]):
            for x in range(self.bounds[0]):
                if self.current_shape[y][x] != grid[y + self.pos[1]][x + self.pos[0]]:
                    return False
        return True

    def place(self, grid):    
        #copy the current shape to the grid
        for y in range(self.bounds[1]):
            for x in range(self.bounds[0]):
                grid[y + self.pos[1]][x + self.pos[0]] = self.current_shape[y][x]

    def move(self, grid, dir):       
        if not self.can_move(grid, dir):
            return

        x_bound = self.bounds[0]
        y_bound = self.bounds[1]
        
        #adjust shape-scan bounds to cut off empty space if necessary
        if self.pos[0] + self.bounds[0] > SIZE[0] - 1:
            x_bound = SIZE[0] - self.pos[0]
        
        if self.pos[1] + self.bounds[1] > SIZE[1] - 1:
            y_bound = SIZE[1] - self.pos[1]

        #delete everything at the current position and recopies the shape to the new position
        for y in range(y_bound):
            for x in range(x_bound):
                if self.current_shape[y][x] == FULL:
                    grid[y + self.pos[1]][x + self.pos[0]] = EMPTY
        for y in range(y_bound):
            for x in range(x_bound):
                if self.current_shape[y][x] != EMPTY:
                    grid[y + self.pos[1] + dir[1]][x + self.pos[0] + dir[0]] = self.current_shape[y][x]
        
        #update position
        self.pos[0] += dir[0]
        self.pos[1] += dir[1]
    
    def rotate(self, grid):
        if not self.can_rotate(grid):
            return
        
        #clockwise rotation; copy rotated shape templates to grid
        self.rot = self.rot + 1 if self.rot + 1 < 4 else 0 #all shapes have 4 rotations
        self.current_shape = self.shape[self.rot]
        self.place(grid)

def is_row_empty(grid, y):
    for x in range(SIZE[0]):
        if grid[y][x] == FULL:
            return False
    return True

def get_full_rows(grid):
    full_rows = []
    for y in range(SIZE[1]):
        for x in range(SIZE[0]):
            if grid[y][x] != FULL:
                break
        else: #this else executes when the inner loop has completed without breaks
            full_rows.append(y)
    return full_rows

def delete_row(grid, y):
    #NOTE assuming there are no non-contiguous full rows when more than 1 is present
        for x in range(SIZE[0]):
            grid[y][x] = EMPTY
        while (not is_row_empty(grid, y - 1)) and (y - 1 > 0):
            #swap empty row w/previous (think of it as bubble sort)
            temp = grid[y].copy() #must copy as assign is by reference by default
            grid[y] = grid[y - 1]
            grid[y - 1] = temp
            
            #proceed
            y -= 1

def can_spawn_block(grid, block):
    for y in range(block.bounds[1]):
        for x in range(block.bounds[0]):
            if block.current_shape[y][x] == EMPTY:
                continue
            if grid[y + block.pos[1]][x + block.pos[0]] == FULL:
                return False
    return True

def refresh():
    os.system('cls')
    print("Score: {S}".format(S=score))
    print("Level: {L}".format(L=level))
    print("XP: {C}/10\n".format(C=cleared))
    print(grid, "\n")
    print("Next:\n{N}".format(N=next_block.shape[0]))
        
# GLOBAL DEFINITIONS ==============================================================

QUIT = 'q'
ROTATE = 'r'
LEFT = 'a'
RIGHT = 'd'
DOWN = 's'

FULL = '□' #filled
EMPTY = ' ' #empty
SIZE = (10, 20)

SCORE_TABLE = [40, 100, 300, 1200]

score = 0
level = 0
cleared = 0

grid = np.full((SIZE[1], SIZE[0]), EMPTY, dtype=str)

active_block = Block(BLOCKS[randint(0, len(BLOCKS) - 1)], [3, 0])
active_block.place(grid)

next_block = Block(BLOCKS[randint(0, len(BLOCKS) - 1)], [3, 0])

# MAIN LOOP ======================================================================

refresh()
while True:
    if not active_block.can_move(grid, [0, 1]):
        if not can_spawn_block(grid, next_block) and not is_row_empty(grid, next_block.bounds[1] - 1):
            refresh()
            print("\nGAME OVER!")
            break
        
        active_block = next_block
        active_block.place(grid)
        
        next_block = Block(BLOCKS[randint(0, len(BLOCKS) - 1)], [3, 0])

        #check line clears when changing shapes to clear multiple lines at once and not one by one
        full_rows = get_full_rows(grid)
        if len(full_rows) > 0:
            #calculate level & xp
            cleared += len(full_rows)
            if (cleared >= 10):
                level += int(cleared / 10)
                cleared = cleared % 10 #if level up, put remainder xp towards next level
            
            #calculate score from table
            if (len(full_rows) < len(SCORE_TABLE)):
                score += SCORE_TABLE[len(full_rows) - 1] + (SCORE_TABLE[len(full_rows) - 1] * level)
            else:
                score += SCORE_TABLE[3] + (SCORE_TABLE[3] * level)

            #delete & shift rows
            for row in full_rows:
                delete_row(grid, row)

    input = msvcrt.getch().decode('ASCII')
    
    if input == QUIT:
        os.system('cls')
        sys.exit()
    
    if input == ROTATE:
        active_block.rotate(grid)
    if input == LEFT:
        active_block.move(grid, [-1, 0])
    if input == RIGHT:
        active_block.move(grid, [1, 0])
    if input == DOWN:
        active_block.move(grid, [0, 1])

    refresh()