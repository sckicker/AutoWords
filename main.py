import pygame
import sys
import random
import time
import json
import os
import pyttsx3
from pygame.locals import *
from config import *
from lessons import NEW_CONCEPT_LESSONS

# 初始化Pygame
pygame.init()

class Game:
    def __init__(self):
        # 默认全屏模式
        self.fullscreen = True
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # 获取全屏分辨率
            self.screen_width, self.screen_height = pygame.display.get_surface().get_size()
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen_width, self.screen_height = SCREEN_WIDTH, SCREEN_HEIGHT
            
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
        self.state = "menu"  # menu, playing, level_complete, game_over
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
    
    def load_audio(self):
        """加载音频文件"""
        try:
            # Load background music
            if os.path.exists(BACKGROUND_MUSIC):
                self.background_music = pygame.mixer.music.load(BACKGROUND_MUSIC)
                pygame.mixer.music.set_volume(MUSIC_VOLUME)
        except:
            print("无法加载背景音乐")
        
        try:
            # Load sound effects
            if os.path.exists(TYPE_SOUND):
                self.type_sound = pygame.mixer.Sound(TYPE_SOUND)
                self.type_sound.set_volume(SFX_VOLUME)
        except:
            print("无法加载打字音效")
        
        try:
            if os.path.exists(CORRECT_SOUND):
                self.correct_sound = pygame.mixer.Sound(CORRECT_SOUND)
                self.correct_sound.set_volume(SFX_VOLUME)
        except:
            print("无法加载正确音效")
        
        try:
            if os.path.exists(ERROR_SOUND):
                self.error_sound = pygame.mixer.Sound(ERROR_SOUND)
                self.error_sound.set_volume(SFX_VOLUME)
        except:
            print("无法加载错误音效")
        
        try:
            if os.path.exists(COMPLETE_SOUND):
                self.complete_sound = pygame.mixer.Sound(COMPLETE_SOUND)
                self.complete_sound.set_volume(SFX_VOLUME)
        except:
            print("无法加载完成音效")
    
    def play_type_sound(self):
        """播放打字音效"""
        if self.type_sound:
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
        """朗读文本"""
        if TTS_ENABLED and hasattr(self, 'tts_engine'):
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"朗读失败: {e}")
    
    def speak_sentence(self):
        """朗读当前句子"""
        if self.current_sentence:
            self.speak(self.current_sentence)
    
    def speak_praise(self):
        """朗读夸奖语"""
        if PRAISE_PHRASES:
            praise = random.choice(PRAISE_PHRASES)
            self.speak(praise)
    
    def speak_encouragement(self):
        """朗读鼓励语"""
        if ENCOURAGEMENT_PHRASES:
            encouragement = random.choice(ENCOURAGEMENT_PHRASES)
            self.speak(encouragement)
    
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
                
                # 计算得分：基于准确率和速度
                base_score = len(self.current_sentence) * SCORE_PER_CORRECT_CHAR
                accuracy_bonus = base_score * (accuracy / 100)
                speed_bonus = min(speed / 10, 50)  # 速度奖励上限
                level_bonus = (self.current_level + 1) * LEVEL_NUMBER_MULTIPLIER
                
                self.score += int(base_score + accuracy_bonus + speed_bonus + level_bonus)
                self.play_complete_sound()
                # 正确完成一句，表扬一下
                self.speak_praise()
                
                # 进入下一句
                self.current_sentence_index += 1
                if self.current_sentence_index >= len(NEW_CONCEPT_LESSONS[self.current_level]["sentences"]):
                    # 本关完成，添加关卡完成奖励
                    self.score += LEVEL_COMPLETION_BONUS
                    self.level_scores[self.current_level] = self.score
                    self.state = "level_complete"
                else:
                    self.next_sentence()
                    # 翻页下一句，开始朗读
                    self.speak_sentence()
            else:
                # 句子未完成或不正确，增加错误计数
                self.errors += 1
                self.play_error_sound()
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
                # 创建绿色粒子效果
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
                    self.create_particles(cursor_x, cursor_y, COLORS['CORRECT'], 5)
                    self.play_correct_sound()
            else:
                # 输入错误，增加错误计数
                self.errors += 1
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
            
            # 绘制粒子
            if particle['life'] > 0:
                alpha = int((particle['life'] / 40) * 255)
                color = particle['color']
                pygame.draw.circle(self.screen, color, 
                               (int(particle['x']), int(particle['y'])), 
                               int(particle['size']))
            else:
                self.particles.remove(particle)
    
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
    
    def draw_menu(self):
        """Draw menu interface"""
        self.draw_gradient_background()
        
        # Draw title with shadow effect
        title = self.font_large.render(GAME_TITLE, True, COLORS['TEXT'])
        title_rect = title.get_rect(center=(self.screen_width//2, self.screen_height//6))
        
        # Draw title shadow
        title_shadow = self.font_large.render(GAME_TITLE, True, COLORS['TEXT_SHADOW'])
        title_shadow_rect = title_shadow.get_rect(center=(self.screen_width//2 + 3, self.screen_height//6 + 3))
        self.screen.blit(title_shadow, title_shadow_rect)
        
        # Draw main title
        self.screen.blit(title, title_rect)
        
        # Draw level selection
        y_offset = self.screen_height//4
        # 根据屏幕高度动态调整间距
        spacing = min(50, (self.screen_height * 0.5) // len(NEW_CONCEPT_LESSONS))
        
        for i, lesson in enumerate(NEW_CONCEPT_LESSONS):
            color = COLORS['HIGHLIGHT'] if i == self.current_level else COLORS['TEXT']
            level_text = self.font_medium.render(f"Level {lesson['level']}: {lesson['title']}", True, color)
            level_rect = level_text.get_rect(center=(self.screen_width//2, y_offset))
            
            # Draw level text shadow
            level_text_shadow = self.font_medium.render(f"Level {lesson['level']}: {lesson['title']}", True, COLORS['TEXT_SHADOW'])
            level_text_shadow_rect = level_text_shadow.get_rect(center=(self.screen_width//2 + 2, y_offset + 2))
            self.screen.blit(level_text_shadow, level_text_shadow_rect)
            
            # Show score if unlocked
            if self.level_scores[i] > 0:
                score_text = self.font_small.render(f"Score: {self.level_scores[i]}", True, COLORS['CORRECT'])
                # Draw score shadow
                score_text_shadow = self.font_small.render(f"Score: {self.level_scores[i]}", True, COLORS['TEXT_SHADOW'])
                self.screen.blit(score_text_shadow, (self.screen_width//2 + 202, y_offset - 8))
                self.screen.blit(score_text, (self.screen_width//2 + 200, y_offset - 10))
            
            self.screen.blit(level_text, level_rect)
            y_offset += spacing
        
        # Draw instructions
        instruction_y = self.screen_height - 150
        start_text = self.font_small.render("Press number keys to select level, press Enter to start", True, COLORS['TEXT'])
        start_rect = start_text.get_rect(center=(self.screen_width//2, instruction_y))
        self.screen.blit(start_text, start_rect)
        
        # 添加退出提示
        exit_text = self.font_small.render("Press ESC to exit game", True, COLORS['WARNING'])
        exit_rect = exit_text.get_rect(center=(self.screen_width//2, instruction_y + 40))
        self.screen.blit(exit_text, exit_rect)
    
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
        
        # 更新并绘制粒子效果
        self.update_and_draw_particles()
        
        # 更新帧计数器
        self.frame_count += 1
    
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
                elif event.type == KEYDOWN:
                    if self.state == "menu":
                        # 处理菜单输入
                        if event.key == K_ESCAPE:
                            running = False
                        elif event.key in [K_1, K_2, K_3, K_4, K_5]:
                            self.current_level = event.key - K_1
                            self.reset_level()
                            self.state = "playing"
                            # 进入input界面，开始朗读当前句子
                            self.speak_sentence()
                    elif self.state == "playing":
                        # 处理游戏输入
                        if event.key == K_BACKSPACE:
                            self.handle_input('\b')
                        elif event.key == K_RETURN:
                            self.handle_input('\r')
                        elif event.key == K_ESCAPE:
                            self.state = "menu"
                        else:
                            # 获取按键字符
                            key_char = event.unicode
                            if key_char:
                                self.handle_input(key_char)
                    elif self.state == "level_complete":
                        # 处理关卡完成输入
                        if event.key == K_ESCAPE:
                            running = False
                        elif event.key == K_n:
                            if self.current_level < len(NEW_CONCEPT_LESSONS) - 1:
                                self.current_level += 1
                                self.reset_level()
                                self.state = "playing"
                            else:
                                self.state = "menu"
                        elif event.key == K_m:
                            self.state = "menu"
                    elif self.state == "game_over":
                        # 处理游戏结束输入
                        if event.key == K_ESCAPE:
                            running = False
                        elif event.key == K_r:
                            # 重新开始当前关卡
                            self.reset_level()
                            self.state = "playing"
                        elif event.key == K_m:
                            # 返回菜单
                            self.state = "menu"
            
            # 检查时间限制
            if self.state == "playing":
                elapsed_time = time.time() - self.start_time
                if elapsed_time > self.time_limit:
                    # 时间到，挑战失败
                    self.state = "game_over"
            
            # 绘制界面
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "playing":
                self.draw_game()
            elif self.state == "level_complete":
                self.draw_level_complete()
            elif self.state == "game_over":
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()