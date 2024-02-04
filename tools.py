import yaml
import os

path_user_data = 'user_data.yaml'

# check 
if not os.path.exists(path_user_data):
    print("没有user_data正在创建...")
    default_content = {
        'current_difficulty': 'Easy',
        'current_leaderboard_difficulty': 'Easy',
        'now_user_name':'xxx',
        'leaderboards': {
            'Easy': {f'User{i}': {'Name': '', 'Time': ''} for i in range(1, 8)},
            'Medium': {f'User{i}': {'Name': '', 'Time': ''} for i in range(1, 8)},
            'Hard': {f'User{i}': {'Name': '', 'Time': ''} for i in range(1, 8)},
            'Very Hard': {f'User{i}': {'Name': '', 'Time': ''} for i in range(1, 8)}
        }
    }
    with open(path_user_data, 'w') as file:
        yaml.dump(default_content, file, allow_unicode=True)

def read_profile():
    with open(path_user_data, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    now_user_name = data['now_user_name']
    current_difficulty = data['current_difficulty']
    current_leaderboard_difficulty = data['current_leaderboard_difficulty']

    return now_user_name, current_difficulty, current_leaderboard_difficulty


def read_leaderboards():
    with open(path_user_data, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    original_data = data['leaderboards']
    leaderboards = {}
    for difficulty, users in original_data.items():
        leaderboard_data = []
        for user, user_info in users.items():
            if user_info['Name'] != '' and user_info['Time'] != '':
                leaderboard_data.append({'name': user_info['Name'], 'time': user_info['Time']})
        leaderboards[difficulty] = leaderboard_data
    return leaderboards


def alter_profile_current_difficulty(new_current_difficulty):
    with open(path_user_data, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    data['current_difficulty'] = new_current_difficulty
    with open(path_user_data, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)
    return True

def alter_profile_current_leaderboard_difficulty(new_current_leaderboard_difficulty):
    with open(path_user_data, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    data['current_leaderboard_difficulty'] = new_current_leaderboard_difficulty
    with open(path_user_data, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)
    return True

def alter_profile_current_user_name(new_name):
    with open(path_user_data, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    data['now_user_name'] = new_name
    with open(path_user_data, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)
    return True

def raed_user_name():
    with open(path_user_data, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data['now_user_name']




def read_yaml(file_path):
    """读取YAML文件"""
    with open(file_path, 'r') as file:
        return yaml.load(file, Loader=yaml.FullLoader)

def write_yaml(data, file_path):
    """写回YAML文件"""
    with open(file_path, 'w') as file:
        yaml.dump(data, file)

def update_leaderboard(user_name, difficulty, user_time):
    data = read_yaml(path_user_data)
    leaderboards = data['leaderboards'][difficulty]

    # 将排行榜转换为方便处理的列表
    leaderboard_list = [{'Name': v['Name'], 'Time': int(v['Time'])} for k, v in leaderboards.items() if v['Name']]

    # 检查是否能加入排行榜
    if len(leaderboard_list) < 7 or user_time < leaderboard_list[-1]['Time']:
        leaderboard_list.append({'Name': user_name, 'Time': user_time})
        # 根据时间排序并截取前7个记录
        leaderboard_list = sorted(leaderboard_list, key=lambda x: x['Time'])[:7]

        # 更新数据
        for i, record in enumerate(leaderboard_list, start=1):
            leaderboards[f'User{i}'] = {'Name': record['Name'], 'Time': str(record['Time'])}
        
        # 清理多余的记录
        for i in range(len(leaderboard_list) + 1, 8):
            leaderboards.pop(f'User{i}', None)

        write_yaml(data, path_user_data)
        
        print("排行榜已更新。")
        return True
    else:
        
        print("未能进入排行榜。")
        return False

