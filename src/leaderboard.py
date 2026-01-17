"""
排行榜系统模块
管理本地排行榜
"""
import json
import os
from datetime import datetime, timedelta


class Leaderboard:
    """本地排行榜系统"""

    def __init__(self, save_path='data/user/leaderboard.json'):
        self.save_path = save_path
        self.data = {
            'daily': [],
            'weekly': [],
            'all_time': []
        }
        self.load()

    def add_score(self, player_name, score, accuracy, speed, combo, level):
        """添加新分数记录"""
        entry = {
            'name': player_name,
            'score': score,
            'accuracy': accuracy,
            'speed': speed,
            'combo': combo,
            'level': level,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S')
        }

        # 添加到各个排行榜
        self.data['daily'].append(entry)
        self.data['weekly'].append(entry)
        self.data['all_time'].append(entry)

        # 清理过期数据并排序
        self._cleanup_and_sort()
        self.save()

        # 返回玩家在各排行榜中的排名
        return {
            'daily': self._get_rank(player_name, score, 'daily'),
            'weekly': self._get_rank(player_name, score, 'weekly'),
            'all_time': self._get_rank(player_name, score, 'all_time')
        }

    def _cleanup_and_sort(self):
        """清理过期数据并排序"""
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)

        # 清理每日排行（只保留今天的）
        self.data['daily'] = [
            e for e in self.data['daily']
            if datetime.strptime(e['date'], '%Y-%m-%d').date() == today
        ]

        # 清理每周排行（只保留7天内的）
        self.data['weekly'] = [
            e for e in self.data['weekly']
            if datetime.strptime(e['date'], '%Y-%m-%d').date() >= week_ago
        ]

        # 排序（按分数降序）
        for category in self.data:
            self.data[category].sort(key=lambda x: x['score'], reverse=True)
            # 只保留前100名
            self.data[category] = self.data[category][:100]

    def _get_rank(self, player_name, score, category):
        """获取玩家在指定排行榜中的排名"""
        for i, entry in enumerate(self.data[category]):
            if entry['name'] == player_name and entry['score'] == score:
                return i + 1
        return None

    def get_top(self, category='daily', limit=10):
        """获取排行榜前N名"""
        return self.data.get(category, [])[:limit]

    def get_player_best(self, player_name, category='all_time'):
        """获取玩家最佳成绩"""
        for entry in self.data.get(category, []):
            if entry['name'] == player_name:
                return entry
        return None

    def get_player_rank(self, player_name, category='daily'):
        """获取玩家当前排名"""
        for i, entry in enumerate(self.data.get(category, [])):
            if entry['name'] == player_name:
                return i + 1
        return None

    def save(self):
        """保存排行榜到文件"""
        try:
            os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
            with open(self.save_path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"保存排行榜失败: {e}")

    def load(self):
        """从文件加载排行榜"""
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, 'r') as f:
                    self.data = json.load(f)
                # 清理过期数据
                self._cleanup_and_sort()
        except Exception as e:
            print(f"加载排行榜失败: {e}")
