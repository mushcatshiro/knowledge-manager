import os
import unittest

from blog.core import render_template

class TestTemplating(unittest.TestCase):
    def test_render_template(self):
        with open(os.environ.get("REFTEMPLATE"), "r") as rf:
            html_content = rf.read()
        rendered_content = render_template() 
        self.assertEqual(rendered_content, html_content)