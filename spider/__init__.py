"""
爬虫模块
用于抓取英语学习资源
"""
from .base import BaseCrawler
from .sentences import SentenceCrawler
from .vocabulary import VocabularyCrawler

__all__ = ['BaseCrawler', 'SentenceCrawler', 'VocabularyCrawler']
