"""
词汇爬虫
从公开资源抓取英语词汇和定义
"""
import re
from typing import List, Dict, Optional
from .base import BaseCrawler


class VocabularyCrawler(BaseCrawler):
    """词汇爬虫 - 获取单词列表和定义"""

    # 预定义的词汇分类
    WORD_CATEGORIES = {
        'basic': {
            'name': 'Basic Words',
            'description': '基础词汇',
            'words': [
                'a', 'an', 'the', 'and', 'or', 'but', 'if', 'then',
                'be', 'have', 'do', 'say', 'get', 'make', 'go', 'know',
                'take', 'see', 'come', 'think', 'look', 'want', 'give', 'use'
            ]
        },
        'greetings': {
            'name': 'Greetings',
            'description': '问候语',
            'words': [
                'hello', 'hi', 'hey', 'goodbye', 'bye', 'good morning',
                'good afternoon', 'good evening', 'good night',
                'how are you', 'nice to meet you', 'see you later'
            ]
        },
        'numbers': {
            'name': 'Numbers',
            'description': '数字',
            'words': [
                'one', 'two', 'three', 'four', 'five', 'six', 'seven',
                'eight', 'nine', 'ten', 'eleven', 'twelve', 'twenty',
                'hundred', 'thousand', 'first', 'second', 'third'
            ]
        },
        'colors': {
            'name': 'Colors',
            'description': '颜色',
            'words': [
                'red', 'blue', 'green', 'yellow', 'orange', 'purple',
                'pink', 'black', 'white', 'brown', 'gray', 'gold', 'silver'
            ]
        },
        'family': {
            'name': 'Family',
            'description': '家庭成员',
            'words': [
                'mother', 'father', 'parent', 'sister', 'brother',
                'grandmother', 'grandfather', 'aunt', 'uncle', 'cousin',
                'son', 'daughter', 'husband', 'wife', 'family'
            ]
        },
        'school': {
            'name': 'School',
            'description': '学校',
            'words': [
                'school', 'class', 'classroom', 'teacher', 'student',
                'book', 'pen', 'pencil', 'paper', 'desk', 'chair',
                'homework', 'test', 'exam', 'grade', 'subject'
            ]
        },
        'food': {
            'name': 'Food',
            'description': '食物',
            'words': [
                'food', 'eat', 'drink', 'breakfast', 'lunch', 'dinner',
                'apple', 'banana', 'orange', 'bread', 'rice', 'meat',
                'fish', 'egg', 'milk', 'water', 'juice', 'tea', 'coffee'
            ]
        },
        'time': {
            'name': 'Time',
            'description': '时间',
            'words': [
                'time', 'day', 'week', 'month', 'year', 'today',
                'tomorrow', 'yesterday', 'morning', 'afternoon', 'evening',
                'night', 'hour', 'minute', 'second', 'now', 'later'
            ]
        },
        'weather': {
            'name': 'Weather',
            'description': '天气',
            'words': [
                'weather', 'sun', 'sunny', 'rain', 'rainy', 'cloud',
                'cloudy', 'wind', 'windy', 'snow', 'snowy', 'hot',
                'cold', 'warm', 'cool', 'temperature'
            ]
        },
        'verbs': {
            'name': 'Common Verbs',
            'description': '常用动词',
            'words': [
                'run', 'walk', 'jump', 'sit', 'stand', 'sleep', 'wake',
                'read', 'write', 'speak', 'listen', 'watch', 'play',
                'work', 'study', 'learn', 'teach', 'help', 'ask', 'answer'
            ]
        }
    }

    def __init__(self, output_dir: str = 'data/lessons/custom'):
        super().__init__(output_dir)

    def get_category_words(self, category: str) -> Optional[Dict]:
        """获取指定分类的词汇"""
        return self.WORD_CATEGORIES.get(category)

    def get_all_categories(self) -> List[str]:
        """获取所有词汇分类"""
        return list(self.WORD_CATEGORIES.keys())

    def crawl(self) -> List[Dict]:
        """生成词汇课程数据"""
        lessons = []

        for i, (cat_id, cat_data) in enumerate(self.WORD_CATEGORIES.items()):
            words = cat_data['words']

            # 为每个单词创建简单的练习句子
            sentences = []
            for word in words:
                sentences.append({
                    'text': self._generate_practice_sentence(word),
                    'translation': ''
                })

            lessons.append({
                'level': i + 1,
                'title': f"{cat_data['name']} - {cat_data['description']}",
                'difficulty': 1 + i // 3,
                'words': words,
                'sentences': sentences
            })

        return lessons

    def _generate_practice_sentence(self, word: str) -> str:
        """为单词生成练习句子"""
        # 简单的模板句子
        templates = [
            f"This is {word}.",
            f"I like {word}.",
            f"Please say {word}.",
            f"Can you spell {word}?",
            f"The word is {word}."
        ]

        # 根据单词长度选择模板
        idx = len(word) % len(templates)
        return templates[idx]

    def process(self, lessons: List[Dict]) -> Dict:
        """处理数据为标准格式"""
        return {
            'meta': {
                'source': 'Vocabulary Builder',
                'version': '1.0',
                'description': '分类词汇学习课程'
            },
            'lessons': lessons
        }

    def run(self, output_file: str = 'vocabulary_lessons.json'):
        """执行并保存"""
        lessons = self.crawl()
        if lessons:
            data = self.process(lessons)
            self.save_json(data, output_file)
            return data
        return None

    def generate_typing_drills(self, category: str = None) -> List[str]:
        """生成打字练习文本"""
        drills = []

        categories = [category] if category else self.get_all_categories()

        for cat in categories:
            cat_data = self.get_category_words(cat)
            if cat_data:
                # 单词列表练习
                words = cat_data['words']
                drills.append(' '.join(words))

                # 重复单词练习（每个单词打3遍）
                for word in words[:5]:  # 取前5个单词
                    drills.append(f"{word} {word} {word}")

        return drills


# 命令行执行
if __name__ == '__main__':
    crawler = VocabularyCrawler()
    crawler.run()
