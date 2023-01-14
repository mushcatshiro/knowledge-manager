"""
markdown syntax

- headers (1-6)
- paragraphs and line breaks (lowest priority)
- bolds
- blockquotes (single and multi, other MD elements)
- lists (UL and OL, other MD elements)
- code (``)
- links (%20)
- images
- character escaping
- code blocks
- mermaid blocks
- mathjax
"""
import os

class Templating:
    def __init__(self) -> None:
        self.preprocessors = []
        self.treeprocessors = ""
        self.postprocessors = []

    def process(self, fname):
        rv = None
        if os.path.isfile(fname):
            with open(fname, "r") as rf:
                lines = rf.read()
            for line in lines:
                pass
        else:
            rv = "file does not exists!"
        return rv


t = Templating()

def render_template(**kwargs):
    return t.process()