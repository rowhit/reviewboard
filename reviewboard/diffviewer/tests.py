import reviewboard.diffviewer.diffutils as diffutils
import reviewboard.diffviewer.parser as diffparser
from reviewboard.scmtools.models import Repository
                         [("equal", 0, 3, 0, 3),])
                         [("delete", 0, 3, 0, 0),])

        opcodes = list(diffutils.MyersDiffer(a, b).get_opcodes())
        differ = diffutils.MyersDiffer(a, b)
        diffutils.register_interesting_lines_for_filename(differ, filename)
    def testInterline(self):
        """Testing inter-line diffs"""

        def deepEqual(A, B):
            typea, typeb = type(A), type(B)
            self.assertEqual(typea, typeb)
            if typea is tuple or typea is list:
                for a, b in map(None, A, B):
                    deepEqual(a, b)
            else:
                self.assertEqual(A, B)

        deepEqual(diffutils.get_line_changed_regions(None, None),
                  (None, None))

        old = 'submitter = models.ForeignKey(Person, verbose_name="Submitter")'
        new = 'submitter = models.ForeignKey(User, verbose_name="Submitter")'
        regions = diffutils.get_line_changed_regions(old, new)
        deepEqual(regions, ([(30, 36)], [(30, 34)]))


        old = '-from reviews.models import ReviewRequest, Person, Group'
        new = '+from .reviews.models import ReviewRequest, Group'
        regions = diffutils.get_line_changed_regions(old, new)
        deepEqual(regions, ([(0, 1), (6, 6), (43, 51)],
                            [(0, 1), (6, 7), (44, 44)]))

        old = 'abcdefghijklm'
        new = 'nopqrstuvwxyz'
        regions = diffutils.get_line_changed_regions(old, new)
        deepEqual(regions, (None, None))

        differ = diffutils.Differ(old.splitlines(), new.splitlines())
        for opcodes in diffutils.opcodes_with_metadata(differ):

    fixtures = ['test_scmtools']
    def testLongFilenames(self):