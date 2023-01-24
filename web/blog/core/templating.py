"""
markdown syntax

- headers (1-6)
- paragraphs and line breaks (lowest priority)
- bolds
- blockquotes (single and multi, other MD elements)
- lists (UL and OL, other MD elements)
- code (priority?)
  - inline (``)
  - block
- links (%20 / whitespace conversion)
  - referrence links
- images
- character escaping
- code blocks
  - mermaid blocks
- mathjax
  - inline (might want to consider not using ($)[.\s\S]+($))
  - block
"""
import os
import re

HEADER = re.compile(r"(#)+(\s){1}(.)+")
PARAGRAPH = None
BOLD = re.compile(r"(\*\*)(.)+(\*\*)")
BLOCKQUOTES = re.compile(r"(\>)(\s){1}(.)+")
UNORDEREDLIST = re.compile(r"")
ORDEREDLIST = re.compile(r"")
INLINECODE = re.compile(r"(`)[.\s\S]+(`)")
CODEBLOCK = re.compile(r"(```)[.\s\S]+(```)")
IMAGES = re.compile(r"(\!\[)(.)+(\]\(.+\))")
MERMAID = re.compile(r"")
MATHJAXBLOCK = re.compile(r"($$)[.\s\S]+($$)")
INLINEMATHJAX = re.compiel(r"($)[.\s\S]+($)")

class ParagraphProcessor:
    def run(self):
        pass

class OListProcessor:
    def run(self):
        pass

class UListProcessor:
    pass

class HeaderProcessor:
    pass

class EmphasizeProcessor:
    pass

class BlockQuoteProcessor:
    """
    take note of multiline
    """
    pass

class Templating:
    def __init__(self) -> None:
        self.preprocessors = [
            HEADER,
            UNORDEREDLIST,
            ORDEREDLIST,
            CODEBLOCK,
            MERMAID,
            INLINECODE,
            IMAGES,
            MATHJAXBLOCK,
            INLINEMATHJAX,
            BLOCKQUOTES,
            BOLD,
            PARAGRAPH
        ]
        self.processors = []
        self.treeprocessors = ""
        self.postprocessors = []

    def process(self, fname):
        rv = None
        if os.path.isfile(fname):
            with open(fname, "r") as rf:
                lines = rf.read()
            for line in lines:
                if not line.strip():
                    continue
                pass
        else:
            rv = "file does not exists!"
        return rv


t = Templating()

def render_template(**kwargs):
    return t.process()
