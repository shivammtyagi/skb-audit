from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json

@dataclass
class Article:
    id: str
    title: str
    url: str
    slug: str
    body_text: str
    body_html: str
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    author: str = ""
    published: Optional[str] = None
    modified: Optional[str] = None
    word_count: int = 0
    has_toc: bool = False
    images: int = 0
    internal_links: int = 0
    external_links: int = 0
    code_blocks: List[str] = field(default_factory=list)
    video_embeds: List[str] = field(default_factory=list)
    type: str = ""
    product: str = ""
    repo: str = ""

def save_articles(path, articles):
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(a) for a in articles], f, indent=2, ensure_ascii=False)

def load_articles(path):
    with open(path, encoding="utf-8") as f:
        return [Article(**{k: v for k, v in d.items() if k in Article.__dataclass_fields__})
                for d in json.load(f)]
