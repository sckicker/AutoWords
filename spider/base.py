"""
爬虫基类
提供基础的网络请求和数据处理功能
"""
import json
import os
import time
import random
from typing import List, Dict, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


class BaseCrawler:
    """爬虫基类"""

    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    def __init__(self, output_dir: str = 'data/lessons/custom'):
        self.output_dir = output_dir
        self.delay_range = (1, 3)  # 请求间隔（秒）
        os.makedirs(output_dir, exist_ok=True)

    def fetch(self, url: str, headers: Optional[Dict] = None) -> Optional[str]:
        """发送HTTP请求获取页面内容"""
        try:
            req_headers = {**self.DEFAULT_HEADERS, **(headers or {})}
            request = Request(url, headers=req_headers)

            with urlopen(request, timeout=30) as response:
                return response.read().decode('utf-8')

        except HTTPError as e:
            print(f"HTTP错误 {e.code}: {url}")
        except URLError as e:
            print(f"URL错误: {e.reason}")
        except Exception as e:
            print(f"请求失败: {e}")

        return None

    def fetch_json(self, url: str, headers: Optional[Dict] = None) -> Optional[Dict]:
        """获取JSON数据"""
        content = self.fetch(url, headers)
        if content:
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
        return None

    def delay(self):
        """随机延迟，避免请求过快"""
        time.sleep(random.uniform(*self.delay_range))

    def save_json(self, data: Dict, filename: str):
        """保存数据到JSON文件"""
        filepath = os.path.join(self.output_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"已保存: {filepath}")
        except Exception as e:
            print(f"保存失败: {e}")

    def load_json(self, filename: str) -> Optional[Dict]:
        """从JSON文件加载数据"""
        filepath = os.path.join(self.output_dir, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载失败: {e}")
        return None

    def crawl(self) -> List[Dict]:
        """执行爬取（子类实现）"""
        raise NotImplementedError("子类必须实现 crawl 方法")

    def process(self, data: List[Dict]) -> List[Dict]:
        """处理数据（子类可选实现）"""
        return data
