"""
每日挑战系统模块
提供每日轮换的特殊挑战
"""
import json
import os
from datetime import datetime, date
import random


class DailyChallenge:
    """每日挑战系统"""

    CHALLENGE_TYPES = {
        'speed': {
            'name': 'Speed Challenge',
            'title': '速度挑战',
            'description': 'Type as many characters as possible in 30 seconds',
            'description_cn': '30秒内输入尽可能多的字符',
            'icon': '⚡',
            'time_limit': 30,
            'goal_type': 'chars',
            'goals': [50, 80, 120]  # 铜、银、金目标
        },
        'accuracy': {
            'name': 'Accuracy Challenge',
            'title': '准确率挑战',
            'description': 'Complete 5 sentences with 100% accuracy',
            'description_cn': '以100%准确率完成5个句子',
            'icon': '🎯',
            'time_limit': 180,
            'goal_type': 'sentences',
            'goals': [3, 4, 5]
        },
        'combo': {
            'name': 'Combo Challenge',
            'title': '连击挑战',
            'description': 'Reach a 30x combo streak',
            'description_cn': '达到30连击',
            'icon': '🔥',
            'time_limit': 120,
            'goal_type': 'combo',
            'goals': [15, 25, 30]
        },
        'marathon': {
            'name': 'Word Marathon',
            'title': '单词马拉松',
            'description': 'Type 100 words correctly',
            'description_cn': '正确输入100个单词',
            'icon': '🏃',
            'time_limit': 300,
            'goal_type': 'words',
            'goals': [50, 75, 100]
        },
        'endurance': {
            'name': 'Endurance Test',
            'title': '耐力测试',
            'description': 'Type continuously for 5 minutes',
            'description_cn': '连续输入5分钟不停止',
            'icon': '💪',
            'time_limit': 300,
            'goal_type': 'time',
            'goals': [180, 240, 300]
        }
    }

    # 奖励配置
    REWARDS = {
        'bronze': {'exp': 50, 'score_multiplier': 1.2},
        'silver': {'exp': 75, 'score_multiplier': 1.35},
        'gold': {'exp': 100, 'score_multiplier': 1.5}
    }

    def __init__(self, save_path='data/user/daily_challenge.json'):
        self.save_path = save_path
        self.today_challenge = None
        self.challenge_progress = {}
        self.completed_today = False
        self.reward_tier = None  # bronze, silver, gold
        self.load_state()
        self._ensure_today_challenge()

    def _ensure_today_challenge(self):
        """确保今日挑战已生成"""
        today = date.today().isoformat()

        if self.today_challenge is None or self.today_challenge.get('date') != today:
            # 生成新的每日挑战
            self._generate_today_challenge()

    def _generate_today_challenge(self):
        """生成今日挑战（基于日期的伪随机）"""
        today = date.today()
        # 使用日期作为随机种子，确保同一天生成相同挑战
        random.seed(today.toordinal())

        challenge_type = random.choice(list(self.CHALLENGE_TYPES.keys()))
        challenge_info = self.CHALLENGE_TYPES[challenge_type].copy()

        self.today_challenge = {
            'date': today.isoformat(),
            'type': challenge_type,
            'info': challenge_info
        }

        # 重置进度
        self.challenge_progress = {
            'chars': 0,
            'words': 0,
            'sentences': 0,
            'combo': 0,
            'max_combo': 0,
            'time': 0,
            'errors': 0,
            'started': False,
            'start_time': None
        }
        self.completed_today = False
        self.reward_tier = None

        # 恢复随机状态
        random.seed()

        self.save_state()

    def get_today_challenge(self):
        """获取今日挑战信息"""
        self._ensure_today_challenge()
        return self.today_challenge

    def start_challenge(self):
        """开始挑战"""
        self._ensure_today_challenge()
        self.challenge_progress['started'] = True
        self.challenge_progress['start_time'] = datetime.now().isoformat()
        self.save_state()

    def update_progress(self, chars=0, words=0, sentences=0, combo=0, errors=0):
        """更新挑战进度"""
        if not self.challenge_progress.get('started') or self.completed_today:
            return None

        self.challenge_progress['chars'] += chars
        self.challenge_progress['words'] += words
        self.challenge_progress['sentences'] += sentences
        self.challenge_progress['errors'] += errors

        # 更新连击（保存最大值）
        if combo > self.challenge_progress['max_combo']:
            self.challenge_progress['max_combo'] = combo

        # 更新已用时间
        if self.challenge_progress['start_time']:
            start = datetime.fromisoformat(self.challenge_progress['start_time'])
            self.challenge_progress['time'] = (datetime.now() - start).total_seconds()

        # 检查是否完成
        result = self._check_completion()
        self.save_state()

        return result

    def _check_completion(self):
        """检查是否完成挑战"""
        if self.completed_today:
            return None

        challenge = self.today_challenge
        if not challenge:
            return None

        challenge_type = challenge['type']
        info = challenge['info']
        goals = info['goals']
        goal_type = info['goal_type']
        time_limit = info['time_limit']

        # 检查是否超时
        elapsed = self.challenge_progress.get('time', 0)
        if elapsed > time_limit:
            # 超时，检查是否达到任何目标
            return self._evaluate_result(goal_type, goals)

        # 获取当前进度值
        if goal_type == 'chars':
            current = self.challenge_progress['chars']
        elif goal_type == 'words':
            current = self.challenge_progress['words']
        elif goal_type == 'sentences':
            # 准确率挑战需要无错误
            if self.challenge_progress['errors'] > 0:
                return None
            current = self.challenge_progress['sentences']
        elif goal_type == 'combo':
            current = self.challenge_progress['max_combo']
        elif goal_type == 'time':
            current = elapsed
        else:
            current = 0

        # 检查是否达到金牌目标
        if current >= goals[2]:
            self.completed_today = True
            self.reward_tier = 'gold'
            return self._get_reward('gold')

        return None

    def _evaluate_result(self, goal_type, goals):
        """评估最终结果"""
        if goal_type == 'chars':
            current = self.challenge_progress['chars']
        elif goal_type == 'words':
            current = self.challenge_progress['words']
        elif goal_type == 'sentences':
            current = self.challenge_progress['sentences']
        elif goal_type == 'combo':
            current = self.challenge_progress['max_combo']
        elif goal_type == 'time':
            current = self.challenge_progress['time']
        else:
            current = 0

        if current >= goals[2]:
            self.reward_tier = 'gold'
        elif current >= goals[1]:
            self.reward_tier = 'silver'
        elif current >= goals[0]:
            self.reward_tier = 'bronze'
        else:
            self.reward_tier = None

        if self.reward_tier:
            self.completed_today = True
            return self._get_reward(self.reward_tier)

        return None

    def _get_reward(self, tier):
        """获取奖励"""
        reward = self.REWARDS[tier].copy()
        reward['tier'] = tier
        reward['challenge'] = self.today_challenge['info']['title']
        return reward

    def get_progress_display(self):
        """获取进度显示信息"""
        if not self.today_challenge:
            return None

        info = self.today_challenge['info']
        goal_type = info['goal_type']
        goals = info['goals']

        if goal_type == 'chars':
            current = self.challenge_progress['chars']
            unit = '字符'
        elif goal_type == 'words':
            current = self.challenge_progress['words']
            unit = '单词'
        elif goal_type == 'sentences':
            current = self.challenge_progress['sentences']
            unit = '句子'
        elif goal_type == 'combo':
            current = self.challenge_progress['max_combo']
            unit = '连击'
        elif goal_type == 'time':
            current = int(self.challenge_progress.get('time', 0))
            unit = '秒'
        else:
            current = 0
            unit = ''

        # 计算进度百分比（相对于金牌目标）
        gold_goal = goals[2]
        progress_pct = min(100, (current / gold_goal) * 100)

        # 剩余时间
        time_limit = info['time_limit']
        elapsed = self.challenge_progress.get('time', 0)
        remaining = max(0, time_limit - elapsed)

        return {
            'current': current,
            'goals': goals,
            'unit': unit,
            'progress_pct': progress_pct,
            'time_remaining': remaining,
            'completed': self.completed_today,
            'reward_tier': self.reward_tier
        }

    def is_challenge_active(self):
        """检查挑战是否进行中"""
        return (self.challenge_progress.get('started', False)
                and not self.completed_today
                and self.challenge_progress.get('time', 0) < self.today_challenge['info']['time_limit'])

    def save_state(self):
        """保存状态"""
        try:
            os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
            data = {
                'today_challenge': self.today_challenge,
                'challenge_progress': self.challenge_progress,
                'completed_today': self.completed_today,
                'reward_tier': self.reward_tier
            }
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"保存每日挑战状态失败: {e}")

    def load_state(self):
        """加载状态"""
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                    self.today_challenge = data.get('today_challenge')
                    self.challenge_progress = data.get('challenge_progress', {})
                    self.completed_today = data.get('completed_today', False)
                    self.reward_tier = data.get('reward_tier')
        except Exception as e:
            print(f"加载每日挑战状态失败: {e}")
