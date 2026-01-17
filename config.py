"""游戏配置文件"""

# 游戏设置
GAME_TITLE = "AutoWords - 新概念英语打字游戏"
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# 颜色定义
COLORS = {
    'BACKGROUND': (25, 25, 50),
    'BACKGROUND_TOP': (30, 30, 60),
    'BACKGROUND_BOTTOM': (20, 20, 40),
    'TEXT': (220, 220, 220),
    'CORRECT': (100, 255, 100),
    'INCORRECT': (255, 100, 100),
    'INPUT': (70, 70, 100),
    'INPUT_BG': (40, 40, 60),  # 输入框背景色
    'HIGHLIGHT': (100, 150, 255),
    'UI': (100, 100, 150),
    'PROGRESS': (70, 130, 180),
    'PROGRESS_BG': (50, 50, 70),
    'WARNING': (255, 200, 50),
    # 3D效果颜色
    'SHADOW_DARK': (10, 10, 20),
    'SHADOW_LIGHT': (35, 35, 70),
    'HIGHLIGHT_LIGHT': (150, 150, 200),
    'GLOW': (80, 120, 200),
    'TEXT_SHADOW': (15, 15, 30)
}

# 游戏参数
TIME_LIMIT_PER_SENTENCE = 30  # 每个句子的时间限制（秒）
MIN_ACCURACY_FOR_PASS = 80    # 通过关卡所需的最低准确率
MAX_ERRORS_PER_LEVEL = 5      # 每个关卡允许的最大错误数
SCORE_PER_CORRECT_CHAR = 10   # 每个正确字符的基础分数
SPEED_BONUS_THRESHOLD = 30    # 达到速度奖励的阈值（字符/分钟

# 字体设置
FONTS = {
    'LARGE': 48,
    'MEDIUM': 36,
    'SMALL': 24
}

# 关卡设置
LEVEL_COMPLETION_BONUS = 100  # 完成关卡的奖励分数
LEVEL_NUMBER_MULTIPLIER = 50  # 关卡数乘数（影响分数）

# 音乐和音效设置
MUSIC_ENABLED = True
MUSIC_VOLUME = 0.5  # 音乐音量 (0.0 - 1.0)
SFX_VOLUME = 0.7  # 音效音量 (0.0 - 1.0)

# TTS语音朗读设置
TTS_ENABLED = True  # 是否启用TTS语音朗读
TTS_RATE = 150  # 语速（每分钟单词数）
TTS_VOLUME = 0.8  # TTS音量 (0.0 - 1.0)
TTS_WORD_ENABLED = True  # 是否启用单词朗读
TTS_CLICK_TO_SPEAK = True  # 是否启用点击朗读

# 夸奖语列表
PRAISE_PHRASES = [
    "Awesome!",
    "Excellent!",
    "Great job!",
    "Perfect!",
    "Well done!",
    "Fantastic!",
    "Outstanding!",
    "Brilliant!",
    "Superb!",
    "Magnificent!",
    "Splendid!",
    "Amazing!",
    "Wonderful!",
    "Incredible!",
    "Marvelous!"
]

# 鼓励语列表（用于错误时）
ENCOURAGEMENT_PHRASES = [
    "Keep trying!",
    "Don't give up!",
    "You can do it!",
    "Almost there!",
    "Keep going!",
    "Try again!",
    "You're doing great!",
    "Stay focused!",
    "Don't worry!",
    "Take your time!",
    "Believe in yourself!",
    "Keep practicing!",
    "You're getting better!",
    "Stay positive!"
]

# 音乐文件路径（用户可以替换为自己的音乐文件）
BACKGROUND_MUSIC = "background.mp3"  # 背景音乐文件
TYPE_SOUND = "type.wav"  # 打字音效
CORRECT_SOUND = "correct.wav"  # 正确音效
ERROR_SOUND = "error.wav"  # 错误音效
COMPLETE_SOUND = "complete.wav"  # 完成音效