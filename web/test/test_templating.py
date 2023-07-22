import os
import unittest
import time

from blog.core import render_template


class TestTemplating(unittest.TestCase):
    def test_render_template(self):
        with open(os.environ.get("REFTEMPLATE"), "r") as rf:
            html_content = rf.read()
        size = len(html_content.encode('utf-8'))
        t = []
        for i in range(100):
            s = time.time()
            rendered_content = render_template(os.environ.get("TESTEMPLATE")) 
            e = time.time()
            t.append(e-s)
        """
        TODO
        ----
        average time taken: 140.03ms for 1.59kb; goal is to get this down to
        hundreds of microseconds range for size of < 50kb range consistently.
        """
        # with open("rendered.html", "w") as wf:
        #     wf.write(rendered_content)
        print("average time taken: {:.2f}ms for {:.2f}kb".format((sum(t)/len(t))*1e6, size*1e-3))
        rc = rendered_content.split("\n")
        hc = html_content.split("\n")
        self.assertEqual(len(rc), len(hc))
        for r, h in zip(rc, hc):
            self.assertEqual(r, h)