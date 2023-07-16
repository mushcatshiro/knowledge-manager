import os
import unittest

from blog.core import render_template


class TestTemplating(unittest.TestCase):
    def test_render_template(self):
        with open(os.environ.get("REFTEMPLATE"), "r") as rf:
            html_content = rf.read()
        rendered_content = render_template(os.environ.get("TESTEMPLATE")) 
        rc = rendered_content.split("\n")
        hc = html_content.split("\n")
        self.assertEqual(len(rc), len(hc))
        for r, h in zip(rc, hc):
            self.assertEqual(r, h)