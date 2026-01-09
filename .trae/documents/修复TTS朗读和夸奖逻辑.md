# 修复TTS朗读和夸奖逻辑

## 问题分析
1. 每一句都要读 - 当前实现正确，在next_sentence()中调用
2. 夸奖位置错误 - 当前在提交时夸奖，应该在切换页面（加载下一句）时夸奖
3. 错误时需要鼓励 - 当前没有错误鼓励功能

## 修改方案

### 1. 在config.py中添加鼓励语列表
- 添加ENCOURAGEMENT_PHRASES列表
- 用于错误时朗读的鼓励语
- 例如：Keep trying, Don't give up, You can do it等

### 2. 修改夸奖逻辑
- 将speak_praise()从提交时移到切换页面时
- 在next_sentence()开始时调用speak_praise()
- 这样每次加载新句子时都会先夸奖上一句

### 3. 添加错误鼓励功能
- 在handle_input()的错误分支中添加鼓励语朗读
- 使用speak_encouragement()方法
- 随机选择鼓励语

## 修改文件
- [config.py](file:///Users/sckicker/Documents/AutoWords/config.py) - 添加鼓励语列表
- [main.py](file:///Users/sckicker/Documents/AutoWords/main.py) - 修改夸奖逻辑和添加鼓励功能

## 预期效果
- 每加载一句新句子时先朗读句子
- 完成句子后，切换到下一句时朗读夸奖语
- 输入错误时朗读鼓励语
- 增强学习体验和互动性