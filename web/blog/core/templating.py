"""
markdown syntax

- [x] headers (1-6)
- [x] paragraphs and line breaks (lowest priority)
- [ ] bolds
- [ ] blockquotes
    - [x] single
    - [x] multi
- [ ] lists
  - [x] UL
  - [ ] OL
  - [ ] todo lists
- [ ] links (%20 / whitespace conversion)
  - [ ] referrence links
- [ ] images
- [ ] character escaping
- [ ] code
  - [ ] mermaid blocks
  - [ ] code blocks
  - [ ] inline
- [ ] mathjax [ref](https://docs.mathjax.org/en/latest/basic/mathematics.html)
  - [ ] inline (might want to consider not using ($)[.\s\S]+($))
  - [x] block
- [ ] tables
- [ ] TOC
- [ ] thematic breaks
- [ ] strikethrough
"""
import os
import re
from re import Pattern
from typing import List
from pprint import pprint


# to only compile once
BLOCKQUOTES = re.compile(r"\>\s(.+)\n*")
UNORDEREDLIST = re.compile(r"(\s\s)*-\s(.+)\n*")
TODOLIST = re.compile(r"(\s\s)*-\s\[[x|\s]{1}\](.+)\n*")
INLINECODE = re.compile(r"(`)[.\s\S]+(`)")
BLOCKCODE = re.compile(r"^`{3}.+\n[\w\W\n]+?`{3}\n*?", re.M)
BLOCKCODE_RUN = re.compile(r"(```)(.+)\n([\w\W\n]+?)(```\n*?)", re.M)
HEADER = re.compile(r"(#+)\s(.+)\n*")
EMPHASIZE = re.compile(r"(\*\*)(.)+(\*\*)")
BLOCKMATHJAX = re.compile(r"(\$\$\n)((.|\n)+)")  # need to change
BLOCKMATHJAX_END = re.compile(r"(\$\$)\n\n")
INLINEMATHJAX = re.compile(r"($)[.\s\S]+($)")
IMAGE = re.compile(r"(\!\[)(.)+(\]\(.+\))")
REFERENCE = re.compile(r"")

PREFIX =\
"<!DOCTYPE html>\n"\
"<html>\n"\
"<head>\n"\
"    <meta charset='utf-8'>\n"\
"    <meta http-equiv='X-UA-Compatible' content='IE=edge'>\n"\
"    <title>Page Title</title>\n"\
"    <meta name='viewport' content='width=device-width, initial-scale=1'>\n"\
"</head>\n"\
"<body>\n"

SUFFIX =\
"</body>\n"\
"</html>"

MATHJAXJS =\
"<script type=\"text/javascript\" id=\"MathJax-script\" async=\"\" src=\"https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.9/MathJax.js?config=TeX-MML-AM_CHTML\"></script>\n"\
"<script type=\"text/x-mathjax-config;executed=true\">MathJax.Hub.Config({tex2jax: { inlineMath: [[\"$\",\"$\"],[\"\\(\",\"\\)\"]] },\"HTML-CSS\": {linebreaks: {automatic: true, width: \"container\"}}});\n"\
"</script>\n"

CODEBLOCKJS =\
"<link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/base16/material-palenight.min.css\">\n"\
"<script src=\"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.3.1/highlight.min.js\"></script>\n"\
"<script>hljs.highlightAll();</script>\n"


class BlockProcessorBase:
    """
    should be as functional as possible i.e. no side effects

    NOTE
    ----
    implement a counter to give a feel of complexity. if not implemented within
    blockprocessor, then implement it in the `process` function. to consider
    the complexity of implementation especially for a line that has multiple
    inline elements. a trick to speed up is to identify the `break`-able loops.
    might want to consider to eliminate `check` and `run` and just use a single
    `process` function. the counter should be groupped by the processor type
    to determine the priority of each processor by running a validation against
    the existing markdown files.
    """
    pattern: Pattern = None

    def check(self, line):
        """always check without indentation
        """
        if self.pattern is None:
            raise NotImplementedError
        m = self.pattern.match(line)
        if m:
            return True
        else:
            return False

    def run(self, block):
        """with indentation, can be multiple lines or single line
        to work around the fact that now all inline elements are not processed
        """
        raise NotImplementedError

class ParagraphProcessor(BlockProcessorBase):
    def check(self, block):
        return True

    def run(self, block):
        lines = block.split("\n")
        out = ""
        for line in lines:
            out += "<p>" + line + "</p>\n"
        return out

class ListProcessor(BlockProcessorBase):
    pattern = UNORDEREDLIST

    def run(self, block):
        indent = False
        m = self.pattern.findall(block)
        if m:
            out = ""
            for i in m:
                if i[0] == "":
                    if indent:
                        out += "</ul>\n"
                        indent = False
                    out += "<li>" + i[1] + "</li>\n"
                else:
                    if not indent:
                        indent = True
                        out += "<ul>\n"
                    out += "<li>" + i[1] + "</li>\n"
            return "<ul>\n" + out + "</ul>\n"

class HeaderProcessor(BlockProcessorBase):
    pattern = HEADER

    def run(self, block):
        m = self.pattern.match(block)
        n = len(m.group(1))  # counts number of hash(es)
        return f"<h{n}>" + m.group(2) + f"</h{n}>\n"

class BlockQuoteProcessor(BlockProcessorBase):
    pattern = BLOCKQUOTES

    def run(self, block):
        m = self.pattern.findall(block)
        out = "\n".join(m)
        return "<blockquote>\n" + out + "\n</blockquote>\n"

class BlockMathJaxProcessor(BlockProcessorBase):
    pattern = BLOCKMATHJAX

    def run(self, block):
        # m = self.pattern.match(block)
        # out = m.group(2).strip()
        # return "<math>\n" + out + "\n</math>\n"
        return block

class BlockCodeProcessor(BlockProcessorBase):
    pattern = BLOCKCODE
    pattern_run = BLOCKCODE_RUN

    def check(self, block):
        m = self.pattern.search(block)
        if m:
            return m.start(), m.end()
        else:
            return None, None

    def run(self, block):
        m = self.pattern_run.match(block)
        return f"<pre><code class=\"{m.group(2)}\">" + m.group(3).strip() + "</code></pre>\n"

class EmphasizeProcessor():
    patten = EMPHASIZE

class ImageProcessor():
    pattern = IMAGE

class InlineMathJaxProcessor():
    # TODO to remove, mathjax will figure this out
    pattern = INLINEMATHJAX

class InlineCodeProcessor():
    cont = True
    pass

class LinkProcessor():
    """to take care of referrence type link
    """
    pass

class ReferenceProcessor():
    # check LinkProcessor
    pass

class Templating:
    def __init__(self) -> None:
        self.blockprocessors: List[BlockProcessorBase] = [
            HeaderProcessor(),
            BlockMathJaxProcessor(),
            BlockQuoteProcessor(),
            ListProcessor(),
            ParagraphProcessor()
        ]
        self.doc = []
        self.preprocessor = BlockCodeProcessor() 
        self.inlineprocessors = []
        self.treeprocessors = ""
        self.postprocessors = []
        self.out = ""
        self.err = ""
        self.codeblock = False
        self.mathjax = False

    def process(self, abspath):
        """
        processes markdown file and returns html file. first pass is to
        enumerate the main blocks i.e. those belongs to `BlockProcessorBase`.
        while in the same loop, processes each line with `InlineProcessorBase`.

        args:
        -----
        abspath (str): absolute path to markdown file

        returns:
        --------
        rv (str): html file

        TODO
        ----
        - provide indicator of needed js files e.g. mathjax, mermaid etc.
        - dealing with indentations
        - prettify html (with BS4)
        """
        if os.path.isfile(abspath):
            with open(abspath, "r") as rf:
                doc = rf.read()
            
            """
            pre-processing to extract code blocks. for the pre_chucks, proceed
            with the block processing and followed by the inline processor. for
            the code chunks, proceed with the code/pre processor. finally,
            combine the entire document and use BS4 to beautify the html.
            """
            while True:
                if doc == "":
                    break
                s_i, e_i = self.preprocessor.check(doc)
                
                if s_i:
                    pre_chunks = doc[:s_i]
                    pre_chunks = pre_chunks.strip().split("\n\n")
                    code_chunk = doc[s_i:e_i]
                    code_chunk = self.preprocessor.run(code_chunk)
                    doc = doc[e_i:]
                    self.codeblock = True
                else:
                    pre_chunks = doc.strip().split("\n\n")
                    code_chunk = None

                out = []
                for block in pre_chunks: 
                    for blockprocessor in self.blockprocessors:
                        if blockprocessor.check(block):
                            out.append(blockprocessor.run(block))
                            break
                pre_chunks = "\n".join(out)

                pre_chunks = pre_chunks.strip().split("\n")
                out = []
                for block in pre_chunks:
                    for inlineprocessor in self.inlineprocessors:
                        if block == "\n":
                            # or just append "\n"?
                            out.append("")
                            continue
                        if inlineprocessor.check(block):
                            block = inlineprocessor.run(block)
                    out.append(block)
                pre_chunks = "\n".join(out)
                    
                self.doc.append(pre_chunks)
                if code_chunk:
                    self.doc.append(code_chunk)
            return PREFIX + "".join(self.doc) + CODEBLOCKJS + MATHJAXJS + SUFFIX
        else:
            raise FileNotFoundError(f"{abspath} not found")


t = Templating()

def render_template(abspath):
    return t.process(abspath)
