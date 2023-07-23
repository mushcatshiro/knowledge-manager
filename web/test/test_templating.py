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
        average time taken: 14156.85ms for 1.59kb; goal is to get this down to
        hundreds of microseconds range for size of < 50kb range consistently.
        suspect regex compile time causes 1st render to be slow, given that the
        time taken was 40k+ ms for 1.59kb.

        7/23 average time taken: 230.00ms for 1.59kb; to investigate why the
        fluctuation in time taken is such big.
        """
        with open("rendered.html", "w") as wf:
            wf.write(rendered_content)
        print("average time taken: {:.2f}ms for {:.2f}kb".format((sum(t)/len(t))*1e6, size*1e-3))
        rc = rendered_content.split("\n")
        hc = html_content.split("\n")
        self.assertEqual(len(rc), len(hc))
        for r, h in zip(rc, hc):
            self.assertEqual(r, h)