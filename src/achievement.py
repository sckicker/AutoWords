"""
成就系统模块
跟踪和管理玩家成就
"""
import json
import os


class AchievementSystem:
    """成就系统"""

    ACHIEVEMENTS = {
        'first_level': {
            'name': 'First Steps',
            'description': 'Complete your first level',
            'icon': '🎯'
        },
        'perfect_sentence': {
            'name': 'Perfect!',
            'description': '100% accuracy on a sentence',
            'icon': '⭐'
        },
        'speed_demon': {
            'name': 'Speed Demon',
            'description': 'Type faster than 60 chars/min',
            'icon': '⚡'
        },
        'combo_5': {
            'name': 'On a Roll',
            'description': 'Reach a 5x combo',
            'icon': '🔥'
        },
        'combo_10': {
            'name': 'Unstoppable',
            'description': 'Reach a 10x combo',
            'icon': '💫'
        },
        'combo_20': {
            'name': 'Legendary',
            'description': 'Reach a 20x combo',
            'icon': '👑'
        },
        'all_levels': {
            'name': 'Champion',
            'description': 'Complete all levels',
            'icon': '🏆'
        },
        'no_errors': {
            'name': 'Flawless',
            'description': 'Complete a level with no errors',
            'icon': '💎'
        },
        # 新增成就
        'early_bird': {
            'name': 'Early Bird',
            'description': 'Practice before 7am',
            'icon': '🌅'
        },
        'night_owl': {
            'name': 'Night Owl',
            'description': 'Practice after 10pm',
            'icon': '🦉'
        },
        'daily_streak_7': {
            'name': 'Weekly Dedication',
            'description': '7 days login streak',
            'icon': '📅'
        },
        'daily_streak_30': {
            'name': 'Monthly Master',
            'description': '30 days login streak',
            'icon': '🗓️'
        },
        'speed_demon_pro': {
            'name': 'Speed Demon Pro',
            'description': 'Type faster than 100 chars/min',
            'icon': '⚡⚡'
        }
    }

    def __init__(self, save_path='data/user/achievements.json'):
        self.save_path = save_path
        self.unlocked = set()
        self.pending_notifications = []
        self.load_achievements()

    def unlock(self, achievement_id):
        """解锁成就"""
        if achievement_id not in self.unlocked and achievement_id in self.ACHIEVEMENTS:
            self.unlocked.add(achievement_id)
            achievement = self.ACHIEVEMENTS[achievement_id]
            self.pending_notifications.append(achievement)
            self.save_achievements()
            return True
        return False

    def check_combo(self, combo):
        """检查连击成就"""
        if combo >= 5:
            self.unlock('combo_5')
        if combo >= 10:
            self.unlock('combo_10')
        if combo >= 20:
            self.unlock('combo_20')

    def check_speed(self, speed):
        """检查速度成就"""
        if speed >= 60:
            self.unlock('speed_demon')
        if speed >= 100:
            self.unlock('speed_demon_pro')

    def check_accuracy(self, accuracy):
        """检查准确率成就"""
        if accuracy >= 100:
            self.unlock('perfect_sentence')

    def check_level_complete(self, level, errors, total_levels):
        """检查关卡完成成就"""
        if level == 0:
            self.unlock('first_level')
        if errors == 0:
            self.unlock('no_errors')
        # 检查是否完成所有关卡
        if level >= total_levels - 1:
            self.unlock('all_levels')

    def check_time_based(self):
        """检查基于时间的成就"""
        from datetime import datetime
        hour = datetime.now().hour
        if hour < 7:
            self.unlock('early_bird')
        elif hour >= 22:
            self.unlock('night_owl')

    def get_pending_notification(self):
        """获取待显示的成就通知"""
        if self.pending_notifications:
            return self.pending_notifications.pop(0)
        return None

    def save_achievements(self):
        """保存成就到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
            with open(self.save_path, 'w') as f:
                json.dump(list(self.unlocked), f)
        except Exception as e:
            print(f"保存成就失败: {e}")

    def load_achievements(self):
        """从文件加载成就"""
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, 'r') as f:
                    self.unlocked = set(json.load(f))
        except Exception as e:
            print(f"加载成就失败: {e}")

    def get_all_achievements(self):
        """获取所有成就及其解锁状态"""
        return [
            {
                'id': aid,
                'unlocked': aid in self.unlocked,
                **info
            }
            for aid, info in self.ACHIEVEMENTS.items()
        ]

    def get_unlocked_count(self):
        """获取已解锁成就数量"""
        return len(self.unlocked)

    def get_total_count(self):
        """获取总成就数量"""
        return len(self.ACHIEVEMENTS)
