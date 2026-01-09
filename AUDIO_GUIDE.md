# 音频文件说明

## 如何添加背景音乐和音效

本游戏支持背景音乐和音效，让游戏体验更加丰富！

### 支持的音频文件
- 背景音乐：MP3, OGG, WAV 格式
- 音效：WAV, OGG 格式

### 音频文件列表

在游戏目录中添加以下音频文件：

1. **background.mp3** - 背景音乐
   - 循环播放的背景音乐
   - 建议使用轻快、不干扰打字的背景音乐
   - 音量：0.5（可在 config.py 中调整）

2. **type.wav** - 打字音效
   - 每次打字时播放
   - 建议使用短促、清脆的音效
   - 音量：0.7（可在 config.py 中调整）

3. **correct.wav** - 正确音效
   - 输入正确字符时播放
   - 建议使用愉悦、积极的音效
   - 音量：0.7（可在 config.py 中调整）

4. **error.wav** - 错误音效
   - 输入错误字符时播放
   - 建议使用温和的提示音效
   - 音量：0.7（可在 config.py 中调整）

5. **complete.wav** - 完成音效
   - 完成句子或关卡时播放
   - 建议使用庆祝、成功的音效
   - 音量：0.7（可在 config.py 中调整）

### 音频设置

在 `config.py` 中可以调整以下设置：

```python
# 音乐和音效设置
MUSIC_ENABLED = True      # 是否启用音乐（True/False）
MUSIC_VOLUME = 0.5        # 音乐音量 (0.0 - 1.0)
SFX_VOLUME = 0.7          # 音效音量 (0.0 - 1.0)
```

### 获取免费音频资源

以下是一些免费音频资源网站：

1. **Freesound** - https://freesound.org/
   - 大量免费音效
   - 需要注册账户
   - 搜索关键词：typing, click, success, error

2. **OpenGameArt** - https://opengameart.org/
   - 游戏音频资源
   - 免费使用
   - 包含背景音乐和音效

3. **Incompetech** - https://incompetech.com/
   - Kevin MacLeod 的免费音乐
   - 可用于商业项目
   - 需要署名

4. **Zapsplat** - https://www.zapsplat.com/
   - 免费音效库
   - 需要注册
   - 每月免费下载额度

### 音频文件示例

如果你没有音频文件，游戏仍然可以正常运行，只是没有声音。

### 注意事项

1. 音频文件必须放在游戏根目录（与 main.py 同级）
2. 文件名必须与配置中的名称完全一致
3. 建议使用 WAV 格式的音效，兼容性更好
4. 背景音乐建议使用 MP3 或 OGG 格式
5. 音频文件不宜过大，以免影响游戏加载速度

### 禁用音乐

如果不想使用音乐，可以在 `config.py` 中设置：

```python
MUSIC_ENABLED = False
```

游戏将静音运行。