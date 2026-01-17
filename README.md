# AutoWords - English Typing Game for Teenagers
# AutoWords - 青少年英语打字学习游戏

A fun and educational typing game designed to help teenagers learn English vocabulary while improving their keyboard skills.

一款专为青少年设计的趣味英语打字学习游戏，在提高键盘技能的同时学习英文单词。

---

## Overview 概述

AutoWords combines typing practice with English vocabulary learning through an engaging game interface. Features include level progression, achievements, daily challenges, and leaderboards to keep learners motivated.

AutoWords 通过精美的游戏界面将打字练习与英语词汇学习相结合。包含等级进阶、成就系统、每日挑战和排行榜等功能，保持学习者的学习动力。

---

## Features 功能特点

### Core Gameplay 核心玩法
- **Level-based Learning** (闯关学习) - Progress through lessons from New Concept English
- **Real-time Feedback** (实时反馈) - Instant accuracy and speed statistics
- **Combo System** (连击系统) - Chain correct inputs for bonus points
- **Time Challenge** (限时挑战) - Complete sentences within the time limit

### TTS System 语音朗读系统
- **Auto-read Sentences** (自动朗读句子) - Hear the sentence when it appears
- **Click-to-Speak** (点击朗读) - Click any word to hear its pronunciation
- **Keyboard Shortcuts** (快捷键控制) - F1 to read sentence, F2 to read current word

### Gamification 游戏化元素
- **Experience & Levels** (经验值与等级) - Gain EXP and level up from Beginner to Transcendent
- **Daily Challenges** (每日挑战) - Speed, accuracy, combo, and marathon challenges
- **Leaderboard** (排行榜) - Daily, weekly, and all-time rankings
- **Achievements** (成就系统) - 13 achievements to unlock

### Visual Effects 视觉效果
- **Particle Effects** (粒子特效) - Celebrate correct inputs with particles
- **Screen Shake** (屏幕抖动) - Feedback for errors
- **Starfield Background** (星空背景) - Animated background

### Sound System 音效系统
- **Typing Sounds** (打字音效) - Satisfying "click" sounds when typing
- **Feedback Sounds** (反馈音效) - Different sounds for correct/incorrect inputs
- **Level Complete** (关卡完成) - Celebratory chord on completion

---

## Installation 安装指南

### Prerequisites 前置要求
- Python 3.8 or higher
- pip package manager

### Dependencies 依赖项
```bash
pip install -r requirements.txt
```

Required packages:
- `pygame` - Game engine (游戏引擎)
- `pyttsx3` - Text-to-Speech (文字转语音)
- `numpy` - Sound generation (音效生成)

### Quick Start 快速开始
```bash
# Install dependencies (安装依赖)
pip install -r requirements.txt

# Run the game (运行游戏)
python main.py
```

---

## How to Play 游戏玩法

1. **Select a Course** (选择课程) - Press number keys 1-9 to select a lesson
2. **Type the Sentence** (输入句子) - Type the English sentence shown on screen
3. **Complete Before Time Runs Out** (限时完成) - Finish within the time limit
4. **Earn Points** (获得分数) - Higher accuracy and speed = more points
5. **Level Up** (升级) - Gain experience and unlock new titles

### Basic Controls 基本操作

| Key 按键 | Function 功能 |
|----------|---------------|
| `↑/↓` | Navigate menu 菜单导航 |
| `1-9` | Quick select 快速选择 |
| `Enter` | Confirm / Start 确认/开始 |
| `Backspace` | Delete character 删除字符 |
| `F1` | Read sentence 朗读句子 |
| `F2` | Read current word 朗读当前单词 |
| `Click word` | Speak that word 点击朗读单词 |
| `ESC` | Back to menu / Exit 返回菜单/退出 |
| `F11` | Toggle fullscreen 切换全屏 |
| `N` | Next level (after completion) 下一关 |
| `R` | Restart (after game over) 重新开始 |

---

## Level System 等级系统

| Level 等级 | Title 称号 | EXP Required 所需经验 |
|------------|-----------|----------------------|
| 1 | Beginner 英语小白 | 0 |
| 2 | Learner 学习新手 | 100 |
| 3 | Student 勤奋学生 | 300 |
| 4 | Scholar 英语达人 | 600 |
| 5 | Expert 单词专家 | 1,000 |
| 6 | Master 语言大师 | 1,500 |
| 7 | Champion 打字冠军 | 2,100 |
| 8 | Legend 传奇 | 2,800 |
| 9 | Mythic 神话 | 3,600 |
| 10 | Transcendent 超越者 | 4,500 |

### Earning Experience 获取经验值
- Correct character 正确字符: +1 EXP
- Complete sentence 完成句子: +10 EXP (Perfect: +15 EXP)
- Complete level 完成关卡: +50 EXP
- Combo bonus 连击奖励: combo × 0.5 EXP

---

## Achievements 成就列表

| Achievement 成就 | Description 描述 |
|-----------------|-----------------|
| First Steps | Complete your first level 完成第一个关卡 |
| Perfect! | 100% accuracy on a sentence 句子100%准确率 |
| Speed Demon | Type faster than 60 chars/min 打字速度超过60字符/分钟 |
| Speed Demon Pro | Type faster than 100 chars/min 打字速度超过100字符/分钟 |
| On a Roll | Reach a 5x combo 达到5连击 |
| Unstoppable | Reach a 10x combo 达到10连击 |
| Legendary | Reach a 20x combo 达到20连击 |
| Champion | Complete all levels 完成所有关卡 |
| Flawless | Complete a level with no errors 零错误完成关卡 |
| Early Bird | Practice before 7am 早上7点前练习 |
| Night Owl | Practice after 10pm 晚上10点后练习 |
| Weekly Dedication | 7 days login streak 连续7天登录 |
| Monthly Master | 30 days login streak 连续30天登录 |

---

## Daily Challenges 每日挑战

The game features rotating daily challenges with bonus rewards:

每天系统会轮换不同的挑战，完成后可获得额外奖励：

| Challenge 挑战 | Goal 目标 |
|---------------|----------|
| Speed Challenge 速度挑战 | Type as many characters as possible in 30 seconds 30秒内输入尽可能多的字符 |
| Accuracy Challenge 准确率挑战 | Complete 5 sentences with 100% accuracy 以100%准确率完成5个句子 |
| Combo Challenge 连击挑战 | Reach a 30x combo streak 达到30连击 |
| Word Marathon 单词马拉松 | Type 100 words correctly 正确输入100个单词 |
| Endurance Test 耐力测试 | Type continuously for 5 minutes 连续输入5分钟 |

**Rewards 奖励**: Bronze (+50 EXP), Silver (+75 EXP), Gold (+100 EXP)

---

## Project Structure 项目结构

```
AutoWords/
├── main.py                 # Main game entry (游戏入口)
├── config.py               # Configuration (配置文件)
├── lessons.py              # Legacy lesson data (旧课程数据)
├── requirements.txt        # Dependencies (依赖项)
├── README.md               # Documentation (说明文档)
│
├── src/                    # Source modules (源代码模块)
│   ├── __init__.py
│   ├── sound.py            # Sound generator (音效生成器)
│   ├── achievement.py      # Achievement system (成就系统)
│   ├── level_system.py     # Level/EXP system (等级经验系统)
│   ├── leaderboard.py      # Leaderboard system (排行榜系统)
│   └── daily_challenge.py  # Daily challenges (每日挑战)
│
├── data/                   # Data files (数据文件)
│   ├── lessons/
│   │   ├── loader.py       # JSON loader (JSON加载器)
│   │   ├── new_concept/    # New Concept English (新概念英语)
│   │   └── custom/         # Custom courses (自定义课程)
│   └── user/               # User data (用户数据)
│       ├── progress.json
│       ├── achievements.json
│       └── leaderboard.json
│
├── spider/                 # Web crawler (爬虫模块)
│   ├── base.py             # Base crawler (爬虫基类)
│   ├── sentences.py        # Sentence crawler (例句爬虫)
│   └── vocabulary.py       # Vocabulary crawler (词汇爬虫)
│
└── assets/                 # Assets (资源文件)
    └── audio/
```

---

## Customization 自定义

### Adding Custom Courses 添加自定义课程

Create a JSON file in `data/lessons/custom/` with the following format:

在 `data/lessons/custom/` 目录下创建 JSON 文件，格式如下：

```json
{
    "meta": {
        "source": "Custom Course",
        "version": "1.0",
        "description": "My custom English lessons"
    },
    "lessons": [
        {
            "level": 1,
            "title": "Lesson 1 - Greetings",
            "difficulty": 1,
            "words": ["hello", "goodbye", "please", "thank"],
            "sentences": [
                {"text": "Hello, how are you?", "translation": "你好，你好吗？"},
                {"text": "Thank you very much.", "translation": "非常感谢。"}
            ]
        }
    ]
}
```

### Expanding Vocabulary with Spider 使用爬虫扩展词库

```bash
# Crawl sentences from Tatoeba (从Tatoeba爬取例句)
python -m spider.sentences

# Generate vocabulary lessons (生成词汇课程)
python -m spider.vocabulary
```

---

## Configuration 配置说明

Edit `config.py` to customize settings:

编辑 `config.py` 自定义游戏设置：

```python
# TTS Settings (语音设置)
TTS_ENABLED = True          # Enable TTS (启用语音)
TTS_WORD_ENABLED = True     # Enable word reading (启用单词朗读)
TTS_CLICK_TO_SPEAK = True   # Enable click-to-speak (启用点击朗读)
TTS_RATE = 150              # Speech rate (语速)

# Audio Settings (音频设置)
MUSIC_VOLUME = 0.5          # Music volume (音乐音量)
SFX_VOLUME = 0.7            # Sound effects volume (音效音量)

# Game Settings (游戏设置)
TIME_LIMIT_PER_SENTENCE = 30    # Time limit per sentence (每句时限)
MIN_ACCURACY_FOR_PASS = 80      # Minimum accuracy to pass (最低通过准确率)
MAX_ERRORS_PER_LEVEL = 5        # Maximum errors allowed (最大错误数)
```

---

## Tech Stack 技术栈

- **Python 3.8+** - Programming language
- **Pygame** - Game engine and graphics
- **pyttsx3** - Text-to-Speech engine
- **NumPy** - Programmatic sound generation

---

## Contributing 贡献指南

Contributions are welcome! Please feel free to submit issues and pull requests.

欢迎贡献！请随时提交 Issue 和 Pull Request。

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License 许可证

This project is licensed under the MIT License.

本项目采用 MIT 许可证。

---

## Acknowledgments 致谢

- New Concept English for lesson content (新概念英语课程内容)
- Tatoeba for example sentences (CC BY 2.0) (Tatoeba例句库)
- Pygame community for the game engine (Pygame社区)
