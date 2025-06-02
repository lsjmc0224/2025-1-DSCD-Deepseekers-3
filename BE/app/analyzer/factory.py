# factory.py

from app.models import InstizPosts
from adapters import InstizPostAdapter
from interfaces import Analyzable

class AdapterFactory:
    def wrap(self, item: object) -> Analyzable:
        if isinstance(item, InstizPosts):
            return InstizPostAdapter(item)
        raise TypeError(f"지원되지 않는 타입입니다: {type(item)}")