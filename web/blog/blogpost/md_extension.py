from markdown.inlinepatterns import LinkInlineProcessor, IMAGE_LINK_RE
from markdown.extensions import Extension
import xml.etree.ElementTree as etree
import os


class ImageURLInlineProcessor(LinkInlineProcessor):
    def handleMatch(self, m, data):
        """
        modifies `./image.png` to `../IMAGE_URL_PREFIX/image.png` where
        IMAGE_URL_PREFIX is an environment variable
        """
        text, index, handled = self.getText(data, m.end(0))
        if not handled:
            return None, None, None

        src, title, index, handled = self.getLink(data, index)
        if not handled:
            return None, None, None

        el = etree.Element("img")

        target = os.environ.get("IMAGE_URL_PREFIX")
        src = src.replace("./", f"../{target}/")
        el.set("src", src)

        if title is not None:
            el.set("title", title)

        el.set("alt", self.unescape(text))
        return el, m.start(0), index


class ImageURLlExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            ImageURLInlineProcessor(IMAGE_LINK_RE, md), "del", 175
        )  # 175?
