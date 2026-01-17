"""
例句爬虫
从公开资源抓取英语例句
"""
import re
from typing import List, Dict
from .base import BaseCrawler


class SentenceCrawler(BaseCrawler):
    """例句爬虫 - 从Tatoeba等开源例句库获取数据"""

    # Tatoeba API (CC BY 2.0 许可)
    TATOEBA_API = "https://tatoeba.org/en/api_v0/search"

    # 适合初学者的常用单词列表
    BEGINNER_WORDS = [
        'hello', 'goodbye', 'please', 'thank', 'sorry',
        'yes', 'no', 'what', 'where', 'when', 'who', 'why', 'how',
        'I', 'you', 'he', 'she', 'we', 'they', 'it',
        'is', 'are', 'am', 'was', 'were', 'have', 'has',
        'can', 'could', 'will', 'would', 'should',
        'like', 'love', 'want', 'need', 'help',
        'book', 'pen', 'school', 'teacher', 'student',
        'eat', 'drink', 'read', 'write', 'play', 'work',
        'good', 'bad', 'big', 'small', 'new', 'old',
        'home', 'family', 'friend', 'time', 'day', 'year'
    ]

    def __init__(self, output_dir: str = 'data/lessons/custom'):
        super().__init__(output_dir)
        self.max_sentences_per_word = 5
        self.max_sentence_length = 80  # 适合打字练习的长度

    def crawl_tatoeba(self, word: str, lang: str = 'eng') -> List[Dict]:
        """从Tatoeba获取包含指定单词的例句"""
        sentences = []

        # 构建搜索URL
        params = f"from={lang}&query={word}&orphans=no&unapproved=no&limit=20"
        url = f"{self.TATOEBA_API}?{params}"

        data = self.fetch_json(url)
        if not data or 'results' not in data:
            return sentences

        for result in data['results']:
            text = result.get('text', '')

            # 过滤条件
            if not self._is_valid_sentence(text):
                continue

            sentence_data = {
                'text': text,
                'source': 'tatoeba',
                'word': word
            }

            # 尝试获取中文翻译
            translations = result.get('translations', [])
            for trans_group in translations:
                if isinstance(trans_group, list):
                    for trans in trans_group:
                        if trans.get('lang') == 'cmn':
                            sentence_data['translation'] = trans.get('text', '')
                            break

            sentences.append(sentence_data)

            if len(sentences) >= self.max_sentences_per_word:
                break

        return sentences

    def _is_valid_sentence(self, text: str) -> bool:
        """验证句子是否适合打字练习"""
        if not text:
            return False

        # 长度检查
        if len(text) > self.max_sentence_length:
            return False
        if len(text) < 10:
            return False

        # 只包含基本ASCII字符和常见标点
        if not re.match(r"^[a-zA-Z0-9\s\.,!?'\"-]+$", text):
            return False

        # 必须以大写字母开头
        if not text[0].isupper():
            return False

        # 必须以标点结尾
        if text[-1] not in '.!?':
            return False

        return True

    def crawl(self) -> List[Dict]:
        """爬取所有初学者单词的例句"""
        all_sentences = []

        print(f"开始爬取例句，共 {len(self.BEGINNER_WORDS)} 个单词...")

        for i, word in enumerate(self.BEGINNER_WORDS):
            print(f"[{i+1}/{len(self.BEGINNER_WORDS)}] 爬取单词: {word}")

            sentences = self.crawl_tatoeba(word)
            all_sentences.extend(sentences)

            print(f"  获取 {len(sentences)} 个例句")

            # 避免请求过快
            self.delay()

        print(f"\n爬取完成，共获取 {len(all_sentences)} 个例句")
        return all_sentences

    def process(self, sentences: List[Dict]) -> Dict:
        """处理并组织爬取的例句"""
        # 按单词分组
        by_word = {}
        for s in sentences:
            word = s.get('word', 'unknown')
            if word not in by_word:
                by_word[word] = []
            by_word[word].append({
                'text': s['text'],
                'translation': s.get('translation', '')
            })

        # 创建课程结构
        lessons = []
        words_per_lesson = 5
        word_list = list(by_word.keys())

        for i in range(0, len(word_list), words_per_lesson):
            lesson_words = word_list[i:i+words_per_lesson]
            lesson_sentences = []

            for word in lesson_words:
                lesson_sentences.extend(by_word[word][:3])  # 每个单词最多3句

            lessons.append({
                'level': len(lessons) + 1,
                'title': f"Practice {len(lessons) + 1} - {', '.join(lesson_words[:3])}...",
                'difficulty': 1 + len(lessons) // 5,  # 难度递增
                'words': lesson_words,
                'sentences': lesson_sentences
            })

        return {
            'meta': {
                'source': 'Tatoeba',
                'license': 'CC BY 2.0',
                'version': '1.0',
                'description': '从Tatoeba例句库抓取的英语练习句子'
            },
            'lessons': lessons
        }

    def run(self, output_file: str = 'tatoeba_sentences.json'):
        """执行爬取并保存"""
        sentences = self.crawl()
        if sentences:
            data = self.process(sentences)
            self.save_json(data, output_file)
            return data
        return None


# 命令行执行
if __name__ == '__main__':
    crawler = SentenceCrawler()
    crawler.run()
