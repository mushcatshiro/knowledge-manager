import re
import string
import os
import math
from collections import Counter
from dataclasses import dataclass
import logging


logger = logging.getLogger(__name__)

try:
    import Stemmer
except ImportError:
    logger.warning("Stemmer module not available")
    Stemmer = None

STOP_WORDS = [
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "that",
    "the",
    "to",
    "was",
    "were",
    "will",
    "with",
]

STEMMER = Stemmer.Stemmer("english") if Stemmer else None

PUNCTUATION = re.compile("[%s]" % re.escape(string.punctuation))


def preprocess_text(text: str):
    text = text.lower()
    text: list[str] = text.split()

    text = [word for word in text if word not in STOP_WORDS]
    text = [PUNCTUATION.sub("", word) for word in text if PUNCTUATION.sub("", word)]

    if STEMMER is not None:
        text = STEMMER.stemWord(text)
    return text


@dataclass
class Document:
    idx: int
    title: str
    content: str

    def analyze(self):
        self.tokens = preprocess_text(f"{self.title} {self.content}")
        self.term_frequencies = Counter(self.tokens)

    def term_frequency(self, term):
        return self.term_frequencies.get(term, 0)


class Index:
    def __init__(self):
        self.index = {}
        self.documents = {}
        self.ctr = 0

    def index_markdown_documents(self, directory):
        for filename in os.listdir(directory):
            if not filename.endswith(".md"):
                continue
            with open(os.path.join(directory, filename)) as f:
                content = f.read()
                # markdown to HTML conversion to extract text only
                document = Document(self.ctr, filename, content)
                self.index_document(document)
            self.ctr += 1

    def index_document(self, document: Document):
        """
        main entrypoint
        """
        if document.idx not in self.documents:
            self.documents[document.idx] = document
            document.analyze()

        for token in document.tokens:
            if token not in self.index:
                self.index[token] = set()
            self.index[token].add(document.idx)

    def document_frequency(self, token):
        return len(self.index.get(token, set()))

    def inverse_document_frequency(self, token):
        # Manning, Hinrich and Schütze use log10, so we do too, even though it
        # doesn't really matter which log we use anyway
        # https://nlp.stanford.edu/IR-book/html/htmledition/inverse-document-frequency-1.html
        return math.log10(len(self.documents) / self.document_frequency(token))

    def _results(self, analyzed_query):
        return [self.index.get(token, set()) for token in analyzed_query]

    def search(self, query, search_type="AND", rank=False):
        """
        Search; this will return documents that contain words from the query,
        and rank them if requested (sets are fast, but unordered).

        Parameters:
          - query: the query string
          - search_type: ('AND', 'OR') do all query terms have to match, or just one
          - score: (True, False) if True, rank results based on TF-IDF score
        """
        if search_type not in ("AND", "OR"):
            return []

        analyzed_query = preprocess_text(query)
        results = self._results(analyzed_query)
        if search_type == "AND":
            # all tokens must be in the document
            documents = [
                self.documents[doc_id] for doc_id in set.intersection(*results)
            ]
        if search_type == "OR":
            # only one token has to be in the document
            documents = [self.documents[doc_id] for doc_id in set.union(*results)]

        if rank:
            return self.rank(analyzed_query, documents)
        return documents

    def rank(self, analyzed_query, documents):
        results = []
        if not documents:
            return results
        for document in documents:
            document: Document
            score = 0.0
            for token in analyzed_query:
                tf = document.term_frequency(token)
                idf = self.inverse_document_frequency(token)
                score += tf * idf
            results.append((document, score))
        return sorted(results, key=lambda doc: doc[1], reverse=True)


class IndexExt:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        self.index = Index()

    def init_app(self, app):
        config: dict = app.config
        markdown_directory = config.get("MARKDOWN_DIRECTORY", "")
        if markdown_directory:
            self.index.index_documents(markdown_directory)
