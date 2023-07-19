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
  - [ ] block
- [ ] tables
- [ ] TOC
- [ ] thematic breaks
- [ ] strikethrough
"""
import os
import re
from re import Pattern
from typing import List


# to only compile once
BLOCKQUOTES = re.compile(r"\>\s(.+)\n*")
GENERALLIST = re.compile(r"(\s\s)*(-{1}|\d+\.)\s(.+)\n*")
ORDEREDLIST = re.compile(r"")
TODOLIST = re.compile(r"(\s\s)*-\s\[[x|\s]{1}\](.+)\n*")
INLINECODE = re.compile(r"(`)[.\s\S]+(`)")
BLOCKCODE = re.compile(r"^`{3}.+\n[\w\W\n]+?`{3}\n*?", re.M)
HEADER = re.compile(r"(#+)\s(.+)\n*")
ref_HEADER = re.compile(r'(?:^|\n)(?P<level>#{1,6})(?P<header>(?:\\.|[^\\])*?)#*(?:\n|$)')  # noqa
EMPHASIZE = re.compile(r"(\*\*)(.)+(\*\*)")
BLOCKMATHJAX = re.compile(r"(\$\$\n)((.|\n)+)")  # need to change
BLOCKMATHJAX_END = re.compile(r"(\$\$)\n\n")
INLINEMATHJAX = re.compile(r"($)[.\s\S]+($)")
IMAGE = re.compile(r"(\!\[)(.)+(\]\(.+\))")
REFERENCE = re.compile(r"")


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
        """
        attempt to deal with the compatibility of codeblocks and paragraphs
        by returning unformatted block if it is a codeblock. also to append
        \n\n
        """
        lines = block.split("\n")
        out = ""
        for line in lines:
            out += "<p>" + line + "</p>\n"
        return out

class ListProcessor(BlockProcessorBase):
    pattern = GENERALLIST

    def run(self, block):
        """
        NOTE
        ----
        current algorithm only support strict unordered list or ordered list
        mixed ordered and unordered list is not supported
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
                        out += f"</{ltype}>\n"
                        indent = False
                    out += "<li>" + i[1] + "</li>\n"
                else:
                    if not indent:
                        indent = True
                        out += f"<{ltype}>\n"
                    out += "<li>" + i[1] + "</li>\n"
            return f"<{ltype}>\n" + out + f"</{ltype}>\n"

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
    """
    need to figure out how make the expression lazy i.e. only a pair
    of ```
    """
    pattern = BLOCKMATHJAX

    def run(self, block):
        m = self.pattern.match(block)
        out = m.group(2).strip()
        return "<math>\n" + out + "\n</math>\n"

class BlockCodeProcessor(BlockProcessorBase):
    """
    need to figure out how make the expression lazy i.e. only a pair
    of ```
    """
    pattern = BLOCKCODE

    def run(self, block):
        m = self.pattern.search(block)
        if m:
            #     for i in m:
            #         out = i[2].strip()
            #         return "<code>\n" + out + "\n</code>\n"
            # return "<code>\n" + m.group(3) + "\n</code>\n"
            return m.start(), m.end()
        else:
            return None, None

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
            UListProcessor(),
            ParagraphProcessor()
        ]
        self.doc = []
        self.preprocessor = BlockCodeProcessor() 
        self.inlineprocessors = []
        self.treeprocessors = ""
        self.postprocessors = []
        self.out = ""
        self.err = ""

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
        rv = None
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
                if self.preprocessor.check(doc):
                    # what if there is no code block?
                    pre_chunks = doc[:s_i]
                    pre_chunks = pre_chunks.strip().split("\n\n")
                    out = []
                    for blockprocessor in self.blockprocessors:
                        for chunk in pre_chunks:
                            if blockprocessor.check(chunk):
                                out.append(blockprocessor.run(chunk))
                                break
                    pre_chunks = "\n\n".join(out)
                    pre_chunks = pre_chunks.strip().split("\n")
                    out = []
                    for inlineprocessor in self.inlineprocessors:
                        for chunk in pre_chunks:
                            if chunk == "\n":
                                out.append("")
                                continue
                            if inlineprocessor.check(chunk):
                                chunk = inlineprocessor.run(chunk)
                        out.append(chunk)
                    pre_chunks = "\n".join(out)

                    code_chunk = doc[s_i:e_i]
                    code_chunk = self.preprocessor.run(code_chunk)
                    
                    self.doc.append(pre_chunks)
                    self.doc.append(code_chunk)
                    doc = doc[e_i:]
                else:
                    break
        else:
            rv = "file does not exists!"
            return rv

    def process_alt(self, abspath):
        with open(abspath, "r") as rf:
            doc = rf.read()
        
        for blockprocessor in self.blockprocessors:
            m = blockprocessor.check(doc)
            if m:
                self.out += blockprocessor.run(doc)
        print(self.out)

t = Templating()

def render_template(abspath):
    return t.process(abspath)
