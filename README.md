# AutoWords - 新概念英语打字游戏

一个专为青少年设计的英文单词学习游戏，帮助学习新概念英语中的单词和句子，通过打字练习提高键盘熟练度和英语水平。

## 功能特点

### 核心功能
- 闯关模式学习新概念英语课程
- 实时准确率和速度统计
- 时间限制挑战
- 分数系统激励学习
- 精美的游戏界面和视觉效果

### 语音朗读系统
- 自动朗读当前句子
- 单词级朗读支持
- 点击单词即可朗读该单词
- 支持快捷键控制朗读

### 趣味性增强
- **等级系统**: 10个等级，从"英语小白"到"超越者"
- **经验值系统**: 输入字符、完成句子、完成关卡都能获得经验
- **连击系统 (Combo)**: 连续正确输入获得连击加成
- **排行榜**: 每日排行、每周排行、总排行
- **每日挑战**: 速度挑战、准确率挑战、连击挑战、单词马拉松
- **成就系统**: 13个成就等你解锁

### 视觉效果
- 粒子特效
- 屏幕抖动反馈
- 星空背景动画
- 渐变色彩效果

### 音效系统
- 程序生成的打字音效（啪啪啪）
- 正确/错误反馈音效
- 关卡完成音效

## 安装说明

1. 确保安装了 Python 3.8+
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行游戏：
   ```bash
   python main.py
   ```

## 依赖项

- pygame - 游戏引擎
- pyttsx3 - 文字转语音
- numpy - 音效生成

## 游戏玩法

1. 在主菜单选择关卡
2. 正确输入屏幕上的英文句子
3. 在时间限制内完成输入
4. 准确率和速度越高，得分越高
5. 完成所有句子进入下一关
6. 积累经验值提升等级

## 控制说明

| 按键 | 功能 |
|------|------|
| 数字键 1-8 | 选择关卡 |
| 字母/符号键 | 输入字符 |
| 回车键 | 确认当前句子 |
| 退格键 | 删除最后一个字符 |
| 空格键 | 朗读当前句子 |
| Tab键 | 朗读当前单词 |
| 鼠标点击单词 | 朗读该单词 |
| ESC | 返回菜单 |
| N | 下一关 (关卡完成时) |
| M | 返回菜单 |
| R | 重新开始 (游戏结束时) |
| F11 | 切换全屏/窗口模式 |

## 项目结构

```
AutoWords/
├── main.py                 # 程序入口和游戏主逻辑
├── config.py               # 配置文件
├── lessons.py              # 课程数据（旧格式，兼容用）
├── requirements.txt        # 依赖项
├── README.md               # 说明文档
│
├── src/                    # 源代码模块
│   ├── __init__.py
│   ├── sound.py            # 音效生成器
│   ├── achievement.py      # 成就系统
│   ├── level_system.py     # 等级/经验系统
│   ├── leaderboard.py      # 排行榜系统
│   └── daily_challenge.py  # 每日挑战系统
│
├── data/                   # 数据文件
│   ├── lessons/
│   │   ├── loader.py       # 课程数据加载器
│   │   ├── new_concept/    # 新概念英语课程 (JSON)
│   │   └── custom/         # 自定义课程
│   └── user/               # 用户数据
│       ├── progress.json
│       ├── achievements.json
│       └── leaderboard.json
│
├── spider/                 # 爬虫模块（扩展词库用）
│   ├── base.py             # 爬虫基类
│   ├── sentences.py        # 例句爬虫
│   └── vocabulary.py       # 词汇爬虫
│
└── assets/                 # 资源文件
    └── audio/              # 音频文件
```

## 等级系统

| 等级 | 称号 | 经验值需求 |
|------|------|-----------|
| 1 | 英语小白 | 0 |
| 2 | 学习新手 | 100 |
| 3 | 勤奋学生 | 300 |
| 4 | 英语达人 | 600 |
| 5 | 单词专家 | 1000 |
| 6 | 语言大师 | 1500 |
| 7 | 打字冠军 | 2100 |
| 8 | 传奇 | 2800 |
| 9 | 神话 | 3600 |
| 10 | 超越者 | 4500 |

## 成就列表

- First Steps - 完成第一个关卡
- Perfect! - 一句话100%准确率
- Speed Demon - 打字速度超过60字符/分钟
- Speed Demon Pro - 打字速度超过100字符/分钟
- On a Roll - 达到5连击
- Unstoppable - 达到10连击
- Legendary - 达到20连击
- Champion - 完成所有关卡
- Flawless - 零错误完成一个关卡
- Early Bird - 早上7点前练习
- Night Owl - 晚上10点后练习
- Weekly Dedication - 连续7天登录
- Monthly Master - 连续30天登录

## 每日挑战

每天系统会随机生成一个挑战：

- **速度挑战**: 30秒内输入尽可能多的字符
- **准确率挑战**: 以100%准确率完成5个句子
- **连击挑战**: 达到30连击
- **单词马拉松**: 正确输入100个单词
- **耐力测试**: 连续输入5分钟

完成挑战可获得额外经验值和分数加成！

## 扩展词库

使用内置爬虫脚本扩展词库：

```bash
# 爬取 Tatoeba 例句
python -m spider.sentences

# 生成词汇练习
python -m spider.vocabulary
```

## 自定义课程

在 `data/lessons/custom/` 目录下创建 JSON 文件，格式如下：

```json
{
    "meta": {
        "source": "Custom",
        "version": "1.0"
    },
    "lessons": [
        {
            "level": 1,
            "title": "My Custom Lesson",
            "difficulty": 1,
            "words": ["word1", "word2"],
            "sentences": [
                {"text": "This is a sentence.", "translation": "这是一个句子。"}
            ]
        }
    ]
}
```

## 配置

编辑 `config.py` 文件自定义游戏设置：

- `TTS_ENABLED`: 是否启用语音朗读
- `TTS_WORD_ENABLED`: 是否启用单词朗读
- `TTS_CLICK_TO_SPEAK`: 是否启用点击朗读
- `MUSIC_VOLUME`: 音乐音量
- `SFX_VOLUME`: 音效音量
- `TIME_LIMIT_PER_SENTENCE`: 每句话时间限制

## 开发

游戏使用 Python 和 Pygame 库开发，界面精美，适合青少年使用。

### 技术栈
- Python 3.8+
- Pygame - 游戏引擎
- pyttsx3 - 文字转语音
- NumPy - 音效合成

### 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
