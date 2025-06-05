from app.analyzer.adapters import (
    InstizPostAdapter, InstizCommentAdapter,
    TiktokCommentAdapter, YoutubeCommentAdapter
)
from app.models import InstizPosts, InstizComments, TiktokComments, YoutubeComments
from app.analyzer.interfaces import Analyzable

class AdapterFactory:
    def wrap(self, item: object) -> Analyzable:
        if isinstance(item, InstizPosts):
            return InstizPostAdapter(item)
        elif isinstance(item, InstizComments):
            return InstizCommentAdapter(item)
        elif isinstance(item, TiktokComments):
            return TiktokCommentAdapter(item)
        elif isinstance(item, YoutubeComments):
            return YoutubeCommentAdapter(item)
        else:
            raise TypeError(f"지원되지 않는 타입입니다: {type(item)}")
