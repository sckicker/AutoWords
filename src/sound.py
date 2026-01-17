"""
音效生成器模块
使用 numpy 程序生成音效，解决音效文件缺失问题
"""
import numpy as np
import pygame


class SoundGenerator:
    """使用程序生成音效"""

    @staticmethod
    def generate_type_sound():
        """生成打字'啪'音效 - 短促的敲击声"""
        sample_rate = 44100
        duration = 0.05  # 50毫秒
        t = np.linspace(0, duration, int(sample_rate * duration), False)

        # 组合多个频率产生敲击感
        freq1, freq2 = 800, 1200
        wave = np.sin(2 * np.pi * freq1 * t) * 0.5 + np.sin(2 * np.pi * freq2 * t) * 0.3

        # 快速衰减包络
        envelope = np.exp(-t * 60)
        wave = wave * envelope

        # 添加一点噪声增加真实感
        noise = np.random.uniform(-0.1, 0.1, len(t))
        wave = wave * 0.8 + noise * 0.2

        # 转换为16位整数
        wave = np.int16(wave * 32767 * 0.5)
        stereo = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo)

    @staticmethod
    def generate_correct_sound():
        """生成正确音效 - 上升的悦耳音调"""
        sample_rate = 44100
        duration = 0.15
        t = np.linspace(0, duration, int(sample_rate * duration), False)

        # 上升音调
        freq = 440 + 200 * t / duration
        wave = np.sin(2 * np.pi * freq * t)

        # 平滑包络
        envelope = np.sin(np.pi * t / duration)
        wave = wave * envelope

        wave = np.int16(wave * 32767 * 0.4)
        stereo = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo)

    @staticmethod
    def generate_error_sound():
        """生成错误音效 - 下降的低沉音调"""
        sample_rate = 44100
        duration = 0.2
        t = np.linspace(0, duration, int(sample_rate * duration), False)

        # 下降音调
        freq = 300 - 100 * t / duration
        wave = np.sin(2 * np.pi * freq * t)

        envelope = np.exp(-t * 5)
        wave = wave * envelope

        wave = np.int16(wave * 32767 * 0.4)
        stereo = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo)

    @staticmethod
    def generate_complete_sound():
        """生成完成音效 - 和弦上升"""
        sample_rate = 44100
        duration = 0.5
        t = np.linspace(0, duration, int(sample_rate * duration), False)

        # C大调和弦 (C, E, G)
        wave = (np.sin(2 * np.pi * 523.25 * t) +  # C5
                np.sin(2 * np.pi * 659.25 * t) +  # E5
                np.sin(2 * np.pi * 783.99 * t))   # G5

        envelope = np.sin(np.pi * t / duration)
        wave = wave * envelope / 3

        wave = np.int16(wave * 32767 * 0.5)
        stereo = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo)
