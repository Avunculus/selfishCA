import numpy as np
import pygame as pg
import os
import time
import random 
pg.font.init()
pg.display.init()

MAX_W, MAX_H = pg.display.get_desktop_sizes()[0]
BF = 4
FH = 24
FPS = 10
FONT = pg.font.SysFont('couriernew', FH, bold=True)
FONT_SMALL = pg.font.SysFont('couriernew', 12, bold=True)
COLORS = (pg.Color( 53,  53,  53),  # OLD: cell @ 0
          pg.Color(178,  34,  34),  # OLD: cell @ 1
          pg.Color(  2,  31, 247),  # font fg 1
          pg.Color( 75, 130, 227),  # font fg 2
          pg.Color(111,   0,  34),  # font bg 1
          pg.Color(180, 180, 187))  # font bg 2

def sprinkle(seed_count:int, area:tuple[int,int]) -> np.ndarray:
    if area[0] * area[1] < seed_count:
        print(f'error: seed count too big ({seed_count= } // {area= }')
        return False
    kernel = [1] * seed_count + [0] * (area[0] * area[1] - seed_count)
    random.shuffle(kernel)
    kernel = np.array(kernel).reshape(area)
    return kernel

DBL_MASK_FT = np.array([[0, 1, 0, 1, 0], # = pt_mask.T
                        [1, 0, 0, 0, 1],
                        [0, 1, 0, 1, 0]])
DBL_MASK_PT = DBL_MASK_FT.T

def make_hex_bg(shape:tuple, scale:tuple) -> pg.Surface:
    m, n = shape
    arr = np.zeros(shape)
    bg = pg.Surface(shape)
    color = bg.map_rgb(0, 0, 0)
    inviz = bg.map_rgb(11, 22, 63)
    bg.set_colorkey(inviz)
    rows = (np.array([inviz, color] * (m // 2)),
            np.array([color, inviz] * (m // 2)))
    for i in range(n):
        arr[:, i] = rows[i % 2]
    pg.surfarray.blit_array(bg, arr)
    bg = pg.transform.scale(bg, (m * scale[0], n * scale[1]))
    return bg

def get_square_kernel(type:str, size:int=1, totalistic=True) -> np.ndarray:
    """Type is one of:\n
    'M' | 'm' (Moore: adjacent and diagonal neighbors)\n
    'V' | 'v' (Von Neuman: adjacent neighbors only)"""
    if type not in 'MmVv': return
    kernel = np.ones((2 * size + 1, 2 * size + 1))
    if type in 'Vv':
        with np.nditer(kernel, flags=['multi_index'], op_flags=['readwrite']) as it:
            for _ in it:
                if abs(size - it.multi_index[0]) + abs(size - it.multi_index[1]) > size:
                    kernel[it.multi_index] = 0
    if not totalistic:
        kernel[size, size] = 0
    # print(f'KERNEL:\n{kernel}')
    return kernel

def random_totalistic_rule(kernel:np.ndarray, val_range:int=2) -> np.ndarray:
    if val_range < 2: return
    rule = np.zeros(np.count_nonzero(kernel) * (val_range - 1) + 1)
    for i in range(rule.size):
        rule[i] = random.randint(0, val_range - 1)
    print(f'RULE:\n{rule}')
    # vstack * valrange?
    return rule 

