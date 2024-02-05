import pygame
import sys
import time 

import tools
import sudoku

pygame.init()

sudoku_board = None
initial_marks = None

screen_size = (800, 600)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("数独游戏")

board_size = 450  # 设置棋盘大小
cell_size = board_size / 9  # 每个小格的大小
board_pos = (175, 60)  # 棋盘在屏幕上的位置

# 绘制排行榜表格
x, y = 300, 150
cell_width, cell_height = 100, 40  # 单元格大小

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLACK_GRAY =  (150, 150, 150)
GREEN = (100, 200, 100) 
COLOR_INACTIVE = (176, 226, 255)
COLOR_ACTIVE = (30, 144, 255)
GOLDEN = (255, 215, 0)
ORANGE = (255, 150, 50)

# 字体
FONT_24 = pygame.font.Font(None, 24)  
FONT_28 = pygame.font.Font(None, 28)
FONT_32 = pygame.font.Font(None, 32)  
FONT_48 = pygame.font.Font(None, 48)
TITLE_FONT = pygame.font.Font(None, 64) 

game_state = 'menu'
start_time = None

# 定义按钮的样式
button_color = GRAY
button_width = 200
button_height = 50
button_width_s = 100  # 小按钮宽度
button_height_s = 40  # 小按钮高度

# 初始化选中的格子和游戏持续时间
selected_cell = None
elapsed_time = 0

button_positions = {
    "Start": (300, 150),
    "Difficulty level": (300, 250),
    "Ranking list": (300, 350),
    "Over": (300, 450),
}

difficulty_button_positions = {
    "Easy": (300, 150),
    "Medium": (300, 250),
    "Hard": (300, 350),
    "Very Hard": (300, 450),
}

leaderboard_button_positions = {
    "Easy": (50, 150),
    "Medium": (50, 250),
    "Hard": (50, 350),
    "Very Hard": (50, 450),
}

# 加载胜利和失败的图片
victory_image = pygame.image.load('img/victory.png')
failed_image = pygame.image.load('img/failed.png')

# 读取默认用户名和当前难度
default_username, current_difficulty, current_leaderboard_difficulty = tools.read_profile()

class InputBox:
    """定义输入框类，用于玩家输入名字"""
    
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)  # 定义输入框的矩形区域
        self.color = COLOR_INACTIVE  # 设置初始颜色
        self.text = text  # 输入框内的文本
        self.txt_surface = FONT_32.render(text, True, self.color)  # 渲染文本
        self.active = False  # 设置输入框的激活状态

    def handle_event(self, event):
        """处理输入框的事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 如果鼠标点击输入框，则激活或取消激活
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
                self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
            else:
                self.active = False
                self.color = COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print("当前参加玩家：", self.text)  # 输出当前玩家名字
                    tools.alter_profile_current_user_name(self.text)  # 更新玩家名字
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]  # 删除最后一个字符
                else:
                    self.text += event.unicode  # 添加新字符
                # 重新渲染文本
                self.txt_surface = FONT_32.render(self.text, True, self.color)

    def draw(self, screen):
        """在屏幕上绘制输入框"""
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

input_box = InputBox(70, 100, 140, 32, default_username)  # 创建输入框实例


def check_button_click(mouse_pos):
    global game_state, start_time, current_difficulty, current_leaderboard_difficulty, selected_cell

    # 如果当前游戏状态为菜单
    if game_state == 'menu':
        # 遍历菜单按钮的位置
        for text, position in button_positions.items():
            # 为每个按钮创建一个矩形，用于检测鼠标点击
            button_rect = pygame.Rect(position[0], position[1], button_width, button_height)
            # 如果当前鼠标位置在按钮上
            if button_rect.collidepoint(mouse_pos):
                # 根据点击的按钮执行相应操作
                if text == "Start":
                    start_game()  # 开始游戏
                elif text == "Over":
                    end_game()  # 结束游戏
                elif text == "Difficulty level":
                    set_difficulty()  # 设置难度
                elif text == "Ranking list":
                    show_leaderboard()  # 显示排行榜
    
    # 如果当前游戏状态为游戏进行中
    elif game_state == 'playing':
        # 创建重新开始和返回菜单按钮的矩形
        restart_button_rect = pygame.Rect(50, 530, button_width, button_height)
        menu_button_rect = pygame.Rect(550, 530, button_width, button_height)
        # 如果点击重新开始按钮
        if restart_button_rect.collidepoint(mouse_pos):
            reset_sudoku_board()  # 重置数独棋盘
            start_time = None  # 重置开始时间
        # 如果点击返回菜单按钮
        elif menu_button_rect.collidepoint(mouse_pos):
            game_state = 'menu'  # 更改游戏状态为菜单
            start_time = None  # 重置开始时间

        # 检测棋盘上的单元格点击
        for row in range(9):
            for col in range(9):
                cell_rect = pygame.Rect(board_pos[0] + col * cell_size, board_pos[1] + row * cell_size, cell_size, cell_size)
                if cell_rect.collidepoint(mouse_pos):
                    selected_cell = (row, col)  # 更新选中的格子
                    return  # 一次只处理一个点击事件，优化性能
                
    # 如果当前游戏状态为设置难度
    elif game_state == 'setting_difficulty':
        # 创建返回按钮的矩形
        button_rect_return = pygame.Rect(550, 530, button_width, button_height)
        # 遍历难度选择按钮
        for difficulty, position in difficulty_button_positions.items():
            button_rect = pygame.Rect(position[0], position[1], button_width, button_height)
            if button_rect.collidepoint(mouse_pos):
                current_difficulty = difficulty  # 更新当前难度
        # 如果点击返回按钮
        if button_rect_return.collidepoint(mouse_pos):
            game_state = 'menu'  # 返回菜单

    # 如果当前游戏状态为查看排行榜
    elif game_state == 'leaderboard':
        button_rect_return = pygame.Rect(550, 530, button_width, button_height)
        # 遍历排行榜难度选择按钮
        for difficulty, position in leaderboard_button_positions.items():
            if pygame.Rect(position[0], position[1], button_width, button_height).collidepoint(mouse_pos):
                current_leaderboard_difficulty = difficulty
        # 如果点击返回按钮
        if button_rect_return.collidepoint(mouse_pos):
            game_state = 'menu'  # 返回菜单

    # 如果游戏状态为胜利
    elif game_state == 'victory':
        button_rect_return = pygame.Rect(550, 530, button_width, button_height)
        # 如果点击返回按钮
        if button_rect_return.collidepoint(mouse_pos):
            game_state = 'menu'  # 返回菜单
            start_time = None  # 重置开始时间

    # 如果游戏状态为失败
    elif game_state == 'failed':
        button_rect_return = pygame.Rect(550, 530, button_width, button_height)
        # 如果点击返回按钮
        if button_rect_return.collidepoint(mouse_pos):
            game_state = 'menu'  # 返回菜单
            start_time = None  # 重置开始时间


def draw_button(text, position):
    """在指定位置绘制按钮"""
    pygame.draw.rect(screen, button_color, (*position, button_width, button_height))
    text_render = FONT_28.render(text, True, BLACK)
    text_rect = text_render.get_rect(center=(position[0]+button_width/2, position[1]+button_height/2))
    screen.blit(text_render, text_rect)


def draw_menu():

    # 渲染并绘制标题
    title_surface = TITLE_FONT.render('Sudoku games', True, BLACK)
    title_rect = title_surface.get_rect(center=(400, 50))
    screen.blit(title_surface, title_rect)

    # 渲染并绘制输入框旁的提示文本
    prompt_surface = FONT_24.render('Enter to save after writing the name', True, BLACK)
    prompt_rect = prompt_surface.get_rect(center=(150, 90))
    screen.blit(prompt_surface, prompt_rect)

    # 在菜单状态下绘制输入框
    input_box.draw(screen)

    for text, position in button_positions.items():
        draw_button(text, position)


def draw_sudoku_board():

    global start_time, elapsed_time

    if start_time is None:
        start_time = time.time()

    elapsed_time = int(time.time() - start_time)
    timer_text = FONT_28.render(f"Time: {elapsed_time} seconds", True, BLACK)
    screen.blit(timer_text, (550, 20))

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
                num_text = FONT_28.render(str(num), True, color)
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
    initial_marks = [[False for _ in range(9)] for _ in range(9)]

    for row in range(9):
        for col in range(9):
            if sudoku_board[row][col] != 0:
                initial_marks[row][col] = True  # 标记预先填充的数字


def draw_difficulty_settings():
    """绘制难度设置页面"""
    current_difficulty_text = FONT_28.render(f"Current Difficulty: {current_difficulty}", True, BLACK)
    screen.blit(current_difficulty_text, (250, 50))

    for difficulty, position in difficulty_button_positions.items():
        if difficulty == current_difficulty:
            button_color = GREEN
        else:
            button_color = GRAY
        pygame.draw.rect(screen, button_color, (*position, button_width, button_height))
        text_render = FONT_28.render(difficulty, True, BLACK)
        text_rect = text_render.get_rect(center=(position[0]+button_width/2, position[1]+button_height/2))
        screen.blit(text_render, text_rect)

    # 绘制返回菜单按钮
    draw_button("Return", (550, 530)) 


def set_difficulty():
    global game_state
    print("设置难度...")
    game_state = 'setting_difficulty'


def draw_leaderboard():

    # 绘制排行榜按钮    
    current_difficulty_text = FONT_28.render(f"Leaderboard Difficulty: {current_leaderboard_difficulty}", True, BLACK)
    screen.blit(current_difficulty_text, (250, 50))

    for difficulty, position in leaderboard_button_positions.items():
        # 根据是否是当前难度来设置按钮颜色
        if difficulty == current_leaderboard_difficulty:
            button_color = GREEN  # 当前难度的按钮颜色
        else:
            button_color = GRAY
        pygame.draw.rect(screen, button_color, (*position, button_width_s, button_height_s))
        text_render = FONT_28.render(difficulty, True, BLACK)
        text_rect = text_render.get_rect(center=(position[0]+button_width_s/2, position[1]+button_height_s/2))
        screen.blit(text_render, text_rect)

    draw_button("Return", (550, 530))  
    
    # 绘制表头
    header_text = ['Name', '                                Time Used']
    for i, header in enumerate(header_text):
        header_render = FONT_24.render(header, True, BLACK)
        header_rect = header_render.get_rect(center=(x + cell_width * i + cell_width // 2, y))
        screen.blit(header_render, header_rect)

    leaderboards = tools.read_leaderboards()

    leaderboard_data = leaderboards[current_leaderboard_difficulty]
    for i, entry in enumerate(leaderboard_data):
        name_render = FONT_24.render(entry['name'], True, BLACK)
        name_rect = name_render.get_rect(center=(x + cell_width // 2, y + cell_height * (i + 1) + cell_height // 2))
        screen.blit(name_render, name_rect)

        time_render = FONT_24.render(str(entry['time']), True, BLACK)
        time_rect = time_render.get_rect(center=(x + cell_width * 2 + cell_width // 2, y + cell_height * (i + 1) + cell_height // 2))
        screen.blit(time_render, time_rect)


def show_leaderboard():
    global game_state
    print("显示排行榜...")
    game_state = 'leaderboard'


victory_image_rect = victory_image.get_rect(center=(400, 330))  # 居中显示
def draw_victory_screen(user_name, time_spent):

    screen.fill(WHITE)  
    
    # 渲染恭喜信息
    congrats_text = FONT_48.render(f'{user_name}, Congratulations on the victory!', True, GOLDEN)
    congrats_rect = congrats_text.get_rect(center=(400, 50))
    screen.blit(congrats_text, congrats_rect)
    
    # 渲染用时信息
    time_text = FONT_48.render(f'It only took {time_spent} seconds', True, GOLDEN)  
    time_rect = time_text.get_rect(center=(400, 100))
    screen.blit(time_text, time_rect)
    
    # 绘制胜利的图片
    screen.blit(victory_image, victory_image_rect)

    draw_button("Menu", (550, 530))

    
failed_image_rect = victory_image.get_rect(center=(380, 330))  # 居中显示
def draw_failed(user_name, time_spent):

    congrats_text = FONT_48.render(f'{user_name}, Almost made it to the leaderboard!', True, BLACK)
    congrats_rect = congrats_text.get_rect(center=(400, 50))
    screen.blit(congrats_text, congrats_rect)
    

    time_text = FONT_48.render(f'It took {time_spent} seconds, Come on! You can do it!', True, ORANGE)  
    time_rect = time_text.get_rect(center=(400, 100))
    screen.blit(time_text, time_rect)
    screen.blit(failed_image, failed_image_rect)

    draw_button("Menu", (550, 530)) 


def end_game():
    print("结束游戏...")
    pygame.quit()
    sys.exit()

# 游戏主循环
running = True

# 游戏主循环，持续运行直到游戏结束
while running:
    # 遍历所有的事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            check_button_click(mouse_pos)
        elif event.type == pygame.KEYDOWN and game_state == 'playing':
            # 如果有格子被选中且该格子不是初始填充的数字
            if selected_cell is not None and not initial_marks[selected_cell[0]][selected_cell[1]]:
                row, col = selected_cell
                if pygame.K_0 <= event.key <= pygame.K_9:
                    sudoku_board[row][col] = event.key - pygame.K_0
                    selected_cell = None
            if sudoku.is_valid_sudoku(sudoku_board):
                # 读取玩家名字
                win_name = tools.read_user_name()
                # 更新排行榜，并检查是否成功更新
                is_updated_leaderboard = tools.update_leaderboard(win_name, current_difficulty, elapsed_time)
                if is_updated_leaderboard:
                    game_state = 'victory'
                else:
                    game_state = 'failed'

        # 处理输入框事件
        input_box.handle_event(event)

    # 填充屏幕背景色
    screen.fill(WHITE)

    # 根据当前游戏状态绘制相应的界面
    if game_state == 'menu':
        draw_menu()
    elif game_state == 'playing':
        draw_sudoku_board()
    elif game_state == 'setting_difficulty':
        draw_difficulty_settings()
    elif game_state == 'leaderboard':
        draw_leaderboard()
    elif game_state == 'victory':
        draw_victory_screen(win_name, elapsed_time)
    elif game_state == 'failed':
        draw_failed(win_name, elapsed_time)
    
    pygame.display.flip()


# 退出Pygame 
pygame.quit()
sys.exit()