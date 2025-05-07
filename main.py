from gui import *
from string import digits

EVENTS = [pg.TEXTINPUT, pg.QUIT, pg.KEYDOWN, pg.MOUSEBUTTONDOWN]
VALUES = {0: pg.Color(0, 0, 0)}
COLOR_MAX = pg.Color(194,  44,  84)

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

def show(sfc:pg.Surface, cells:np.ndarray, val_range:int) -> None:
    img = pg.Surface(cells.shape)
    arr = np.zeros_like(cells)
    for i in range(1, val_range):       # 0 = black (doesn't need draw)
        color = img.map_rgb(VALUES[i])
        arr[np.where(cells==i)] = color
    # color1 = img.map_rgb(COLORS[0])
    # color2 = img.map_rgb(COLORS[1])
    # arr[np.where(cells==1)] = color1
    # arr[np.where(cells==2)] = color2
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



def main(grid:np.ndarray, kernel: np.ndarray, rule:np.ndarray,
         scale:tuple[int,int], val_range:int) -> bool:
    pg.event.set_blocked(None)
    pg.event.set_allowed(EVENTS)
    grid = np.random.random(grid.shape) * (val_range - 1)
    grid = grid.round()
    set_colordict(val_range)
    rez = (grid.shape[0] * scale[0], grid.shape[1] * scale[1])
    win = pg.display.set_mode(rez, flags=pg.NOFRAME)
    show(win, grid.astype(np.int64), val_range)
    clock = pg.time.Clock()
    autoflip = False
    running = True
    while running:
        clock.tick(FPS)
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    return False
                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_SPACE:
                            autoflip = not autoflip
                        case pg.K_q:        # quit
                            if event.mod & pg.KMOD_CTRL:
                                return False
                        case pg.K_r:        # re-set, randomize
                            if event.mod & pg.KMOD_CTRL: 
                                autoflip = False
                                grid = np.random.random(grid.shape) \
                                    * (val_range - 1)
                                grid = grid.round()
                                show(win, grid.astype(np.int64), val_range)
                        case pg.K_n:        # new game
                            if event.mod & pg.KMOD_CTRL:
                                return True
        if autoflip: # advance 1 gen 
            grid = flip_totalistic(grid, kernel, rule) 
            show(win, grid.astype(np.int64), val_range)
        pg.display.update()

SCALE = (4, 4)
COLS  = MAX_W // SCALE[0]
COLS -= COLS % 2
ROWS  = MAX_H // SCALE[1]
ROWS -= ROWS % 2
GRID  = np.zeros((COLS, ROWS))


if __name__ == '__main__':
    # current args: hood, hoodsize, valrange
    hood = 'V'
    hood_size = 1
    val_range = 4       # cell values are in range(3)
    ca_code = 'Q' + hood + repr(hood_size) + 'T' + repr(val_range)
    print(f'CA: {ca_code}')
    kernel = get_square_kernel(hood, hood_size)
    kernel = pad_to_fit(kernel, GRID.shape)
    rule = random_totalistic_rule(kernel, val_range=val_range)
    repeat = main(GRID, kernel, rule, SCALE, val_range)
    while repeat:
        GRID *= 0
        kernel = pad_to_fit(get_square_kernel(hood, hood_size), GRID.shape)
        rule = random_totalistic_rule(kernel, val_range=val_range)
        repeat = main(GRID, kernel, rule, SCALE, val_range)
    pg.quit()
    quit()
