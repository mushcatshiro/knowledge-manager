"""
markdown syntax

- headers (1-6)
- paragraphs and line breaks (lowest priority)
- bolds
- blockquotes (single and multi, other MD elements, 3rd lowest priority)
- lists (UL and OL, other MD elements, 2nd lowest priority)
- links (%20 / whitespace conversion)
  - referrence links
- images
- character escaping?
- code
  - mermaid blocks
  - code blocks
  - inline
- mathjax
  - inline (might want to consider not using ($)[.\s\S]+($))
  - block
"""
import os
import re
from re import Pattern
from typing import List


# to only compile once
BLOCKQUOTES = re.compile(r"(\>)(\s){1}(.)+")
UNORDEREDLIST = re.compile(r"")
ORDEREDLIST = re.compile(r"")
INLINECODE = re.compile(r"(`)[.\s\S]+(`)")
BLOCKCODE = re.compile(r"(```)[.\s\S]+(```)")  # need to change
HEADER = re.compile(r"(#)+(\s){1}(.)+")
ref_HEADER = re.compile(r'(?:^|\n)(?P<level>#{1,6})(?P<header>(?:\\.|[^\\])*?)#*(?:\n|$)')  # noqa
EMPHASIZE = re.compile(r"(\*\*)(.)+(\*\*)")
BLOCKMATHJAX = re.compile(r"($$)[.\s\S]+($$)")  # need to change
INLINEMATHJAX = re.compiel(r"($)[.\s\S]+($)")
IMAGE = re.compile(r"(\!\[)(.)+(\]\(.+\))")
REFERENCE = re.compile(r"")
MERMAID = re.compile(r"(```)mermaid\n")

class BlockProcessorBase:
    """should be as functional as possible i.e. no side effect
    """
    pattern: Pattern = None
    cont: bool = False   # meant for processing multiple lines
    skip: bool = False   # stop after a particular pattern is processed
    block: bool = False  # block's logic is different form inline counterpart

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

    def run(self, lines):
        """with indentation, can be multiple lines or single line
        to work around the fact that now all inline elements are not processed
        """
        raise NotImplementedError

class ParagraphProcessor(BlockProcessorBase):
    skip = True  # technically does not matter
    # to figure out how to deal with None pattern
    def run(self, line):
        return "<p>" + line + "</p>"

class OListProcessor(BlockProcessorBase):
    # having both skip and cont can be confusing
    cont = True
    skip = True
    def run(self):
        pass

class UListProcessor(BlockProcessorBase):
    cont = True
    skip = True
    pass

class HeaderProcessor(BlockProcessorBase):
    pattern = HEADER
    skip = True

    def run(self, line):
        m = self.pattern.match(line)
        n = len(m[0].group(0))  # counts number of hash(es)
        return f"<h{n}>" + line + f"</h{n}>"

class BlockQuoteProcessor(BlockProcessorBase):
    """block logic is different from other block
    """
    block = True
    cont = True

    def run(self, line):
        pass

class BlockMathJaxProcessor(BlockProcessorBase):
    cont = True
    block = True
    skip = True
    pattern = BLOCKMATHJAX
    pass

class BlockCodeProcessor(BlockProcessorBase):
    skip = True
    mermaid_pattern = MERMAID
    pattern = BLOCKCODE

class EmphasizeProcessor(PreprocessorBase):
    patten = EMPHASIZE

class ImageProcessor(PreprocessorBase):
    pattern = IMAGE

class InlineMathJaxProcessor(PreprocessorBase):
    # TODO to remove, mathjax will figure this out
    pattern = INLINEMATHJAX

class InlineCodeProcessor(PreprocessorBase):
    cont = True
    pass


class LinkProcessor(PreprocessorBase):
    """to take care of referrence type link
    """
    pass

class ReferenceProcessor(PreprocessorBase):
    # check LinkProcessor
    pass

class Templating:
    def __init__(self) -> None:
        self.blockprocessors: List[BlockProcessorBase] = [
            HeaderProcessor,
            BlockMathJaxProcessor,
            BlockCodeProcessor, 
            BlockQuoteProcessor,
            UListProcessor,
            OListProcessor,
            ParagraphProcessor
        ]
        self.inlineprocessors = []
        self.treeprocessors = ""
        self.postprocessors = []
        self.out = ""
        self.err = ""

    def process(self, fname):
        rv = None
        if os.path.isfile(fname):
            with open(fname, "r") as rf:
                doc = rf.read()
            
            lines = doc.split("\n\n")

            """
            block processing using a single for loop (passing in chunks)
            by using lines.split("\n\n") one can obtain the logical blocks
            except for paragraph block or shouldnt matter for simplicity sake?

            inline processing using the following intuition
            > s = "asd asd sss asd"
            > p = re.compile(r"asd")  # no sure if re.S flag is needed
            > re.sub(p, lambda match: "aaa".format(*match.group()), s)
            # expected output to be "aaa aaa sss aaa"
            """
            for idx, line in enumerate(lines):
                if not line.strip():
                    for processor in self.blockprocessors:
                        m = processor.check(line.strip())
                        if m == True and processor.cont == True:
                            start = idx
                        elif m == True and processor.cont == False:
                            line = processor.run(line)
                        elif m == False and processor.cont == True:
                            end = idx
                            # to figure out how to select start to end lines
                            line = processor.run(lines[start: end])
                            # reset
                            start = None
                            end = None
                        elif isinstance(processor, ParagraphProcessor):
                            self.err +=\
                                f"\"{line.replace('\n', '')}\" does not match"\
                                " to any markdown pattern defined"
                        self.out += line
                        if processor.skip == True:
                            break
            return self.out
        else:
            rv = "file does not exists!"
        return rv


t = Templating()

def render_template(**kwargs):
    return t.process()
