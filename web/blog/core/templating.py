"""
markdown syntax

- [x] headers (1-6)
- [x] paragraphs and line breaks (lowest priority)
- [ ] bolds
- [ ] blockquotes
    - [ ] single
    - [ ] multi
- [ ] lists
  - [x] UL
  - [ ] OL
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
"""
import os
import re
from re import Pattern
from typing import List


# to only compile once
BLOCKQUOTES = re.compile(r"\>\s(.+)\n*")
GENERALLIST = re.compile(r"(\s\s)*(-{1}|\d+\.)\s(.+)\n*")
ORDEREDLIST = re.compile(r"")
INLINECODE = re.compile(r"(`)[.\s\S]+(`)")
BLOCKCODE = re.compile(r"(```)(.+\n)((.|\n)+)(```)")  # need to change
HEADER = re.compile(r"(#+)\s(.+)\n*")
ref_HEADER = re.compile(r'(?:^|\n)(?P<level>#{1,6})(?P<header>(?:\\.|[^\\])*?)#*(?:\n|$)')  # noqa
EMPHASIZE = re.compile(r"(\*\*)(.)+(\*\*)")
BLOCKMATHJAX = re.compile(r"(\$\$\n)((.|\n)+)(\$\$)")  # need to change
INLINEMATHJAX = re.compile(r"($)[.\s\S]+($)")
IMAGE = re.compile(r"(\!\[)(.)+(\]\(.+\))")
REFERENCE = re.compile(r"")
MERMAID = re.compile(r"(```)mermaid\n(```)")


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
        m = self.pattern.match(block)
        return "<code>\n" + m.group(3) + "\n</code>\n"

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
            blocks = doc.split("\n\n")

            """
            block processing using a single for loop (passing in chunks)
            by using lines.split("\n\n") one can obtain the logical blocks
            except for paragraph block or shouldnt matter for simplicity sake?

            inline processing using the following intuition
            > s = "asd asd sss asd"
            > p = re.compile(r"asd")  # no sure if re.S flag is needed
            > re.sub(p, lambda match: "aaa".format(*match.group()), s)
            # expected output to be "aaa aaa sss aaa"

            NOTE
            ----
            need to figure out how to deal with multiple inlineprocessors on
            single line. one way is to use a for loop within the
            blockprocessors.
            or can just match the entire file and process them by priority? the
            complexity is just O(n) where n is the number of patterns defined.
            """
            for idx, block in enumerate(blocks):
                if block.strip():
                    for blockprocessor in self.blockprocessors:
                        m = blockprocessor.check(block.strip())
                        # line_out = ""  # might want to make a copy
                        # for line in block.split("\n"):
                        #     for inlineprocessor in self.inlineprocessors:
                        #         m = inlineprocessor.check(line)
                        #         if m:
                        #             out = inlineprocessor.run(line)
                        #         else:
                        #             out = line
                        #         line_out += out
                        if m:
                            block_out = blockprocessor.run(block.strip())
                            self.out += block_out
                            break
            return self.out.strip()
        else:
            rv = "file does not exists!"
            return rv


t = Templating()

def render_template(abspath):
    return t.process(abspath)
