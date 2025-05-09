from gui import *
from string import digits

EVENTS = [pg.TEXTINPUT, pg.QUIT, pg.KEYDOWN, pg.MOUSEBUTTONDOWN, pg.MOUSEMOTION, pg.MOUSEWHEEL]
VALUES = {0: pg.Color(0, 0, 0)}
COLOR_MAX = pg.Color(194,  44,  84)
SCALE = (4, 4)              # should derive from: W, H, hoodsize, valrange -> scale up to prevent lag

def set_colordict(val_range:int) -> None:
    global VALUES
    VALUES[val_range - 1] = COLOR_MAX
    for i in range(1, val_range - 1):
        color = VALUES[0].lerp(COLOR_MAX, i / (val_range - 1))
        VALUES[i] = color
    # print(f'COLORS:\n{[VALUES[i] for i in sorted(VALUES)]}')

def convolve2d(arr0:np.ndarray, arr1:np.ndarray) -> np.ndarray:
    func1 = np.fft.fft2(arr0)
    func2 = np.fft.fft2(np.flipud(np.fliplr(arr1)))
    m, n = func1.shape
    convolved = np.real(np.fft.ifft2(func1 * func2))
    convolved = np.roll(convolved, (- int(m / 2) + 1, - int(n / 2) + 1), axis=(0, 1))
    return convolved

def flip_totalistic(cells:np.ndarray, kernel:np.ndarray,
                    rule:np.ndarray) -> np.ndarray:
    ngb_sum = convolve2d(cells, kernel).round()
    new_cells = np.zeros(ngb_sum.shape)
    for i in np.nonzero(rule):
        for j in i:
            new_cells[np.where(ngb_sum == j)] = rule[j]
    return new_cells

def show_totalistic(sfc:pg.Surface, cells:np.ndarray, val_range:int) -> None:
    img = pg.Surface(cells.shape)
    arr = np.zeros_like(cells)
    for i in range(1, val_range):       # 0 = black (doesn't need draw)
        color = img.map_rgb(VALUES[i])
        arr[np.where(cells==i)] = color
    pg.surfarray.blit_array(img, arr)
    img = pg.transform.scale(img, sfc.get_size())
    sfc.blit(img, (0, 0))

def pad_to_fit(arr:np.ndarray, shape:tuple) -> np.ndarray:
    cols, rows = shape
    after0 = (cols - arr.shape[0]) // 2
    before0 = cols - arr.shape[0] - after0
    after1 = (rows - arr.shape[1]) // 2
    before1 = rows - arr.shape[1] - after1
    return np.pad(arr, ((before0, after0), (before1, after1)))

class GameTotalistic:
    def __init__(self, grid:np.ndarray, kernel:np.ndarray, rule:np.ndarray,
                 scale:tuple[int,int], val_range:int):
        self.grid   = grid
        self.kernel = kernel
        self.rule   = rule
        self.scale  = scale
        self.val_range = val_range
        set_colordict(val_range)
        rez = (grid.shape[0] * scale[0], grid.shape[1] * scale[1])
        self.win = pg.display.set_mode(rez, flags=pg.NOFRAME)
        self.show()

    def show(self):
        show_totalistic(self.win, self.grid.astype(np.int64), self.val_range)

    def flip(self):
        self.grid = flip_totalistic(self.grid, self.kernel, self.rule)
        self.show()
        
        
####################

def main() -> bool:
    cols  = MAX_W // SCALE[0]
    cols -= cols % 2
    rows  = MAX_H // SCALE[1]
    rows -= rows % 2
    grid  = np.zeros((cols, rows))
    scale = SCALE
    # DEFAULTS: current args:: hood, hoodsize, val_range, seed
    hood = 'V'
    hood_size = 2
    val_range = 4       # cell values are in range(3)
    # KERNEL: 
    kernel = get_square_kernel(hood, hood_size)
    kernel = pad_to_fit(kernel, grid.shape)
    # RULE
    rule = random_totalistic_rule(kernel, val_range=val_range)
    # SEED: single shape: max-range QV9, randomized 
    seed  = get_square_kernel('v', 9)
    seed *= np.random.random(seed.shape) * (val_range - 1)
    seed = seed.round()
    print(f'SEED:\n{seed}')
    seed = pad_to_fit(seed, grid.shape)
    grid += seed
    # # alt: 'noise'
    # grid = np.random.random(grid.shape) * (val_range - 1)
    # grid = grid.round()
    # GAME:
    game = GameTotalistic(grid, kernel, rule, scale, val_range)
    menu = GameMenu()
    ############ MAIN LOOP #######
    clock = pg.time.Clock()
    autoflip = False
    running  = True
    pg.event.set_blocked(None)
    pg.event.set_allowed(EVENTS)
    while running:
        clock.tick(FPS)
        if menu.showing:
            menu.handle_events(game)
        else:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return False
                elif event.type == pg.KEYDOWN:
                    if event.key ==    pg.K_SPACE:
                        autoflip = not autoflip
                    elif event.key ==  pg.K_ESCAPE:
                        menu.show(game)
                        autoflip = False
                    elif event.key ==  pg.K_q:        # quit
                        if event.mod & pg.KMOD_CTRL: break
                    elif event.key ==  pg.K_r:        # re-set, randomize
                        if event.mod & pg.KMOD_CTRL: 
                            autoflip = False
                            game.grid = np.random.random(game.grid.shape) \
                                * (game.val_range - 1)
                            game.grid = game.grid.round()
                            game.show()
        if autoflip: # advance 1 gen 
            game.flip()
        pg.display.update()



if __name__ == '__main__':
    main()
    pg.quit()
    quit()
