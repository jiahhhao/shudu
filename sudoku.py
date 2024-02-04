import numpy as np
import random


def is_valid(board, row, col, num):
    """检查在给定位置填入数字是否有效"""
    # 检查行
    if num in board[row]:
        return False
    # 检查列
    if num in [board[i][col] for i in range(9)]:
        return False
    # 检查宫
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def solve_sudoku(board, find_multiple_solutions=False):
    """使用回溯法解决数独，可选是否查找多个解"""
    empty = find_empty_location(board)
    if not empty:
        return True  # 没有空位置时返回True
    row, col = empty

    for num in random.sample(range(1, 10), 9):  # 随机化数字顺序
        if is_valid(board, row, col, num):
            board[row][col] = num
            if solve_sudoku(board, find_multiple_solutions):
                return True
            board[row][col] = 0  # 回溯

    return False


def find_empty_location(board):
    """找到棋盘上的一个空位置"""
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None


def remove_numbers_from_board(board, attempts=5):
    """
    从完整的棋盘中移除数字以创建谜题。
    'attempts' 控制移除数字的尝试次数，该参数可以根据难度级别调整。
    """
    while attempts > 0:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        while board[row][col] == 0:  # 如果已经是空的，则找另一个
            row = random.randint(0, 8)
            col = random.randint(0, 8)
        backup = board[row][col]
        board[row][col] = 0  # 尝试移除数字

        # 复制棋盘以检查解的唯一性
        board_copy = [row[:] for row in board]
        if not solve_sudoku(board_copy, find_multiple_solutions=True):
            board[row][col] = backup  # 如果没有唯一解，撤销移除操作

        attempts -= 1

def generate_sudoku_puzzle(difficulty):
    board = [[0 for _ in range(9)] for _ in range(9)]
    solve_sudoku(board)  # 生成完整解决方案
    print("ANS:\n", np.array(board))
    # 根据难度调整移除数字的数量
    if difficulty == 'Easy':
        remove_numbers_from_board(board, attempts=20)
    elif difficulty == 'Medium':
        remove_numbers_from_board(board, attempts=30)
    elif difficulty == 'Hard':
        remove_numbers_from_board(board, attempts=40)
    elif difficulty == 'Very Hard':
        remove_numbers_from_board(board, attempts=50)

    return board

def create_sudoku_board(difficulty):
    # print(f"开始创建...难度为{difficulty}的棋盘")
    # puzzle = generate_sudoku_puzzle(difficulty=difficulty)
    puzzle = [[4, 0, 3, 5, 9, 8, 2, 6, 1],
            [2, 9, 6, 4, 3, 1, 8, 7, 5],
            [8, 5, 1, 2, 7, 6, 4, 9, 3],
            [1, 2, 9, 7, 8, 4, 3, 5, 6],
            [5, 4, 7, 6, 2, 3, 9, 1, 8],
            [3, 6, 8, 9, 1, 5, 7, 2, 4],
            [7, 3, 4, 1, 6, 9, 5, 8, 2],
            [6, 8, 2, 3, 5, 7, 1, 4, 9],
            [9, 1, 5, 8, 4, 2, 6, 3, 7]]
    return puzzle

def is_valid_sudoku(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return False
    def check_row_col(matrix):
        for row in matrix:
            if len(row) > len(set(row)):
                return False
        return True

    def check_subgrid(matrix):
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                subgrid = [matrix[x][y] for x in range(i, i + 3) for y in range(j, j + 3)]
                if len(subgrid) > len(set(subgrid)):
                    return False
        return True

    return check_row_col(board) and check_row_col(zip(*board)) and check_subgrid(board)
    
