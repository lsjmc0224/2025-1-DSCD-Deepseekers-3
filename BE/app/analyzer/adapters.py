from app.analyzer.interfaces import Analyzable
from app.models import InstizPosts, InstizComments, TiktokComments, YoutubeComments

class InstizPostAdapter(Analyzable):
    def __init__(self, post: InstizPosts):
        self._post = post

    @property
    def content(self) -> str:
        return self._post.content

    def get_original(self) -> object:
        return self._post


class InstizCommentAdapter(Analyzable):
    def __init__(self, comment: InstizComments):
        self._comment = comment

    @property
    def content(self) -> str:
        return self._comment.content

    def get_original(self) -> object:
        return self._comment

class TiktokCommentAdapter(Analyzable):
    def __init__(self, comment: TiktokComments):
        self._comment = comment

    @property
    def content(self) -> str:
        return self._comment.content

    def get_original(self) -> object:
        return self._comment

class YoutubeCommentAdapter(Analyzable):
    def __init__(self, comment: YoutubeComments):
        self._comment = comment

    @property
    def content(self) -> str:
        return self._comment.content

    def get_original(self) -> object:
        return self._comment
