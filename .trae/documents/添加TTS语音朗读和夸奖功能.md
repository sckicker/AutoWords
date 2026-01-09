# 添加TTS语音朗读和夸奖功能

## 功能需求
1. 进入游戏界面时朗读英文句子
2. 答对提交时使用英文夸奖（awesome, good, excellent等）

## 实现方案

### 1. 安装pyttsx3库
- 使用跨平台的TTS库pyttsx3
- 支持离线使用，无需网络连接
- 可以控制语速、音量、语音选择

### 2. 在config.py中添加TTS配置
- TTS开关控制
- 语速设置
- 音量设置
- 夸奖语列表

### 3. 在main.py中实现TTS功能
- 初始化TTS引擎
- 添加朗读句子的方法
- 添加朗读夸奖的方法
- 在加载句子时自动朗读
- 在完成句子时随机选择并朗读夸奖

### 4. 夸奖语列表
- Awesome!
- Excellent!
- Great job!
- Perfect!
- Well done!
- Fantastic!
- Outstanding!
- Brilliant!
- Superb!
- Magnificent!
- Splendid!

## 修改文件
- [config.py](file:///Users/sckicker/Documents/AutoWords/config.py) - 添加TTS配置
- [main.py](file:///Users/sckicker/Documents/AutoWords/main.py) - 实现TTS功能
- requirements.txt - 添加pyttsx3依赖

## 预期效果
- 进入游戏界面时自动朗读当前句子
- 完成句子时随机选择夸奖语并朗读
- 增强游戏互动性和学习效果