"""
课程数据加载器
支持从JSON文件加载课程数据
"""
import json
import os
from typing import List, Dict, Optional


class LessonLoader:
    """课程数据加载器"""

    def __init__(self, base_path='data/lessons'):
        self.base_path = base_path
        self.cache = {}  # 缓存已加载的数据

    def load_all(self) -> List[Dict]:
        """加载所有课程数据"""
        all_lessons = []

        # 加载新概念英语
        new_concept_path = os.path.join(self.base_path, 'new_concept')
        if os.path.exists(new_concept_path):
            for filename in sorted(os.listdir(new_concept_path)):
                if filename.endswith('.json'):
                    filepath = os.path.join(new_concept_path, filename)
                    lessons = self._load_json_file(filepath)
                    if lessons:
                        all_lessons.extend(lessons)

        # 加载自定义课程
        custom_path = os.path.join(self.base_path, 'custom')
        if os.path.exists(custom_path):
            for filename in sorted(os.listdir(custom_path)):
                if filename.endswith('.json'):
                    filepath = os.path.join(custom_path, filename)
                    lessons = self._load_json_file(filepath)
                    if lessons:
                        all_lessons.extend(lessons)

        return all_lessons

    def load_book(self, book_name: str) -> List[Dict]:
        """加载指定书籍的课程"""
        filepath = os.path.join(self.base_path, 'new_concept', f'{book_name}.json')
        return self._load_json_file(filepath)

    def load_custom(self, filepath: str) -> List[Dict]:
        """加载自定义课程文件"""
        return self._load_json_file(filepath)

    def _load_json_file(self, filepath: str) -> List[Dict]:
        """加载JSON文件"""
        if filepath in self.cache:
            return self.cache[filepath]

        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 处理不同的JSON格式
                lessons = self._normalize_data(data)
                self.cache[filepath] = lessons
                return lessons

        except Exception as e:
            print(f"加载课程文件失败 {filepath}: {e}")

        return []

    def _normalize_data(self, data: Dict) -> List[Dict]:
        """标准化课程数据格式"""
        lessons = []

        # 新格式：包含meta和lessons字段
        if 'lessons' in data:
            for lesson in data['lessons']:
                normalized = self._normalize_lesson(lesson)
                if normalized:
                    lessons.append(normalized)

        # 旧格式：直接是课程列表
        elif isinstance(data, list):
            for item in data:
                normalized = self._normalize_lesson(item)
                if normalized:
                    lessons.append(normalized)

        return lessons

    def _normalize_lesson(self, lesson: Dict) -> Optional[Dict]:
        """标准化单个课程数据"""
        if not lesson:
            return None

        # 提取句子文本
        sentences = []
        if 'sentences' in lesson:
            for s in lesson['sentences']:
                if isinstance(s, str):
                    sentences.append(s)
                elif isinstance(s, dict):
                    text = s.get('text') or s.get('sentence')
                    if text:
                        sentences.append(text)

        if not sentences:
            return None

        return {
            'level': lesson.get('level', 1),
            'title': lesson.get('title', 'Untitled'),
            'difficulty': lesson.get('difficulty', 1),
            'words': lesson.get('words', []),
            'sentences': sentences,
            'translations': self._extract_translations(lesson)
        }

    def _extract_translations(self, lesson: Dict) -> List[str]:
        """提取翻译"""
        translations = []
        if 'sentences' in lesson:
            for s in lesson['sentences']:
                if isinstance(s, dict):
                    trans = s.get('translation', '')
                    translations.append(trans)
        return translations

    def get_sentences_only(self) -> List[str]:
        """获取所有句子（用于兼容旧代码）"""
        all_lessons = self.load_all()
        sentences = []
        for lesson in all_lessons:
            sentences.extend(lesson.get('sentences', []))
        return sentences

    def get_words_for_level(self, level: int) -> List[str]:
        """获取指定关卡的单词列表"""
        all_lessons = self.load_all()
        for lesson in all_lessons:
            if lesson.get('level') == level:
                return lesson.get('words', [])
        return []

    def clear_cache(self):
        """清除缓存"""
        self.cache = {}


# 兼容性函数：用于旧代码迁移
def get_all_sentences() -> List[str]:
    """获取所有句子（兼容旧代码）"""
    loader = LessonLoader()
    return loader.get_sentences_only()


def get_lessons() -> List[Dict]:
    """获取所有课程（兼容旧代码）"""
    loader = LessonLoader()
    return loader.load_all()
