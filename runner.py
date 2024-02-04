import pygame
import sys
import time 

import tools
import sudoku


# 初始化Pygame
pygame.init()

sudoku_board = None
initial_marks = None

class InputBox:
    
    def __init__(self, x, y, w, h, text=''):
        self.FONT = pygame.font.Font(None, 32)
        self.COLOR_INACTIVE = pygame.Color('lightskyblue3')
        self.COLOR_ACTIVE = pygame.Color('dodgerblue2')

        self.rect = pygame.Rect(x, y, w, h)
        self.color = self.COLOR_INACTIVE
        self.text = text
        self.txt_surface = self.FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 如果用户点击输入框，就激活它
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
                self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE
            else:
                self.active = False
                self.color = self.COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)  # 或者做其他事情
                    tools.alter_profile_current_user_name(self.text)
                    # self.text = ''  # 按下回车后清空输入框
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # 重新渲染文本
                self.txt_surface = self.FONT.render(self.text, True, self.color)

    def draw(self, screen):
        # 绘制文本
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # 绘制输入框边框
        pygame.draw.rect(screen, self.color, self.rect, 2)


# 设置屏幕尺寸
screen_size = (800, 600)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("数独游戏")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLACK_GRAY =  (150, 150, 150)
FONT = pygame.font.Font(None, 32)  # 用于输入框
TITLE_FONT = pygame.font.Font(None, 64)  # 用于标题
TEXT_FONT = pygame.font.Font(None, 24)  # 用于提示文本

# 定义颜色
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
COLOR_WHITE = pygame.Color('white')
# 设置字体
font = pygame.font.Font(None, 28)

game_state = 'menu'
start_time = None

# 按钮属性
button_color = GRAY
button_width = 200
button_height = 50

button_width_s = 100
button_height_s = 40

elapsed_time = 0

button_positions = {
    "Start": (300, 150),
    "Difficulty level": (300, 250),
    "Ranking list": (300, 350),
    "Over": (300, 450),
}

# 当前难度
# current_difficulty = 'Easy'  # 默认难度为简单
# current_leaderboard_difficulty = 'Easy'

# 难度按钮的位置
difficulty_button_positions = {
    "Easy": (300, 150),
    "Medium": (300, 250),
    "Hard": (300, 350),
    "Very Hard": (300, 450),
}

# 假设你有一个排行榜数据的字典，其中包括不同难度的排行榜
# TODO 
default_username, current_difficulty, current_leaderboard_difficulty = tools.read_profile()
input_box = InputBox(70, 100, 140, 32, default_username)

selected_cell = None  # 初始化选中的格子为None

# 添加排行榜按钮的位置
leaderboard_button_positions = {
    "Easy": (50, 150),
    "Medium": (50, 250),
    "Hard": (50, 350),
    "Very Hard": (50, 450),
}

def check_button_click(mouse_pos):
    global game_state, start_time, current_difficulty, current_leaderboard_difficulty,selected_cell
    if game_state == 'menu':
        # 当游戏处于菜单状态时，处理主菜单的按钮点击
        for text, position in button_positions.items():
            button_rect = pygame.Rect(position[0], position[1], button_width, button_height)
            if button_rect.collidepoint(mouse_pos):
                if text == "Start":
                    start_game()
                elif text == "Over":
                    end_game()
                elif text == "Difficulty level":
                    set_difficulty()
                elif text == "Ranking list":
                    show_leaderboard()
    
    elif game_state == 'playing':
        # 当游戏处于播放状态时，仅处理"重新开始"和"返回菜单"按钮的点击
        restart_button_rect = pygame.Rect(50, 530, button_width, button_height)
        menu_button_rect = pygame.Rect(550, 530, button_width, button_height)
        if restart_button_rect.collidepoint(mouse_pos):
            reset_sudoku_board()
            start_time = None  # 重置开始时间

        elif menu_button_rect.collidepoint(mouse_pos):
            game_state = 'menu'
            start_time = None  # 重置开始时间


        board_pos = (175, 60)  # 棋盘在屏幕上的位置
        cell_size = 450 / 9  # 每个小格的大小
        for row in range(9):
            for col in range(9):
                cell_rect = pygame.Rect(board_pos[0] + col * cell_size, board_pos[1] + row * cell_size, cell_size, cell_size)
                if cell_rect.collidepoint(mouse_pos):
                    selected_cell = (row, col)  # 更新选中的格子
                    return  # 一次只处理一个点击
                
    elif game_state == 'setting_difficulty':
        # 处理难度选择按钮
        button_rect_return = pygame.Rect(550, 530, button_width, button_height)
        for difficulty, position in difficulty_button_positions.items():
            button_rect = pygame.Rect(position[0], position[1], button_width, button_height)
            if button_rect.collidepoint(mouse_pos):
                current_difficulty = difficulty  # 更新当前难度
                print(f"当前查看难度难度为: {difficulty}")

        if button_rect_return.collidepoint(mouse_pos):
            tools.alter_profile_current_difficulty(current_difficulty)
            game_state = 'menu'

    elif game_state == 'leaderboard':
        # 排行榜状态下的按钮处理
        button_rect_return = pygame.Rect(550, 530, button_width, button_height)
        for difficulty, position in leaderboard_button_positions.items():
            if pygame.Rect(position[0], position[1], button_width, button_height).collidepoint(mouse_pos):
                current_leaderboard_difficulty = difficulty 
        if button_rect_return.collidepoint(mouse_pos):
            tools.alter_profile_current_leaderboard_difficulty(current_leaderboard_difficulty)
            game_state = 'menu'
    elif game_state == 'victory':
        button_rect_return = pygame.Rect(550, 530, button_width, button_height)
        if button_rect_return.collidepoint(mouse_pos):
            game_state = 'menu'
            start_time = None  # 重置开始时间
    elif game_state == 'failed':
        button_rect_return = pygame.Rect(550, 530, button_width, button_height)
        if button_rect_return.collidepoint(mouse_pos):
            game_state = 'menu'
            start_time = None  # 重置开始时间

def draw_button(text, position):
    
    """在指定位置绘制按钮"""
    pygame.draw.rect(screen, button_color, (*position, button_width, button_height))
    text_render = font.render(text, True, BLACK)
    text_rect = text_render.get_rect(center=(position[0]+button_width/2, position[1]+button_height/2))
    screen.blit(text_render, text_rect)

# ---------------------------------------------------下面是菜单页面
    
def draw_menu():

    # 渲染并绘制标题
    title_surface = TITLE_FONT.render('Sudoku games', True, BLACK)
    title_rect = title_surface.get_rect(center=(400, 50))
    screen.blit(title_surface, title_rect)

    # 渲染并绘制输入框旁的提示文本
    prompt_surface = TEXT_FONT.render('Enter to save after writing the name', True, BLACK)
    prompt_rect = prompt_surface.get_rect(center=(150, 90))  # 根据输入框位置调整
    screen.blit(prompt_surface, prompt_rect)

    # 在菜单状态下绘制输入框
    input_box.draw(screen)

    for text, position in button_positions.items():
        draw_button(text, position)

# ---------------------------------------------------上面是菜单页面

# ---------------------------------------------------下面是开始页面
def draw_sudoku_board():
    global start_time, elapsed_time
    if start_time is None:
        start_time = time.time()

    elapsed_time = int(time.time() - start_time)
    timer_text = font.render(f"Time: {elapsed_time} seconds", True, BLACK)
    screen.blit(timer_text, (550, 20))

    board_size = 450  # 设置棋盘大小
    cell_size = board_size / 9  # 每个小格的大小
    board_pos = (175, 60)  # 棋盘在屏幕上的位置

    # 绘制网格和数字
    for row in range(9):
        for col in range(9):
            # 计算当前格子的位置
            cell_x = board_pos[0] + col * cell_size
            cell_y = board_pos[1] + row * cell_size
            
            num = sudoku_board[row][col]
            if num != 0:  # 如果当前格子有数字
                if initial_marks[row][col]:
                    color = BLACK_GRAY  # 预先填充的数字为灰色
                else:
                    color = BLACK  # 用户填入的数字为黑色
                num_text = font.render(str(num), True, color)
                text_rect = num_text.get_rect(center=(cell_x + cell_size / 2, cell_y + cell_size / 2))
                screen.blit(num_text, text_rect)

    # 绘制网格线
    for i in range(10):
        if i % 3 == 0:
            line_width = 4
        else:
            line_width = 1
        pygame.draw.line(screen, BLACK, (board_pos[0] + i * cell_size, board_pos[1]), (board_pos[0] + i * cell_size, board_pos[1] + board_size), line_width)
        pygame.draw.line(screen, BLACK, (board_pos[0], board_pos[1] + i * cell_size), (board_pos[0] + board_size, board_pos[1] + i * cell_size), line_width)

    draw_button("Restart", (50, 530))
    draw_button("Menu", (550, 530))

def reset_sudoku_board():
    global sudoku_board
    for row in range(9):
        for col in range(9):
            if not initial_marks[row][col]:  # 如果不是预先填充的数字
                sudoku_board[row][col] = 0  # 清空用户填入的数字

def start_game():
    global game_state, start_time, sudoku_board, initial_marks
    start_time =  None
    game_state = 'playing'
    print("开始游戏...")

    sudoku_board = sudoku.create_sudoku_board(current_difficulty)
    # 假设sudoku_board已经被定义为一个9x9的二维数组
    initial_marks = [[False for _ in range(9)] for _ in range(9)]

    # 填充棋盘和标记数组
    for row in range(9):
        for col in range(9):
            if sudoku_board[row][col] != 0:
                initial_marks[row][col] = True  # 标记预先填充的数字

# --------------------------------------------------- 上面是开始页面

# --------------------------------------------------- 下面是设置难度页面
    
# 绘制难度设置页面
def draw_difficulty_settings():
    """绘制难度设置页面"""
    # 绘制当前难度标题
    current_difficulty_text = font.render(f"Current Difficulty: {current_difficulty}", True, BLACK)
    screen.blit(current_difficulty_text, (250, 50))

    # 绘制难度选择按钮
    for difficulty, position in difficulty_button_positions.items():
        # 根据是否是当前难度来设置按钮颜色
        if difficulty == current_difficulty:
            button_color = (100, 200, 100)  # 当前难度的按钮颜色
        else:
            button_color = GRAY
        pygame.draw.rect(screen, button_color, (*position, button_width, button_height))
        text_render = font.render(difficulty, True, BLACK)
        text_rect = text_render.get_rect(center=(position[0]+button_width/2, position[1]+button_height/2))
        screen.blit(text_render, text_rect)

    # 绘制返回菜单按钮
    draw_button("Return", (550, 530))  # 假设位置在(300, 550)

def set_difficulty():
    global game_state
    print("设置难度...")
    game_state = 'setting_difficulty'
# --------------------------------------------------- 上面是设置难度页面
    
# --------------------------------------------------- 下面是排行榜页面
# 绘制排行榜页面
def draw_leaderboard():
    # 绘制排行榜按钮    
    current_difficulty_text = font.render(f"Leaderboard Difficulty: {current_leaderboard_difficulty}", True, BLACK)
    screen.blit(current_difficulty_text, (250, 50))
    for difficulty, position in leaderboard_button_positions.items():
        # 根据是否是当前难度来设置按钮颜色
        if difficulty == current_leaderboard_difficulty:
            button_color = (100, 200, 100)  # 当前难度的按钮颜色
        else:
            button_color = GRAY
        pygame.draw.rect(screen, button_color, (*position, button_width_s, button_height_s))
        text_render = font.render(difficulty, True, BLACK)
        text_rect = text_render.get_rect(center=(position[0]+button_width_s/2, position[1]+button_height_s/2))
        screen.blit(text_render, text_rect)

    # 绘制返回按钮
    draw_button("Return", (550, 530))  # 假设位置在(300, 550)

    # 绘制排行榜表格
    x, y = 300, 150  # 表格左上角位置
    cell_width, cell_height = 100, 40  # 单元格大小
    font_size = 24
    header_font = pygame.font.Font(None, font_size)
    cell_font = pygame.font.Font(None, font_size)
    
    # 绘制表头
    header_text = ['Name', '                                Time Used']
    for i, header in enumerate(header_text):
        header_render = header_font.render(header, True, BLACK)
        header_rect = header_render.get_rect(center=(x + cell_width * i + cell_width // 2, y))
        screen.blit(header_render, header_rect)

    # 绘制排行榜数据
    
    leaderboards = tools.read_leaderboards()

    leaderboard_data = leaderboards[current_leaderboard_difficulty]
    for i, entry in enumerate(leaderboard_data):
        name_render = cell_font.render(entry['name'], True, BLACK)
        name_rect = name_render.get_rect(center=(x + cell_width // 2, y + cell_height * (i + 1) + cell_height // 2))
        screen.blit(name_render, name_rect)

        time_render = cell_font.render(str(entry['time']), True, BLACK)
        time_rect = time_render.get_rect(center=(x + cell_width * 2 + cell_width // 2, y + cell_height * (i + 1) + cell_height // 2))
        screen.blit(time_render, time_rect)

def show_leaderboard():
    global game_state
    print("显示排行榜...")
    game_state = 'leaderboard'
# --------------------------------------------------- 上面是排行榜页面

# --------------------------------------------------- 下面是恭喜
    
victory_image = pygame.image.load('img/victory.png')
victory_image_rect = victory_image.get_rect(center=(400, 330))  # 居中显示

# 定义字体
FONT = pygame.font.Font(None, 48)
def draw_victory_screen(user_name, time_spent):
    screen.fill(WHITE)  # 用黑色填充屏幕
    
    # 渲染恭喜信息
    congrats_text = FONT.render(f'{user_name}, Congratulations on the victory!', True, (255, 215, 0))  # 金色
    congrats_rect = congrats_text.get_rect(center=(400, 50))
    screen.blit(congrats_text, congrats_rect)
    
    # 渲染用时信息
    time_text = FONT.render(f'It only took {time_spent} seconds', True, (255, 215, 0))  # 金色
    time_rect = time_text.get_rect(center=(400, 100))
    screen.blit(time_text, time_rect)
    
    # 绘制胜利的图片
    screen.blit(victory_image, victory_image_rect)

    draw_button("Menu", (550, 530))  # 假设位置在(300, 550)
    # 更新屏幕显示
    pygame.display.flip()

# --------------------------------------------------- 上面是恭喜
    


failed_image = pygame.image.load('img/failed.png')
failed_image_rect = victory_image.get_rect(center=(380, 330))  # 居中显示
def draw_failed(user_name, time_spent):
    # 渲染恭喜信息
    congrats_text = FONT.render(f'{user_name}, Almost made it to the leaderboard!', True, BLACK)
    congrats_rect = congrats_text.get_rect(center=(400, 50))
    screen.blit(congrats_text, congrats_rect)
    
    # 渲染用时信息
    time_text = FONT.render(f'It took {time_spent} seconds, Come on! You can do it!', True, (255, 150, 50))  
    time_rect = time_text.get_rect(center=(400, 100))
    screen.blit(time_text, time_rect)
    screen.blit(failed_image, failed_image_rect)

    draw_button("Menu", (550, 530))  # 假设位置在(300, 550)
    # 更新屏幕显示
    pygame.display.flip()

def end_game():
    print("结束游戏...")
    pygame.quit()
    sys.exit()








# 游戏主循环
running = True

win_name = 'p'
cost_time = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 检测鼠标点击
            mouse_pos = pygame.mouse.get_pos()
            check_button_click(mouse_pos)
        elif event.type == pygame.KEYDOWN and game_state== 'playing':
            if game_state == 'playing' and selected_cell is not None:
                row, col = selected_cell
                if not initial_marks[row][col]:  # 仅允许更改未被标记的格子 TODO 还可以修改 
                    if pygame.K_0 <= event.key <= pygame.K_9:
                        sudoku_board[row][col] = event.key - pygame.K_0
                        selected_cell = None  # 清除选中的格子
            if sudoku.is_valid_sudoku(sudoku_board):
                print("SUCCESS!!!!!!!!!!!!!!!!!!!!!!!")

                win_name = tools.raed_user_name()

                print("NAME:", win_name, "TIME:", elapsed_time)
                cost_time = elapsed_time
                is_updated_leaderboard = tools.update_leaderboard(win_name, current_difficulty, elapsed_time)
                if is_updated_leaderboard:
                    game_state = 'victory'
                else:
                    game_state = 'failed'


        input_box.handle_event(event)
    # 填充背景色
    screen.fill(WHITE)

    if game_state == 'menu':
        # 绘制按钮
        draw_menu()
        
    elif game_state == 'playing':
        # 绘制数独棋盘
        draw_sudoku_board()
    elif game_state == 'setting_difficulty':
        draw_difficulty_settings()
    elif game_state == 'leaderboard':
        draw_leaderboard()
    elif game_state == 'victory':
        draw_victory_screen(win_name,cost_time)
    elif game_state == 'failed':
        draw_failed(win_name,cost_time)
    # 更新屏幕显示
    pygame.display.flip()




# 退出Pygame 
pygame.quit()
sys.exit()


