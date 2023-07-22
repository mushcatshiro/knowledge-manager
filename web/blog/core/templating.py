"""
markdown syntax

- [x] headers (1-6)
- [x] paragraphs and line breaks (lowest priority)
- [x] bolds and italics
- [ ] blockquotes
    - [x] single
    - [x] multi
- [ ] lists
  - [x] UL
  - [x] OL
  - [ ] todo lists
- [ ] links (%20 / whitespace conversion)
  - [ ] referrence links
- [ ] images
- [ ] character escaping
- [ ] code
  - [ ] mermaid blocks
  - [x] code blocks
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
BLOCKQUOTEPAT = re.compile(r"\>\s(.+)\n*")
LISTPAT = re.compile(r"(\s\s)*(-|\d+\.|)\s\[[x|\s]{1}\]*(.+)\n*")
_TODOLIST = re.compile(r"(\s\s)*-\s\[[x|\s]{1}\](.+)\n*")  # to remove
INLINECODEPAT = re.compile(r"(`)[.\s\S]+(`)")
BLOCKCODEPAT = re.compile(r"^`{3}.+\n[\w\W\n]+?`{3}\n*?", re.M)
BLOCKCODE_RUN = re.compile(r"(```)(.+)\n([\w\W\n]+?)(```\n*?)", re.M)  # to merge
HEADERPAT = re.compile(r"(#+)\s(.+)\n*")
EMPHASIZEPAT = re.compile(r"(\*{1,2})(.+?|\s*)(\*{1,2})")
BLOCKMATHJAXPAT = re.compile(r"(\$\$\n)((.|\n)+)(\$\$)")  # need to change
INLINEMATHJAXPAT = re.compile(r"($)[.\s\S]+($)")
IMAGEPAT = re.compile(r"(\!\[)(.+|\s*)+(\]\()(.+)(\))")
REFERENCEPAT = re.compile(r"")

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


class ProcessorBase:
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

    def check(self, block):
        """always check without indentation
        """
        if self.pattern is None:
            raise NotImplementedError
        m = self.pattern.match(block)
        if m:
            return True
        else:
            return False

    def run(self, block):
        """with indentation, can be multiple lines or single line
        to work around the fact that now all inline elements are not processed
        """
        raise NotImplementedError

class ParagraphProcessor(ProcessorBase):
    def check(self, block):
        return True

    def run(self, block):
        lines = block.split("\n")
        out = ""
        for line in lines:
            out += "<p>" + line + "</p>\n"
        return out

class ListProcessor(ProcessorBase):
    pattern = LISTPAT

    def run(self, block):
        """
        TODO
        ----
        integration with todo list
        """
        indent = False
        m = self.pattern.findall(block)
        if m:
            if m[0][2] == "-":
                ltype = "ul"
            elif m[0][2][:-1].isnumeric():
                ltype = "ol"
            else:
                raise ValueError
            out = ""
            for i in m:
                if i[0] == "":
                    if indent:
                        out += f"</{ltype}l>\n"
                        indent = False
                    out += "<li>" + i[1] + "</li>\n"
                else:
                    if not indent:
                        indent = True
                        out += f"<{ltype}l>\n"
                    out += "<li>" + i[1] + "</li>\n"
            return f"<{ltype}l>\n" + out + f"</{ltype}l>\n"

class HeaderProcessor(ProcessorBase):
    pattern = HEADERPAT

    def run(self, block):
        m = self.pattern.match(block)
        n = len(m.group(1))  # counts number of hash(es)
        return f"<h{n}>" + m.group(2) + f"</h{n}>\n"

class BlockQuoteProcessor(ProcessorBase):
    pattern = BLOCKQUOTEPAT

    def run(self, block):
        m = self.pattern.findall(block)
        out = "\n".join(m)
        return "<blockquote>\n" + out + "\n</blockquote>\n"

class BlockMathJaxProcessor(ProcessorBase):
    pattern = BLOCKMATHJAXPAT

    def run(self, block):
        return block

class BlockCodeProcessor:
    pattern = BLOCKCODEPAT
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

class EmphasizeProcessor(ProcessorBase):
    pattern = EMPHASIZEPAT

    def check(self, block):
        m = self.pattern.search(block)
        if m and (m.group(1) == m.group(3)):
            return True
        else:
            return False

    def run(self, line):
        m = self.pattern.search(line)
        if len(m.group(1)) == 1:
            tag = "em"
        elif len(m.group(1)) == 2:
            tag = "strong"
        return re.sub(self.pattern, rf"<{tag}>\2</{tag}>", line)

class ImageProcessor(ProcessorBase):
    pattern = IMAGEPAT

    def run(self, line):
        # r"(\!\[)(.+|\s*)+(\]\()(.+)(\))"
        m = self.pattern.match(line)
        return f"<img src=\"{m.group(4)}\" alt=\"{m.group(2)}\" title=\"{m.group(2)}\">\n"

class InlineMathJaxProcessor(ProcessorBase):
    # should have higest priority together with inline code
    pattern = INLINEMATHJAXPAT

class InlineCodeProcessor(ProcessorBase):
    pass

class ReferenceProcessor(ProcessorBase):
    # check LinkProcessor
    pass

class Templating:
    def __init__(self) -> None:
        self.blockprocessors: List[ProcessorBase] = [
            HeaderProcessor(),
            BlockMathJaxProcessor(),
            BlockQuoteProcessor(),
            ListProcessor(),
            ParagraphProcessor()
        ]
        self.doc = []
        self.preprocessor = BlockCodeProcessor() 
        self.inlineprocessors = [
            EmphasizeProcessor(),
        ]
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
        if not os.path.isfile(abspath):
            raise FileNotFoundError(f"{abspath} not found")

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
                doc = ""

            out = []
            for block in pre_chunks: 
                for blockprocessor in self.blockprocessors:
                    if blockprocessor.check(block):
                        out.append(blockprocessor.run(block))
                        break
            pre_chunks = "\n".join(out)

            pre_chunks = pre_chunks.strip().split("\n")
            out = []
            for line in pre_chunks:
                for inlineprocessor in self.inlineprocessors:
                    if line == "\n":
                        # or just append "\n"?
                        out.append("")
                        continue
                    if inlineprocessor.check(line):
                        line = inlineprocessor.run(line)
                out.append(line)
            pre_chunks = "\n".join(out)

            self.doc.append(pre_chunks)
            if code_chunk:
                self.doc.append(code_chunk)
        return PREFIX + "".join(self.doc) + CODEBLOCKJS + MATHJAXJS + SUFFIX
        


t = Templating()

def render_template(abspath):
    return t.process(abspath)
