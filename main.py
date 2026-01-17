import pygame
import sys
import random
import time
import json
import os
import pyttsx3
import threading
import queue
import numpy as np
from pygame.locals import *
from config import *

# 尝试从新的模块结构导入，否则回退到旧的导入方式
try:
    from src import SoundGenerator, AchievementSystem, LevelSystem, Leaderboard, DailyChallenge
    from data.lessons.loader import LessonLoader
    # 使用新的JSON数据加载器
    lesson_loader = LessonLoader()
    NEW_CONCEPT_LESSONS = lesson_loader.load_all()
    if not NEW_CONCEPT_LESSONS:
        # 如果JSON文件为空，回退到旧的lessons.py
        from lessons import NEW_CONCEPT_LESSONS
except ImportError:
    # 回退到旧的导入方式
    from lessons import NEW_CONCEPT_LESSONS
    # 内联类定义（兼容模式）
    LevelSystem = None
    Leaderboard = None
    DailyChallenge = None

# 初始化Pygame
pygame.init()


class Game:
    def __init__(self):
        # 默认窗口模式，支持调整大小 (Default window mode, resizable)
        self.fullscreen = False
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self._create_display()
            
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        
        # 根据屏幕高度动态调整字体大小
        scale_factor = self.screen_height / 700  # 基于标准高度700px
        font_sizes = {
            'LARGE': int(FONTS['LARGE'] * scale_factor),
            'MEDIUM': int(FONTS['MEDIUM'] * scale_factor),
            'SMALL': int(FONTS['SMALL'] * scale_factor)
        }
        
        # 使用支持中文的字体
        try:
            self.font_large = pygame.font.Font('Arial Unicode.ttf', font_sizes['LARGE'])
        except:
            self.font_large = pygame.font.SysFont('arialunicode', font_sizes['LARGE'])        
        
        try:
            self.font_medium = pygame.font.Font('Arial Unicode.ttf', font_sizes['MEDIUM'])
        except:
            self.font_medium = pygame.font.SysFont('arialunicode', font_sizes['MEDIUM'])
            
        try:
            self.font_small = pygame.font.Font('Arial Unicode.ttf', font_sizes['SMALL'])
        except:
            self.font_small = pygame.font.SysFont('arialunicode', font_sizes['SMALL'])
        
        # Game state
        self.state = "menu"  # menu, course_select, playing, level_complete, game_over, leaderboard, achievements
        self.menu_index = 0  # 主菜单选择索引 (Main menu selection index)
        self.current_level = 0
        self.current_sentence_index = 0
        self.current_sentence = ""
        self.user_input = ""
        self.start_time = 0
        self.time_limit = TIME_LIMIT_PER_SENTENCE  # Time limit per sentence (seconds)
        self.correct_chars = 0
        self.total_chars = 0
        self.errors = 0
        self.score = 0
        self.level_scores = [0] * len(NEW_CONCEPT_LESSONS)
        self.max_errors = MAX_ERRORS_PER_LEVEL  # Maximum number of errors
        
        # Initialize particle system
        self.particles = []
        self.stars = []
        self.init_stars()
        self.frame_count = 0

        # 单词位置记录（用于点击朗读）
        self.word_rects = []

        # 连击系统 (Combo)
        self.combo = 0
        self.max_combo = 0
        self.combo_timer = 0

        # 屏幕抖动效果
        self.screen_shake = 0
        self.screen_shake_intensity = 0

        # 成就系统
        self.achievement_system = AchievementSystem()
        self.current_achievement_notification = None
        self.notification_timer = 0

        # 等级系统
        if LevelSystem:
            self.level_system = LevelSystem()
        else:
            self.level_system = None

        # 排行榜系统
        if Leaderboard:
            self.leaderboard = Leaderboard()
        else:
            self.leaderboard = None

        # 每日挑战系统
        if DailyChallenge:
            self.daily_challenge = DailyChallenge()
        else:
            self.daily_challenge = None

        # Initialize audio system
        pygame.mixer.init()
        self.background_music = None
        self.type_sound = None
        self.correct_sound = None
        self.error_sound = None
        self.complete_sound = None
        
        # Load audio files if enabled
        if MUSIC_ENABLED:
            self.load_audio()
        
        # Initialize TTS engine
        self.init_tts()
        
        # Initialize voice queue and thread
        self.voice_queue = queue.Queue()
        self.voice_thread = None
        self.start_voice_thread()

    def _create_display(self):
        """创建显示窗口 (Create display window)"""
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.screen_width, self.screen_height = pygame.display.get_surface().get_size()
        else:
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                pygame.RESIZABLE
            )

    def toggle_fullscreen(self):
        """切换全屏/窗口模式 (Toggle fullscreen/window mode)"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            # 进入全屏
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.screen_width, self.screen_height = pygame.display.get_surface().get_size()
        else:
            # 恢复窗口模式
            self.screen_width = SCREEN_WIDTH
            self.screen_height = SCREEN_HEIGHT
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                pygame.RESIZABLE
            )
        # 重新计算字体大小
        self._update_fonts()
        # 重新初始化星空背景
        self.init_stars()

    def _update_fonts(self):
        """根据屏幕大小更新字体 (Update fonts based on screen size)"""
        scale_factor = self.screen_height / 700
        font_sizes = {
            'LARGE': int(FONTS['LARGE'] * scale_factor),
            'MEDIUM': int(FONTS['MEDIUM'] * scale_factor),
            'SMALL': int(FONTS['SMALL'] * scale_factor)
        }
        try:
            self.font_large = pygame.font.Font('Arial Unicode.ttf', font_sizes['LARGE'])
        except:
            self.font_large = pygame.font.SysFont('arialunicode', font_sizes['LARGE'])
        try:
            self.font_medium = pygame.font.Font('Arial Unicode.ttf', font_sizes['MEDIUM'])
        except:
            self.font_medium = pygame.font.SysFont('arialunicode', font_sizes['MEDIUM'])
        try:
            self.font_small = pygame.font.Font('Arial Unicode.ttf', font_sizes['SMALL'])
        except:
            self.font_small = pygame.font.SysFont('arialunicode', font_sizes['SMALL'])

    def handle_resize(self, width, height):
        """处理窗口大小变化 (Handle window resize)"""
        self.screen_width = width
        self.screen_height = height
        self._update_fonts()
        self.init_stars()

    def start_voice_thread(self):
        """启动语音播放线程"""
        if TTS_ENABLED:
            self.voice_thread = threading.Thread(target=self.voice_worker, daemon=True)
            self.voice_thread.start()
    
    def voice_worker(self):
        """语音播放工作线程"""
        while True:
            try:
                text = self.voice_queue.get(timeout=0.1)
                if text is None:
                    break
                # 检查 tts_engine 是否存在
                if hasattr(self, 'tts_engine') and self.tts_engine:
                    try:
                        self.tts_engine.say(text)
                        self.tts_engine.runAndWait()
                    except Exception as e:
                        print(f"语音播放失败: {e}")
            except queue.Empty:
                continue
            except Exception as e:
                print(f"语音线程错误: {e}")
                continue
    
    def stop_voice_thread(self):
        """停止语音播放线程"""
        if self.voice_thread:
            self.voice_queue.put(None)
            self.voice_thread.join(timeout=1)
    
    def load_audio(self):
        """加载音频文件，如果文件不存在则使用程序生成的音效"""
        # 初始化打字音效变体列表（用于节奏感）
        self.type_sounds = []

        try:
            # Load background music
            if os.path.exists(BACKGROUND_MUSIC):
                self.background_music = pygame.mixer.music.load(BACKGROUND_MUSIC)
                pygame.mixer.music.set_volume(MUSIC_VOLUME)
        except:
            print("无法加载背景音乐")

        # 打字音效 - 多个变体用于节奏感
        try:
            if os.path.exists(TYPE_SOUND):
                self.type_sound = pygame.mixer.Sound(TYPE_SOUND)
                self.type_sound.set_volume(SFX_VOLUME)
            else:
                # 使用程序生成音效
                self.type_sound = SoundGenerator.generate_type_sound()
                self.type_sound.set_volume(SFX_VOLUME)
                # 生成多个打字音效变体，增加节奏变化
                for _ in range(3):
                    sound = SoundGenerator.generate_type_sound()
                    sound.set_volume(SFX_VOLUME * (0.9 + random.random() * 0.2))
                    self.type_sounds.append(sound)
        except Exception as e:
            print(f"无法加载打字音效: {e}")

        # 正确音效
        try:
            if os.path.exists(CORRECT_SOUND):
                self.correct_sound = pygame.mixer.Sound(CORRECT_SOUND)
            else:
                self.correct_sound = SoundGenerator.generate_correct_sound()
            self.correct_sound.set_volume(SFX_VOLUME)
        except Exception as e:
            print(f"无法加载正确音效: {e}")

        # 错误音效
        try:
            if os.path.exists(ERROR_SOUND):
                self.error_sound = pygame.mixer.Sound(ERROR_SOUND)
            else:
                self.error_sound = SoundGenerator.generate_error_sound()
            self.error_sound.set_volume(SFX_VOLUME)
        except Exception as e:
            print(f"无法加载错误音效: {e}")

        # 完成音效
        try:
            if os.path.exists(COMPLETE_SOUND):
                self.complete_sound = pygame.mixer.Sound(COMPLETE_SOUND)
            else:
                self.complete_sound = SoundGenerator.generate_complete_sound()
            self.complete_sound.set_volume(SFX_VOLUME)
        except Exception as e:
            print(f"无法加载完成音效: {e}")

    def play_type_sound(self):
        """播放打字音效 - 带有随机变化的节奏感"""
        if self.type_sounds:
            # 随机选择一个音效变体
            sound = random.choice(self.type_sounds)
            sound.play()
        elif self.type_sound:
            self.type_sound.play()
    
    def play_correct_sound(self):
        """播放正确音效"""
        if self.correct_sound:
            self.correct_sound.play()
    
    def play_error_sound(self):
        """播放错误音效"""
        if self.error_sound:
            self.error_sound.play()
    
    def play_complete_sound(self):
        """播放完成音效"""
        if self.complete_sound:
            self.complete_sound.play()
    
    def start_background_music(self):
        """开始播放背景音乐"""
        if MUSIC_ENABLED and self.background_music:
            pygame.mixer.music.play(-1, fade_ms=1000)
    
    def stop_background_music(self):
        """停止背景音乐"""
        if MUSIC_ENABLED:
            pygame.mixer.music.stop()
    
    # TTS语音朗读功能
    def init_tts(self):
        """初始化TTS引擎"""
        if TTS_ENABLED:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', TTS_RATE)
                self.tts_engine.setProperty('volume', TTS_VOLUME)
                return True
            except Exception as e:
                print(f"无法初始化TTS引擎: {e}")
                return False
        return False
    
    def speak(self, text):
        """朗读文本（同步）"""
        if TTS_ENABLED and hasattr(self, 'tts_engine'):
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"朗读失败: {e}")
    
    def speak_async(self, text):
        """异步朗读文本"""
        if TTS_ENABLED and hasattr(self, 'tts_engine') and self.voice_thread:
            self.voice_queue.put(text)
    
    def speak_sentence(self):
        """朗读当前句子（异步）"""
        if self.current_sentence:
            self.speak_async(self.current_sentence)

    def speak_word(self, word):
        """朗读单个单词（异步）"""
        if TTS_ENABLED and word:
            # 清理单词中的标点符号
            clean_word = word.strip('.,!?;:"\'-')
            if clean_word:
                self.speak_async(clean_word)

    def speak_current_word(self):
        """朗读当前正在输入的单词"""
        if not self.current_sentence:
            return
        words = self.current_sentence.split()
        # 根据用户输入进度确定当前单词
        input_words = self.user_input.split() if self.user_input else []
        current_word_index = len(input_words)
        if current_word_index < len(words):
            self.speak_word(words[current_word_index])

    def speak_word_by_index(self, index):
        """朗读指定索引的单词"""
        if not self.current_sentence:
            return
        words = self.current_sentence.split()
        if 0 <= index < len(words):
            self.speak_word(words[index])

    def speak_praise(self):
        """朗读夸奖语（异步）- 根据连击数选择不同级别的夸奖"""
        if self.combo >= 10:
            # 高连击使用更激动的夸奖
            super_praise = ["Incredible!", "Amazing!", "You're on fire!", "Unstoppable!", "Legendary!"]
            praise = random.choice(super_praise)
        elif self.combo >= 5:
            praise = random.choice(["Great job!", "Excellent!", "Wonderful!", "Fantastic!"])
        elif PRAISE_PHRASES:
            praise = random.choice(PRAISE_PHRASES)
        else:
            praise = "Good!"
        self.speak_async(praise)

    def speak_encouragement(self):
        """朗读鼓励语（异步）- 使用较短的鼓励语"""
        # 选择较短的鼓励语，不打断游戏节奏
        short_encouragements = ["Try again!", "Keep going!", "You can do it!", "Almost!", "Don't give up!"]
        encouragement = random.choice(short_encouragements)
        self.speak_async(encouragement)
    
    def reset_level(self):
        """重置当前关卡"""
        if self.current_level < len(NEW_CONCEPT_LESSONS):
            self.current_sentence_index = 0
            self.next_sentence()
            self.correct_chars = 0
            self.total_chars = 0
            self.user_input = ""
            self.score = self.level_scores[self.current_level]
    
    def next_sentence(self):
        """加载下一个句子"""
        if self.current_level < len(NEW_CONCEPT_LESSONS):
            lesson = NEW_CONCEPT_LESSONS[self.current_level]
            if self.current_sentence_index < len(lesson["sentences"]):
                self.current_sentence = lesson["sentences"][self.current_sentence_index]
                self.user_input = ""
                self.start_time = time.time()
            else:
                # 本关完成
                self.state = "level_complete"
                self.level_scores[self.current_level] = self.score
    
    def check_input(self):
        """检查用户输入"""
        if not self.current_sentence:
            return True
            
        for i, char in enumerate(self.user_input):
            if i >= len(self.current_sentence) or char != self.current_sentence[i]:
                return False
        return True
    
    def calculate_accuracy(self):
        """计算准确率"""
        if self.total_chars == 0:
            return 100
        return max(0, int((self.correct_chars / self.total_chars) * 100))
    
    def calculate_speed(self):
        """计算打字速度（字符/分钟）"""
        elapsed_time = time.time() - self.start_time
        if elapsed_time <= 0:
            return 0
        return int((len(self.user_input) / elapsed_time) * 60)
    
    def handle_input(self, char):
        """处理用户输入"""
        if self.state != "playing":
            return
            
        if char == '\b':  # 退格键
            if len(self.user_input) > 0:
                # 退格时，如果最后一个字符是错误的，减少错误计数
                last_idx = len(self.user_input) -1
                if last_idx < len(self.current_sentence) and self.user_input[last_idx] != self.current_sentence[last_idx]:
                    self.errors = max(0, self.errors - 1)
                self.user_input = self.user_input[:-1]
                self.total_chars = max(0, self.total_chars - 1)
                if last_idx < len(self.current_sentence) and self.user_input[last_idx:last_idx+1] == self.current_sentence[last_idx:last_idx+1]:
                    self.correct_chars = min(self.correct_chars, len(self.user_input))
                self.play_type_sound()
        elif char == '\r':  # 回车键
            # 检查句子是否完成且正确
            if self.user_input == self.current_sentence:
                accuracy = self.calculate_accuracy()
                speed = self.calculate_speed()

                # 检查准确率和速度成就
                self.achievement_system.check_accuracy(accuracy)
                self.achievement_system.check_speed(speed)

                # 计算得分：基于准确率和速度
                base_score = len(self.current_sentence) * SCORE_PER_CORRECT_CHAR
                accuracy_bonus = base_score * (accuracy / 100)
                speed_bonus = min(speed / 10, 50)  # 速度奖励上限
                level_bonus = (self.current_level + 1) * LEVEL_NUMBER_MULTIPLIER
                # 连击奖励
                combo_multiplier = 1 + min(self.max_combo, 20) * 0.05  # 最高2倍

                self.score += int((base_score + accuracy_bonus + speed_bonus + level_bonus) * combo_multiplier)
                self.play_complete_sound()
                # 触发庆祝动画
                self.trigger_celebration()
                # 正确完成一句，表扬一下（根据连击选择夸奖语）
                self.speak_praise()

                # 添加句子完成经验 (Add EXP for sentence completion)
                if self.level_system:
                    is_perfect = (accuracy == 100)
                    self.level_system.add_exp_for_sentence(perfect=is_perfect)
                    # 连击奖励经验
                    if self.combo > 0:
                        self.level_system.add_exp_for_combo(self.combo)

                # 进入下一句
                self.current_sentence_index += 1
                if self.current_sentence_index >= len(NEW_CONCEPT_LESSONS[self.current_level]["sentences"]):
                    # 本关完成，添加关卡完成奖励
                    self.score += LEVEL_COMPLETION_BONUS
                    self.level_scores[self.current_level] = self.score

                    # 检查关卡完成成就
                    self.achievement_system.check_level_complete(
                        self.current_level, self.errors, len(NEW_CONCEPT_LESSONS)
                    )

                    # 添加经验值 (Add experience points)
                    if self.level_system:
                        # 关卡完成经验
                        level_up = self.level_system.add_exp_for_level()
                        if level_up:
                            # 升级了！可以添加通知
                            pass
                        # 保存进度
                        self.level_system.save_progress()

                    # 提交排行榜 (Submit to leaderboard)
                    if self.leaderboard:
                        final_accuracy = self.calculate_accuracy()
                        final_speed = self.calculate_speed()
                        self.leaderboard.add_score(
                            player_name="Player",
                            score=self.score,
                            accuracy=final_accuracy,
                            speed=final_speed,
                            combo=self.max_combo,
                            level=self.current_level + 1
                        )

                    self.state = "level_complete"
                else:
                    self.next_sentence()
                    # 翻页下一句，开始朗读
                    self.speak_sentence()
            else:
                # 句子未完成或不正确，增加错误计数
                self.errors += 1
                # 重置连击
                self.combo = 0
                self.play_error_sound()
                # 屏幕抖动
                self.trigger_screen_shake(5, 2)
                # 朗读鼓励语
                self.speak_encouragement()
        else:
            # 添加字符到输入
            self.user_input += char
            self.total_chars += 1
            self.play_type_sound()
            
            # 检查当前字符是否正确
            idx = len(self.user_input) - 1
            if idx < len(self.current_sentence) and self.user_input[idx] == self.current_sentence[idx]:
                self.correct_chars += 1
                # 添加经验值 (Add EXP for correct char)
                if self.level_system:
                    self.level_system.add_exp_for_char()
                # 连击系统
                self.combo += 1
                self.combo_timer = time.time()
                self.max_combo = max(self.max_combo, self.combo)
                # 检查连击成就
                self.achievement_system.check_combo(self.combo)
                # 连击奖励分数
                combo_bonus = min(self.combo, 20)  # 最高20倍
                self.score += combo_bonus
                # 创建绿色粒子效果，连击越高效果越强
                if self.state == "playing":
                    input_y = self.screen_height // 2
                    input_font_height = self.font_large.get_height()
                    input_box_padding = int(input_font_height * 0.3)
                    input_box_height = input_font_height + input_box_padding * 2
                    input_box_horizontal_padding = int(input_font_height * 0.5)
                    input_box_width = max(400, len(self.user_input) * 20 + input_box_horizontal_padding * 2)
                    input_box_x = (self.screen_width - input_box_width) // 2
                    input_box_y = input_y - input_box_padding
                    input_text_x = input_box_x + (input_box_width - len(self.user_input) * 20) // 2
                    input_text_y = input_box_y + (input_box_height - input_font_height) // 2
                    cursor_x = input_text_x + len(self.user_input) * 20
                    cursor_y = input_text_y + (input_font_height - int(input_font_height * 0.7)) // 2
                    # 连击越高粒子越多
                    particle_count = 5 + min(self.combo // 2, 10)
                    self.create_particles(cursor_x, cursor_y, COLORS['CORRECT'], particle_count)
                    self.play_correct_sound()
            else:
                # 输入错误，增加错误计数
                self.errors += 1
                # 重置连击
                self.combo = 0
                # 创建红色粒子效果
                if self.state == "playing":
                    input_y = self.screen_height // 2
                    input_font_height = self.font_large.get_height()
                    input_box_padding = int(input_font_height * 0.3)
                    input_box_height = input_font_height + input_box_padding * 2
                    input_box_horizontal_padding = int(input_font_height * 0.5)
                    input_box_width = max(400, len(self.user_input) * 20 + input_box_horizontal_padding * 2)
                    input_box_x = (self.screen_width - input_box_width) // 2
                    input_box_y = input_y - input_box_padding
                    input_text_x = input_box_x + (input_box_width - len(self.user_input) * 20) // 2
                    input_text_y = input_box_y + (input_box_height - input_font_height) // 2
                    cursor_x = input_text_x + len(self.user_input) * 20
                    cursor_y = input_text_y + (input_font_height - int(input_font_height * 0.7)) // 2
                    self.create_particles(cursor_x, cursor_y, COLORS['INCORRECT'], 8)
                    self.play_error_sound()
                    # 屏幕抖动效果
                    self.trigger_screen_shake(8, 3)
    
    def init_stars(self):
        """初始化背景星星"""
        self.stars = []
        for _ in range(100):
            star = {
                'x': random.randint(0, self.screen_width),
                'y': random.randint(0, self.screen_height),
                'size': random.randint(1, 3),
                'brightness': random.randint(100, 255),
                'speed': random.uniform(0.1, 0.5)
            }
            self.stars.append(star)
    
    def update_and_draw_stars(self):
        """更新并绘制背景星星"""
        for star in self.stars:
            # 更新亮度（闪烁效果）
            star['brightness'] += random.randint(-5, 5)
            star['brightness'] = max(100, min(255, star['brightness']))
            
            # 缓慢移动星星
            star['y'] -= star['speed']
            if star['y'] < 0:
                star['y'] = self.screen_height
                star['x'] = random.randint(0, self.screen_width)
            
            # 绘制星星
            color = (star['brightness'], star['brightness'], star['brightness'])
            pygame.draw.circle(self.screen, color, (int(star['x']), int(star['y'])), star['size'])
    
    def create_particles(self, x, y, color, count=10):
        """创建粒子效果"""
        for _ in range(count):
            particle = {
                'x': x,
                'y': y,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'life': random.randint(20, 40),
                'color': color,
                'size': random.randint(2, 5)
            }
            self.particles.append(particle)
    
    def update_and_draw_particles(self):
        """更新并绘制粒子效果"""
        for particle in self.particles[:]:
            # 更新粒子位置
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['size'] = max(1, particle['size'] - 0.1)

            # 应用重力（如果有）
            if 'gravity' in particle:
                particle['vy'] += particle['gravity']

            # 绘制粒子
            if particle['life'] > 0:
                max_life = particle.get('max_life', 40)
                alpha = int((particle['life'] / max_life) * 255)
                color = particle['color']
                pygame.draw.circle(self.screen, color,
                               (int(particle['x']), int(particle['y'])),
                               int(particle['size']))
            else:
                self.particles.remove(particle)

    def trigger_screen_shake(self, duration=10, intensity=5):
        """触发屏幕抖动"""
        self.screen_shake = duration
        self.screen_shake_intensity = intensity

    def get_screen_shake_offset(self):
        """获取屏幕抖动偏移"""
        if self.screen_shake > 0:
            self.screen_shake -= 1
            return (random.randint(-self.screen_shake_intensity, self.screen_shake_intensity),
                    random.randint(-self.screen_shake_intensity, self.screen_shake_intensity))
        return (0, 0)

    def create_confetti(self, x, y, count=20):
        """创建五彩纸屑效果 - 用于完成句子时庆祝"""
        colors = [
            (255, 100, 100), (100, 255, 100), (100, 100, 255),
            (255, 255, 100), (255, 100, 255), (100, 255, 255)
        ]
        for _ in range(count):
            particle = {
                'x': x + random.randint(-50, 50),
                'y': y,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-8, -2),
                'life': random.randint(60, 120),
                'color': random.choice(colors),
                'size': random.randint(4, 8),
                'gravity': 0.2
            }
            self.particles.append(particle)

    def trigger_celebration(self):
        """触发庆祝动画"""
        # 在屏幕多个位置创建五彩纸屑
        for _ in range(3):
            x = random.randint(100, self.screen_width - 100)
            y = random.randint(50, 150)
            self.create_confetti(x, y, count=15)

        # 如果连击高，效果更强
        if self.combo >= 5:
            center_x = self.screen_width // 2
            self.create_particles(center_x, self.screen_height // 2, (255, 215, 0), count=30)

    def draw_gradient_background(self):
        """绘制渐变背景"""
        # 创建渐变背景
        background = pygame.Surface((self.screen_width, self.screen_height))
        
        # 计算渐变步数
        gradient_steps = 100
        
        # 计算颜色渐变
        for y in range(self.screen_height):
            # 计算当前行的颜色（线性插值）
            ratio = y / self.screen_height
            r = int(COLORS['BACKGROUND_TOP'][0] * (1 - ratio) + COLORS['BACKGROUND_BOTTOM'][0] * ratio)
            g = int(COLORS['BACKGROUND_TOP'][1] * (1 - ratio) + COLORS['BACKGROUND_BOTTOM'][1] * ratio)
            b = int(COLORS['BACKGROUND_TOP'][2] * (1 - ratio) + COLORS['BACKGROUND_BOTTOM'][2] * ratio)
            
            # 绘制当前行
            pygame.draw.line(background, (r, g, b), (0, y), (self.screen_width, y))
        
        self.screen.blit(background, (0, 0))
        
        # 绘制背景星星
        self.update_and_draw_stars()
    
    def draw_panel(self, x, y, width, height, title=None):
        """绘制面板背景 (Draw panel background)"""
        # 面板背景
        panel_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, COLORS['INPUT_BG'], panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['UI'], panel_rect, 2, border_radius=10)

        # 面板标题
        if title:
            title_text = self.font_small.render(title, True, COLORS['HIGHLIGHT'])
            self.screen.blit(title_text, (x + 10, y + 5))

        return panel_rect

    def draw_menu(self):
        """绘制简洁主菜单 (Draw simplified main menu)"""
        self.draw_gradient_background()

        center_x = self.screen_width // 2

        # 1. 标题 Title with shadow
        title = self.font_large.render(GAME_TITLE, True, COLORS['TEXT'])
        title_rect = title.get_rect(center=(center_x, 60))
        title_shadow = self.font_large.render(GAME_TITLE, True, COLORS['TEXT_SHADOW'])
        self.screen.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
        self.screen.blit(title, title_rect)

        # 副标题
        subtitle = self.font_small.render("English Typing Game 英语打字学习游戏", True, COLORS['UI'])
        subtitle_rect = subtitle.get_rect(center=(center_x, 100))
        self.screen.blit(subtitle, subtitle_rect)

        # 2. 玩家等级信息（简洁一行）
        if self.level_system:
            level_info = self.level_system.get_level_info()
            progress = self.level_system.get_progress_to_next()

            # 等级文本
            level_text = f"Lv.{self.level_system.current_level} {level_info['title']}"
            if self.level_system.current_level < 10:
                next_exp = self.level_system.LEVEL_CONFIG[self.level_system.current_level + 1]['exp_required']
                level_text += f"  EXP: {self.level_system.current_exp}/{next_exp}"

            level_surface = self.font_small.render(level_text, True, level_info['color'])
            level_rect = level_surface.get_rect(center=(center_x, 140))
            self.screen.blit(level_surface, level_rect)

            # 经验条
            bar_width = 200
            bar_height = 8
            bar_x = center_x - bar_width // 2
            bar_y = 160

            pygame.draw.rect(self.screen, COLORS['PROGRESS_BG'],
                           (bar_x, bar_y, bar_width, bar_height), border_radius=4)
            fill_width = int(bar_width * progress / 100)
            if fill_width > 0:
                pygame.draw.rect(self.screen, COLORS['PROGRESS'],
                               (bar_x, bar_y, fill_width, bar_height), border_radius=4)

        # 3. 菜单选项（垂直列表，方向键选择）
        menu_items = [
            ("1", "Start Game", "开始游戏"),
            ("2", "Leaderboard", "排行榜"),
            ("3", "Achievements", "成就"),
        ]

        menu_y = 220
        menu_spacing = 50

        for i, (key, en, cn) in enumerate(menu_items):
            is_selected = (i == self.menu_index)

            # 选中指示器
            if is_selected:
                indicator = ">"
                color = COLORS['HIGHLIGHT']
            else:
                indicator = " "
                color = COLORS['TEXT']

            item_text = f"{indicator} [{key}] {en} {cn}"
            item_surface = self.font_medium.render(item_text, True, color)
            item_rect = item_surface.get_rect(center=(center_x, menu_y + i * menu_spacing))

            # 选中项背景
            if is_selected:
                bg_rect = item_rect.inflate(40, 10)
                pygame.draw.rect(self.screen, (40, 50, 70), bg_rect, border_radius=5)

            self.screen.blit(item_surface, item_rect)

        # 4. 底部快捷键
        bottom_y = self.screen_height - 50
        shortcuts = "[Up/Down] Select  [Enter] Confirm  [ESC] Exit  [F11] Fullscreen"
        shortcut_surface = self.font_small.render(shortcuts, True, COLORS['UI'])
        shortcut_rect = shortcut_surface.get_rect(center=(center_x, bottom_y))
        self.screen.blit(shortcut_surface, shortcut_rect)

    def draw_course_select(self):
        """绘制课程选择界面 (Draw course selection screen)"""
        self.draw_gradient_background()

        center_x = self.screen_width // 2

        # 标题
        title = self.font_large.render("Select Course 选择课程", True, COLORS['TEXT'])
        title_rect = title.get_rect(center=(center_x, 50))
        self.screen.blit(title, title_rect)

        # 课程列表
        y_offset = 120
        available_height = self.screen_height - y_offset - 80
        max_visible = min(len(NEW_CONCEPT_LESSONS), available_height // 45)

        # 计算可见范围（滚动支持）
        start_idx = max(0, self.current_level - max_visible // 2)
        end_idx = min(len(NEW_CONCEPT_LESSONS), start_idx + max_visible)
        if end_idx - start_idx < max_visible:
            start_idx = max(0, end_idx - max_visible)

        for i in range(start_idx, end_idx):
            lesson = NEW_CONCEPT_LESSONS[i]
            is_selected = (i == self.current_level)

            # 颜色
            if is_selected:
                color = COLORS['HIGHLIGHT']
                indicator = ">"
            else:
                color = COLORS['TEXT']
                indicator = " "

            # 课程信息
            lesson_title = lesson.get('title', f'Lesson {i+1}')
            if len(lesson_title) > 35:
                lesson_title = lesson_title[:32] + "..."

            text = f"{indicator} [{i+1}] {lesson_title}"
            text_surface = self.font_small.render(text, True, color)
            text_rect = text_surface.get_rect(midleft=(center_x - 250, y_offset))

            # 选中项背景
            if is_selected:
                bg_rect = pygame.Rect(center_x - 280, y_offset - 15, 560, 35)
                pygame.draw.rect(self.screen, (40, 50, 70), bg_rect, border_radius=5)

            self.screen.blit(text_surface, text_rect)

            # 最高分
            if i < len(self.level_scores) and self.level_scores[i] > 0:
                score_text = f"Best: {self.level_scores[i]}"
                score_surface = self.font_small.render(score_text, True, COLORS['CORRECT'])
                self.screen.blit(score_surface, (center_x + 150, y_offset - 10))

            y_offset += 45

        # 滚动提示
        if start_idx > 0:
            up_text = self.font_small.render("...", True, COLORS['UI'])
            self.screen.blit(up_text, (center_x - 10, 100))
        if end_idx < len(NEW_CONCEPT_LESSONS):
            down_text = self.font_small.render("...", True, COLORS['UI'])
            self.screen.blit(down_text, (center_x - 10, y_offset))

        # 底部快捷键
        bottom_y = self.screen_height - 40
        shortcuts = "[Up/Down] Select  [1-9] Quick Select  [Enter] Start  [ESC] Back"
        shortcut_surface = self.font_small.render(shortcuts, True, COLORS['UI'])
        shortcut_rect = shortcut_surface.get_rect(center=(center_x, bottom_y))
        self.screen.blit(shortcut_surface, shortcut_rect)

    def draw_leaderboard_screen(self):
        """绘制排行榜界面 (Draw leaderboard screen)"""
        self.draw_gradient_background()

        # 标题
        title = self.font_large.render("Leaderboard 排行榜", True, COLORS['TEXT'])
        title_rect = title.get_rect(center=(self.screen_width//2, 50))
        self.screen.blit(title, title_rect)

        if not self.leaderboard:
            no_lb = self.font_medium.render("Leaderboard not available", True, COLORS['WARNING'])
            no_lb_rect = no_lb.get_rect(center=(self.screen_width//2, self.screen_height//2))
            self.screen.blit(no_lb, no_lb_rect)
        else:
            # 三个排行榜标签
            tabs = [
                ("Daily 今日", "daily"),
                ("Weekly 本周", "weekly"),
                ("All Time 总榜", "all_time")
            ]

            tab_width = self.screen_width // 3
            panel_height = self.screen_height - 180

            for i, (tab_name, category) in enumerate(tabs):
                x = i * tab_width + 20
                y = 100
                width = tab_width - 40

                # 绘制面板
                self.draw_panel(x, y, width, panel_height, tab_name)

                # 获取排行数据
                top_scores = self.leaderboard.get_top(category, 10)

                if not top_scores:
                    no_data = self.font_small.render("No records yet", True, COLORS['UI'])
                    self.screen.blit(no_data, (x + 20, y + 50))
                else:
                    entry_y = y + 40
                    for rank, entry in enumerate(top_scores, 1):
                        # 排名颜色
                        if rank == 1:
                            rank_color = (255, 215, 0)  # Gold
                        elif rank == 2:
                            rank_color = (192, 192, 192)  # Silver
                        elif rank == 3:
                            rank_color = (205, 127, 50)  # Bronze
                        else:
                            rank_color = COLORS['TEXT']

                        rank_text = f"#{rank} {entry['name'][:8]}"
                        score_text = f"{entry['score']}"

                        rank_surface = self.font_small.render(rank_text, True, rank_color)
                        score_surface = self.font_small.render(score_text, True, COLORS['CORRECT'])

                        self.screen.blit(rank_surface, (x + 15, entry_y))
                        self.screen.blit(score_surface, (x + width - 70, entry_y))

                        entry_y += 35

        # 返回提示
        back_text = self.font_small.render("Press [ESC] or [L] to go back 按 ESC 或 L 返回", True, COLORS['UI'])
        back_rect = back_text.get_rect(center=(self.screen_width//2, self.screen_height - 40))
        self.screen.blit(back_text, back_rect)

    def draw_achievements_screen(self):
        """绘制成就界面 (Draw achievements screen)"""
        self.draw_gradient_background()

        # 标题
        unlocked = self.achievement_system.get_unlocked_count()
        total = self.achievement_system.get_total_count()
        title = self.font_large.render(f"Achievements 成就 ({unlocked}/{total})", True, COLORS['TEXT'])
        title_rect = title.get_rect(center=(self.screen_width//2, 50))
        self.screen.blit(title, title_rect)

        # 成就列表
        all_achievements = self.achievement_system.get_all_achievements()

        # 计算布局 - 每行3个
        cols = 3
        margin = 20
        ach_width = (self.screen_width - margin * (cols + 1)) // cols
        ach_height = 80

        for i, ach in enumerate(all_achievements):
            col = i % cols
            row = i // cols

            x = margin + col * (ach_width + margin)
            y = 100 + row * (ach_height + margin)

            # 背景颜色根据解锁状态
            if ach['unlocked']:
                bg_color = (50, 70, 50)  # 绿色调
                text_color = COLORS['CORRECT']
            else:
                bg_color = COLORS['INPUT_BG']
                text_color = COLORS['UI']

            # 绘制成就卡片
            card_rect = pygame.Rect(x, y, ach_width, ach_height)
            pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS['UI'], card_rect, 2, border_radius=8)

            # 图标和名称
            icon_name = f"{ach['icon']} {ach['name']}"
            name_surface = self.font_small.render(icon_name, True, text_color)
            self.screen.blit(name_surface, (x + 10, y + 10))

            # 描述
            desc_surface = self.font_small.render(ach['description'], True, COLORS['TEXT'])
            self.screen.blit(desc_surface, (x + 10, y + 40))

        # 返回提示
        back_text = self.font_small.render("Press [ESC] or [A] to go back 按 ESC 或 A 返回", True, COLORS['UI'])
        back_rect = back_text.get_rect(center=(self.screen_width//2, self.screen_height - 40))
        self.screen.blit(back_text, back_rect)
    
    def draw_game(self):
        """Draw game interface"""
        self.draw_gradient_background()
        
        # Draw level title
        lesson_title = NEW_CONCEPT_LESSONS[self.current_level]["title"]
        title_text = self.font_medium.render(f"Level {NEW_CONCEPT_LESSONS[self.current_level]['level']}: {lesson_title}", True, COLORS['TEXT'])
        self.screen.blit(title_text, (20, 20))
        
        # Draw score
        score_text = self.font_medium.render(f"Score: {self.score}", True, COLORS['TEXT'])
        self.screen.blit(score_text, (self.screen_width - 150, 20))
        
        # Draw progress
        progress_text = self.font_small.render(f"Sentence {self.current_sentence_index + 1}/{len(NEW_CONCEPT_LESSONS[self.current_level]['sentences'])}", True, COLORS['TEXT'])
        self.screen.blit(progress_text, (self.screen_width - 250, 60))
        
        # Draw error count
        errors_text = self.font_small.render(f"Errors: {self.errors}/{MAX_ERRORS_PER_LEVEL}", True, 
                                           COLORS['CORRECT'] if self.errors < MAX_ERRORS_PER_LEVEL * 0.5 else COLORS['WARNING'])
        self.screen.blit(errors_text, (self.screen_width - 250, 85))
        
        # Draw target sentence with text highlighting (no boxes)
        # 根据屏幕高度动态调整位置
        sentence_y = self.screen_height // 4
        
        # Split sentence into words
        words = self.current_sentence.split()
        input_words = self.user_input.split()
        
        # Calculate total width needed for all words
        total_width = 0
        word_surfaces = []
        for word in words:
            word_surface = self.font_large.render(word, True, COLORS['TEXT'])
            word_surfaces.append(word_surface)
            total_width += word_surface.get_width() + 30  # 30px spacing between words
        
        # Start position to center the words
        x_offset = (self.screen_width - total_width) // 2

        # 清空单词位置记录
        self.word_rects = []

        # Draw all words with highlighting
        for i, (word, word_surface) in enumerate(zip(words, word_surfaces)):
            # Check if this word has been typed correctly
            is_correct = i < len(input_words) and input_words[i] == word
            is_typed = i < len(input_words)

            # Determine text color
            if is_typed:
                if is_correct:
                    text_color = COLORS['CORRECT']
                else:
                    text_color = COLORS['INCORRECT']
            else:
                text_color = COLORS['TEXT']

            # Render word with correct color
            word_surface_colored = self.font_large.render(word, True, text_color)

            # 记录单词位置（用于点击朗读）
            word_rect = pygame.Rect(x_offset, sentence_y, word_surface.get_width(), word_surface.get_height())
            self.word_rects.append((word, word_rect, i))

            # Draw text shadow for 3D effect
            shadow_offset = 3
            word_surface_shadow = self.font_large.render(word, True, COLORS['TEXT_SHADOW'])
            self.screen.blit(word_surface_shadow, (x_offset + shadow_offset, sentence_y + shadow_offset))

            # Draw main text
            self.screen.blit(word_surface_colored, (x_offset, sentence_y))

            x_offset += word_surface.get_width() + 30
        
        # Draw input area with 3D effect
        input_y = self.screen_height // 2
        
        # Calculate input box width and height based on font size
        input_surface = self.font_large.render(self.user_input, True, COLORS['INPUT'])
        input_font_height = self.font_large.get_height()
        input_box_padding = int(input_font_height * 0.3)  # 边距为字体高度的30%
        input_box_height = input_font_height + input_box_padding * 2  # 框高度
        input_box_horizontal_padding = int(input_font_height * 0.5)  # 水平边距
        input_box_width = max(400, input_surface.get_width() + input_box_horizontal_padding * 2)
        
        # Calculate input box position
        input_box_x = (self.screen_width - input_box_width) // 2
        input_box_y = input_y - input_box_padding
        
        # Draw multiple shadow layers for 3D effect
        shadow_layers = [
            (8, COLORS['SHADOW_DARK']),
            (5, COLORS['SHADOW_LIGHT']),
            (3, COLORS['SHADOW_LIGHT'])
        ]
        for offset, color in shadow_layers:
            shadow_rect = pygame.Rect(input_box_x + offset, input_box_y + offset, 
                                    input_box_width, input_box_height)
            pygame.draw.rect(self.screen, color, shadow_rect)
        
        # Draw main input box background
        input_box_rect = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
        pygame.draw.rect(self.screen, COLORS['INPUT_BG'], input_box_rect)
        
        # Draw inner glow effect
        glow_rect = pygame.Rect(input_box_x + 2, input_box_y + 2, 
                               input_box_width - 4, input_box_height - 4)
        pygame.draw.rect(self.screen, COLORS['GLOW'], glow_rect, 1)
        
        # Draw highlight border (top and left)
        pygame.draw.line(self.screen, COLORS['HIGHLIGHT_LIGHT'], 
                        (input_box_x, input_box_y), 
                        (input_box_x + input_box_width, input_box_y), 2)
        pygame.draw.line(self.screen, COLORS['HIGHLIGHT_LIGHT'], 
                        (input_box_x, input_box_y), 
                        (input_box_x, input_box_y + input_box_height), 2)
        
        # Draw shadow border (bottom and right)
        pygame.draw.line(self.screen, COLORS['SHADOW_DARK'], 
                        (input_box_x, input_box_y + input_box_height), 
                        (input_box_x + input_box_width, input_box_y + input_box_height), 2)
        pygame.draw.line(self.screen, COLORS['SHADOW_DARK'], 
                        (input_box_x + input_box_width, input_box_y), 
                        (input_box_x + input_box_width, input_box_y + input_box_height), 2)
        
        # Draw outer border
        pygame.draw.rect(self.screen, COLORS['INPUT'], input_box_rect, 2)
        
        # Draw user input text vertically and horizontally centered in the box
        input_text_x = input_box_x + (input_box_width - input_surface.get_width()) // 2
        input_text_y = input_box_y + (input_box_height - input_font_height) // 2
        self.screen.blit(input_surface, (input_text_x, input_text_y))
        
        # Draw cursor with glow effect (positioned at the end of input text)
        cursor_x = input_text_x + input_surface.get_width()
        cursor_height = int(input_font_height * 0.7)  # 光标高度为字体高度的70%
        cursor_y = input_text_y + (input_font_height - cursor_height) // 2
        
        # 光标闪烁效果
        cursor_visible = (self.frame_count // 30) % 2 == 0
        if cursor_visible:
            # Draw cursor glow
            pygame.draw.line(self.screen, COLORS['GLOW'], (cursor_x - 1, cursor_y - 1), 
                           (cursor_x - 1, cursor_y + cursor_height + 1), 4)
            # Draw cursor
            pygame.draw.line(self.screen, COLORS['TEXT'], (cursor_x, cursor_y), 
                           (cursor_x, cursor_y + cursor_height), 2)
        
        # Draw game info
        elapsed_time = time.time() - self.start_time
        remaining_time = max(0, self.time_limit - elapsed_time)
        
        # 根据屏幕高度动态调整底部信息位置
        info_y = self.screen_height - 180
        
        time_text = self.font_small.render(f"Time left: {int(remaining_time)}s", True, 
                                          COLORS['CORRECT'] if remaining_time > 10 else COLORS['INCORRECT'])
        self.screen.blit(time_text, (50, info_y))
        
        accuracy = self.calculate_accuracy()
        accuracy_text = self.font_small.render(f"Accuracy: {accuracy}%", True, 
                                              COLORS['CORRECT'] if accuracy >= MIN_ACCURACY_FOR_PASS else COLORS['INCORRECT'])
        self.screen.blit(accuracy_text, (200, info_y))
        
        speed = self.calculate_speed()
        speed_text = self.font_small.render(f"Speed: {speed} chars/min", True, COLORS['TEXT'])
        self.screen.blit(speed_text, (380, info_y))
        
        # Draw progress bar with enhanced visual effects
        progress_bar_y = self.screen_height - 120
        progress_bar_height = 20
        progress_bar_x = 50
        progress_bar_width = self.screen_width - 100
        
        # Draw progress bar shadow
        pygame.draw.rect(self.screen, COLORS['SHADOW_DARK'], 
                       (progress_bar_x + 3, progress_bar_y + 3, progress_bar_width, progress_bar_height))
        
        # Draw progress bar background
        pygame.draw.rect(self.screen, COLORS['PROGRESS_BG'], 
                       (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height))
        
        # Draw progress bar with gradient and glow effect
        progress = min(1.0, (self.current_sentence_index) / len(NEW_CONCEPT_LESSONS[self.current_level]['sentences']))
        progress_width = int(progress_bar_width * progress)
        
        if progress_width > 0:
            # Draw progress bar shadow
            pygame.draw.rect(self.screen, COLORS['SHADOW_DARK'], 
                           (progress_bar_x + 2, progress_bar_y + 2, progress_width, progress_bar_height))
            
            # Draw progress bar with gradient (simplified as solid color for performance)
            pygame.draw.rect(self.screen, COLORS['PROGRESS'], 
                           (progress_bar_x, progress_bar_y, progress_width, progress_bar_height))
            
            # Draw highlight on top of progress bar
            pygame.draw.line(self.screen, COLORS['HIGHLIGHT_LIGHT'], 
                            (progress_bar_x, progress_bar_y), 
                            (progress_bar_x + progress_width, progress_bar_y), 2)
            
            # Draw glow effect on progress bar
            if progress_width > 10:
                glow_rect = pygame.Rect(progress_bar_x + 2, progress_bar_y + 2, 
                                      progress_width - 4, progress_bar_height - 4)
                pygame.draw.rect(self.screen, COLORS['GLOW'], glow_rect, 1)
        
        # Draw progress bar border
        pygame.draw.rect(self.screen, COLORS['UI'], 
                       (progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height), 2)
        
        # 添加快捷键提示
        hint_text = self.font_small.render("Press ESC to return to menu", True, COLORS['WARNING'])
        hint_rect = hint_text.get_rect(center=(self.screen_width//2, self.screen_height - 60))
        self.screen.blit(hint_text, hint_rect)

        # 绘制连击显示
        self.draw_combo()

        # 绘制成就通知
        self.draw_achievement_notification()

        # 更新并绘制粒子效果
        self.update_and_draw_particles()

        # 更新帧计数器
        self.frame_count += 1

    def draw_combo(self):
        """绘制连击效果"""
        if self.combo < 2:
            return

        # 计算连击显示位置
        combo_x = self.screen_width - 180
        combo_y = 120

        # 连击数越高，效果越明显
        if self.combo >= 10:
            color = (255, 215, 0)  # 金色
        elif self.combo >= 5:
            color = (255, 165, 0)  # 橙色
        else:
            color = COLORS['CORRECT']  # 绿色

        # 缩放效果
        scale = 1.0 + min(self.combo * 0.03, 0.3)

        # 绘制连击阴影
        combo_shadow = self.font_medium.render(f"Combo x{self.combo}", True, COLORS['TEXT_SHADOW'])
        self.screen.blit(combo_shadow, (combo_x + 2, combo_y + 2))

        # 绘制连击文字
        combo_text = self.font_medium.render(f"Combo x{self.combo}", True, color)
        self.screen.blit(combo_text, (combo_x, combo_y))

        # 高连击时添加闪光粒子效果
        if self.combo >= 5 and self.frame_count % 15 == 0:
            sparkle_colors = [(255, 255, 100), (255, 215, 0), (255, 255, 255)]
            for _ in range(3):
                particle = {
                    'x': combo_x + random.randint(0, 100),
                    'y': combo_y + random.randint(-5, 20),
                    'vx': random.uniform(-1, 1),
                    'vy': random.uniform(-2, 0),
                    'life': random.randint(15, 30),
                    'color': random.choice(sparkle_colors),
                    'size': random.randint(2, 4)
                }
                self.particles.append(particle)

    def draw_achievement_notification(self):
        """绘制成就通知"""
        # 检查新通知
        if self.current_achievement_notification is None:
            notification = self.achievement_system.get_pending_notification()
            if notification:
                self.current_achievement_notification = notification
                self.notification_timer = 180  # 3秒显示时间（60fps * 3）

        # 绘制当前通知
        if self.current_achievement_notification and self.notification_timer > 0:
            achievement = self.current_achievement_notification
            self.notification_timer -= 1

            # 计算动画位置（滑入/滑出效果）
            if self.notification_timer > 150:
                # 滑入阶段
                progress = (180 - self.notification_timer) / 30
                y_offset = int(-80 * (1 - progress))
            elif self.notification_timer < 30:
                # 滑出阶段
                progress = self.notification_timer / 30
                y_offset = int(-80 * (1 - progress))
            else:
                y_offset = 0

            # 通知框位置和大小
            notification_width = 320
            notification_height = 80
            notification_x = (self.screen_width - notification_width) // 2
            notification_y = 30 + y_offset

            # 绘制通知框背景
            notification_rect = pygame.Rect(notification_x, notification_y,
                                            notification_width, notification_height)
            # 背景阴影
            shadow_rect = pygame.Rect(notification_x + 3, notification_y + 3,
                                      notification_width, notification_height)
            pygame.draw.rect(self.screen, (20, 20, 40), shadow_rect, border_radius=12)
            # 主背景
            pygame.draw.rect(self.screen, (50, 50, 80), notification_rect, border_radius=12)
            # 金色边框
            pygame.draw.rect(self.screen, (255, 215, 0), notification_rect, 3, border_radius=12)

            # 绘制"Achievement Unlocked!"标题
            title_text = self.font_small.render("Achievement Unlocked!", True, (255, 215, 0))
            self.screen.blit(title_text, (notification_x + 15, notification_y + 8))

            # 绘制成就名称和描述
            name_text = self.font_medium.render(f"{achievement['icon']} {achievement['name']}", True, (255, 255, 255))
            self.screen.blit(name_text, (notification_x + 15, notification_y + 32))

            desc_text = self.font_small.render(achievement['description'], True, (180, 180, 200))
            self.screen.blit(desc_text, (notification_x + 15, notification_y + 58))

            # 通知结束时清空
            if self.notification_timer <= 0:
                self.current_achievement_notification = None

    def draw_level_complete(self):
        """Draw level complete interface"""
        self.draw_gradient_background()
        
        title = self.font_large.render("Level Complete!", True, COLORS['CORRECT'])
        title_rect = title.get_rect(center=(self.screen_width//2, self.screen_height//5))
        self.screen.blit(title, title_rect)
        
        score_text = self.font_medium.render(f"Level Score: {self.score - sum(self.level_scores[:self.current_level])}", True, COLORS['TEXT'])
        score_rect = score_text.get_rect(center=(self.screen_width//2, self.screen_height//3))
        self.screen.blit(score_text, score_rect)
        
        total_score_text = self.font_medium.render(f"Total Score: {self.score}", True, COLORS['TEXT'])
        total_score_rect = total_score_text.get_rect(center=(self.screen_width//2, self.screen_height//3 + 50))
        self.screen.blit(total_score_text, total_score_rect)
        
        if self.current_level < len(NEW_CONCEPT_LESSONS) - 1:
            next_text = self.font_medium.render("Press N for next level, M for menu", True, COLORS['TEXT'])
            next_rect = next_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
            self.screen.blit(next_text, next_rect)
        else:
            complete_text = self.font_medium.render("Congratulations! All levels completed!", True, COLORS['CORRECT'])
            complete_rect = complete_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
            self.screen.blit(complete_text, complete_rect)
            
            menu_text = self.font_medium.render("Press M for menu", True, COLORS['TEXT'])
            menu_rect = menu_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 60))
            self.screen.blit(menu_text, menu_rect)
        
        # 添加退出提示
        exit_text = self.font_small.render("Press ESC to exit game", True, COLORS['WARNING'])
        exit_rect = exit_text.get_rect(center=(self.screen_width//2, self.screen_height - 100))
        self.screen.blit(exit_text, exit_rect)
    
    def draw_game_over(self):
        """Draw game over interface"""
        self.draw_gradient_background()
        
        title = self.font_large.render("Game Over", True, COLORS['INCORRECT'])
        title_rect = title.get_rect(center=(self.screen_width//2, self.screen_height//5))
        self.screen.blit(title, title_rect)
        
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, COLORS['TEXT'])
        score_rect = score_text.get_rect(center=(self.screen_width//2, self.screen_height//3))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.font_medium.render("Press R to restart, M for menu", True, COLORS['TEXT'])
        restart_rect = restart_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
        self.screen.blit(restart_text, restart_rect)
        
        # 添加退出提示
        exit_text = self.font_small.render("Press ESC to exit game", True, COLORS['WARNING'])
        exit_rect = exit_text.get_rect(center=(self.screen_width//2, self.screen_height - 100))
        self.screen.blit(exit_text, exit_rect)
    
    def run(self):
        """运行游戏主循环"""
        running = True
        # 启动背景音乐
        self.start_background_music()
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == VIDEORESIZE:
                    # 处理窗口大小变化 (Handle window resize)
                    if not self.fullscreen:
                        self.handle_resize(event.w, event.h)
                elif event.type == KEYDOWN:
                    # F11 全局切换全屏 (F11 toggle fullscreen globally)
                    if event.key == K_F11:
                        self.toggle_fullscreen()
                        continue
                    if self.state == "menu":
                        # 主菜单输入 (Main menu input)
                        if event.key == K_ESCAPE:
                            running = False
                        elif event.key == K_UP:
                            self.menu_index = (self.menu_index - 1) % 3
                        elif event.key == K_DOWN:
                            self.menu_index = (self.menu_index + 1) % 3
                        elif event.key == K_RETURN:
                            # Enter确认选择
                            if self.menu_index == 0:  # Start Game
                                self.state = "course_select"
                            elif self.menu_index == 1:  # Leaderboard
                                self.state = "leaderboard"
                            elif self.menu_index == 2:  # Achievements
                                self.state = "achievements"
                        elif event.key == K_1:
                            self.menu_index = 0
                            self.state = "course_select"
                        elif event.key == K_2:
                            self.menu_index = 1
                            self.state = "leaderboard"
                        elif event.key == K_3:
                            self.menu_index = 2
                            self.state = "achievements"

                    elif self.state == "course_select":
                        # 课程选择界面 (Course selection)
                        if event.key == K_ESCAPE:
                            self.state = "menu"
                        elif event.key == K_UP:
                            self.current_level = (self.current_level - 1) % len(NEW_CONCEPT_LESSONS)
                        elif event.key == K_DOWN:
                            self.current_level = (self.current_level + 1) % len(NEW_CONCEPT_LESSONS)
                        elif event.key == K_RETURN:
                            self.reset_level()
                            self.state = "playing"
                            self.speak_sentence()
                        elif event.key in [K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]:
                            level_idx = event.key - K_1
                            if level_idx < len(NEW_CONCEPT_LESSONS):
                                self.current_level = level_idx
                                self.reset_level()
                                self.state = "playing"
                                self.speak_sentence()

                    elif self.state == "leaderboard":
                        # 排行榜界面 (Leaderboard)
                        if event.key in [K_ESCAPE, K_BACKSPACE]:
                            self.state = "menu"

                    elif self.state == "achievements":
                        # 成就界面 (Achievements)
                        if event.key in [K_ESCAPE, K_BACKSPACE]:
                            self.state = "menu"

                    elif self.state == "playing":
                        # 处理游戏输入 (Handle game input)
                        if event.key == K_BACKSPACE:
                            self.handle_input('\b')
                        elif event.key == K_RETURN:
                            self.handle_input('\r')
                        elif event.key == K_ESCAPE:
                            self.state = "menu"
                        elif event.key == K_F1:
                            # F1键朗读当前句子 (F1 to read sentence)
                            self.speak_sentence()
                        elif event.key == K_F2:
                            # F2键朗读当前单词 (F2 to read current word)
                            self.speak_current_word()
                        else:
                            # 获取按键字符（包括空格）
                            # Get key character (including space)
                            key_char = event.unicode
                            if key_char:
                                self.handle_input(key_char)

                    elif self.state == "level_complete":
                        # 处理关卡完成输入 (Handle level complete input)
                        if event.key == K_ESCAPE:
                            self.state = "menu"
                        elif event.key == K_n:
                            if self.current_level < len(NEW_CONCEPT_LESSONS) - 1:
                                self.current_level += 1
                                self.reset_level()
                                self.state = "playing"
                                self.speak_sentence()
                            else:
                                self.state = "menu"
                        elif event.key == K_m:
                            self.state = "menu"

                    elif self.state == "game_over":
                        # 处理游戏结束输入 (Handle game over input)
                        if event.key == K_ESCAPE:
                            self.state = "menu"
                        elif event.key == K_r:
                            # 重新开始当前关卡
                            self.reset_level()
                            self.state = "playing"
                            self.speak_sentence()
                        elif event.key == K_m:
                            # 返回菜单
                            self.state = "menu"

                # 处理鼠标点击事件（点击单词朗读）
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1 and self.state == "playing":  # 左键点击
                        for word, rect, index in self.word_rects:
                            if rect.collidepoint(event.pos):
                                self.speak_word(word)
                                # 创建点击反馈粒子效果
                                self.create_particles(rect.centerx, rect.centery, (100, 200, 255), 5)
                                break

            # 检查时间限制
            if self.state == "playing":
                elapsed_time = time.time() - self.start_time
                if elapsed_time > self.time_limit:
                    # 时间到，挑战失败
                    self.state = "game_over"

            # 绘制界面 (Draw interface based on state)
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "course_select":
                self.draw_course_select()
            elif self.state == "leaderboard":
                self.draw_leaderboard_screen()
            elif self.state == "achievements":
                self.draw_achievements_screen()
            elif self.state == "playing":
                self.draw_game()
            elif self.state == "level_complete":
                self.draw_level_complete()
            elif self.state == "game_over":
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)

        # 清理资源
        self.stop_voice_thread()
        self.stop_background_music()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()