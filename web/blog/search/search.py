import os

from .index import IndexObj


class Search:
    """
    TODO
    implement cosine similarity search?
    """

    def __init__(self, absdir):
        self.indexobj: IndexObj = IndexObj(absdir).index()

    def update_index(self):
        self.indexobj.index()

    def find_similar(self):
        return self.indexobj.get_top_N_items()


class SearchServer:
    """
    motive
    to run reindex outside of flask instance
    """

    pass
