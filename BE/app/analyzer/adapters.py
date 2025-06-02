# adapters.py

from interfaces import Analyzable
from app.models import InstizPosts  # 예시 import 위치

class InstizPostAdapter(Analyzable):
    def __init__(self, post: InstizPosts):
        self._post = post

    @property
    def content(self) -> str:
        return self._post.content

    def get_original(self) -> object:
        return self._post