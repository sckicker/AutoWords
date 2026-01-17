"""
等级/经验值系统模块
管理玩家等级和经验值
"""
import json
import os


class LevelSystem:
    """玩家等级系统"""

    LEVEL_CONFIG = {
        1: {'name': 'Beginner', 'exp_required': 0, 'title': '英语小白', 'color': (150, 150, 150)},
        2: {'name': 'Learner', 'exp_required': 100, 'title': '学习新手', 'color': (100, 200, 100)},
        3: {'name': 'Student', 'exp_required': 300, 'title': '勤奋学生', 'color': (100, 150, 255)},
        4: {'name': 'Scholar', 'exp_required': 600, 'title': '英语达人', 'color': (200, 100, 255)},
        5: {'name': 'Expert', 'exp_required': 1000, 'title': '单词专家', 'color': (255, 200, 100)},
        6: {'name': 'Master', 'exp_required': 1500, 'title': '语言大师', 'color': (255, 150, 50)},
        7: {'name': 'Champion', 'exp_required': 2100, 'title': '打字冠军', 'color': (255, 100, 100)},
        8: {'name': 'Legend', 'exp_required': 2800, 'title': '传奇', 'color': (255, 50, 150)},
        9: {'name': 'Mythic', 'exp_required': 3600, 'title': '神话', 'color': (200, 50, 255)},
        10: {'name': 'Transcendent', 'exp_required': 4500, 'title': '超越者', 'color': (255, 215, 0)}
    }

    def __init__(self, save_path='data/user/progress.json'):
        self.save_path = save_path
        self.current_exp = 0
        self.current_level = 1
        self.total_words_typed = 0
        self.total_sentences_completed = 0
        self.total_levels_completed = 0
        self.load_progress()

    def add_exp(self, amount):
        """添加经验值，返回是否升级"""
        self.current_exp += amount
        return self._check_level_up()

    def add_exp_for_char(self):
        """正确输入一个字符获得的经验"""
        return self.add_exp(1)

    def add_exp_for_sentence(self, perfect=False):
        """完成一句话获得的经验"""
        exp = 15 if perfect else 10
        self.total_sentences_completed += 1
        return self.add_exp(exp)

    def add_exp_for_level(self):
        """完成一个关卡获得的经验"""
        self.total_levels_completed += 1
        return self.add_exp(50)

    def add_exp_for_combo(self, combo):
        """连击奖励经验"""
        bonus = int(combo * 0.5)
        return self.add_exp(bonus)

    def _check_level_up(self):
        """检查是否升级，返回新等级或None"""
        old_level = self.current_level
        for level in sorted(self.LEVEL_CONFIG.keys(), reverse=True):
            if self.current_exp >= self.LEVEL_CONFIG[level]['exp_required']:
                if level > self.current_level:
                    self.current_level = level
                    self.save_progress()
                    return level
                break
        return None

    def get_progress_to_next(self):
        """获取到下一级的进度百分比"""
        if self.current_level >= max(self.LEVEL_CONFIG.keys()):
            return 100.0

        current_exp_req = self.LEVEL_CONFIG[self.current_level]['exp_required']
        next_exp_req = self.LEVEL_CONFIG[self.current_level + 1]['exp_required']
        exp_in_level = self.current_exp - current_exp_req
        exp_needed = next_exp_req - current_exp_req

        return min(100.0, (exp_in_level / exp_needed) * 100)

    def get_exp_to_next_level(self):
        """获取距离下一级还需要多少经验"""
        if self.current_level >= max(self.LEVEL_CONFIG.keys()):
            return 0

        next_exp_req = self.LEVEL_CONFIG[self.current_level + 1]['exp_required']
        return next_exp_req - self.current_exp

    def get_level_info(self):
        """获取当前等级信息"""
        return self.LEVEL_CONFIG.get(self.current_level, self.LEVEL_CONFIG[1])

    def get_title(self):
        """获取当前称号"""
        return self.get_level_info()['title']

    def get_level_color(self):
        """获取当前等级颜色"""
        return self.get_level_info()['color']

    def save_progress(self):
        """保存进度到文件"""
        try:
            os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
            data = {
                'exp': self.current_exp,
                'level': self.current_level,
                'total_words': self.total_words_typed,
                'total_sentences': self.total_sentences_completed,
                'total_levels': self.total_levels_completed
            }
            with open(self.save_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"保存进度失败: {e}")

    def load_progress(self):
        """从文件加载进度"""
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                    self.current_exp = data.get('exp', 0)
                    self.current_level = data.get('level', 1)
                    self.total_words_typed = data.get('total_words', 0)
                    self.total_sentences_completed = data.get('total_sentences', 0)
                    self.total_levels_completed = data.get('total_levels', 0)
        except Exception as e:
            print(f"加载进度失败: {e}")
