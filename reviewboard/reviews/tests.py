from djblets.testing.decorators import add_fixtures
from kgb import SpyAgency
from reviewboard.reviews.models import (Comment,
                                        DefaultReviewer,
                                        Group,
                                        ReviewRequest,
                                        ReviewRequestDraft,
                                        Review,
                                        Screenshot)
from reviewboard.scmtools.core import Commit
from reviewboard.testing import TestCase
    fixtures = ['test_users']
        user1 = User.objects.get(username='doc')
        user2 = User.objects.get(username='grumpy')
        self.create_review_request(summary='Test 1',
                                   publish=True,
                                   submitter=user1)
        self.create_review_request(summary='Test 2',
                                   submitter=user2)
        self.create_review_request(summary='Test 3',
                                   status='S',
                                   public=True,
                                   submitter=user1)
        self.create_review_request(summary='Test 4',
                                   status='S',
                                   public=True,
                                   submitter=user2)
        self.create_review_request(summary='Test 5',
                                   status='D',
                                   public=True,
                                   submitter=user1)
        self.create_review_request(summary='Test 6',
                                   status='D',
                                   submitter=user2)
            ReviewRequest.objects.public(user1),
            [
                'Test 1',
            ])
        self.assertValidSummaries(
            ReviewRequest.objects.public(status=None),
            [
                'Test 5',
                'Test 4',
                'Test 3',
                'Test 1',
            ])
        self.assertValidSummaries(
            ReviewRequest.objects.public(user2, status=None),
            [
                'Test 6',
                'Test 5',
                'Test 4',
                'Test 3',
                'Test 2',
                'Test 1'
            ])
    def test_to_group(self):
        """Testing ReviewRequest.objects.to_group"""
        user1 = User.objects.get(username='doc')
        group1 = self.create_review_group(name='privgroup')
        group1.users.add(user1)
        review_request = self.create_review_request(summary='Test 1',
                                                    public=True,
                                                    submitter=user1)
        review_request.target_groups.add(group1)
        review_request = self.create_review_request(summary='Test 2',
                                                    public=False,
                                                    submitter=user1)
        review_request.target_groups.add(group1)
        review_request = self.create_review_request(summary='Test 3',
                                                    public=True,
                                                    status='S',
                                                    submitter=user1)
        review_request.target_groups.add(group1)
        self.assertValidSummaries(
            ReviewRequest.objects.to_group("privgroup", None),
            [
                'Test 1',
            ])
        self.assertValidSummaries(
            ReviewRequest.objects.to_group("privgroup", None, status=None),
            [
                'Test 3',
                'Test 1',
            ])
    def test_to_user_group(self):
        """Testing ReviewRequest.objects.to_user_groups"""
        user1 = User.objects.get(username='doc')
        user2 = User.objects.get(username='grumpy')
        group1 = self.create_review_group(name='group1')
        group1.users.add(user1)
        group2 = self.create_review_group(name='group2')
        group2.users.add(user2)
        review_request = self.create_review_request(summary='Test 1',
                                                    public=True,
                                                    submitter=user1)
        review_request.target_groups.add(group1)
        review_request = self.create_review_request(summary='Test 2',
                                                    submitter=user2,
                                                    public=True,
                                                    status='S')
        review_request.target_groups.add(group1)
        review_request = self.create_review_request(summary='Test 3',
                                                    public=True,
                                                    submitter=user2)
        review_request.target_groups.add(group1)
        review_request.target_groups.add(group2)
        self.assertValidSummaries(
            ReviewRequest.objects.to_user_groups("doc", local_site=None),
            [
                'Test 3',
                'Test 1',
            ])
        self.assertValidSummaries(
            ReviewRequest.objects.to_user_groups(
                "doc", status=None, local_site=None),
            [
                'Test 3',
                'Test 2',
                'Test 1',
            ])
        self.assertValidSummaries(
            ReviewRequest.objects.to_user_groups(
                "grumpy", user=user2, local_site=None),
            [
                'Test 3',
            ])
    def test_to_user_directly(self):
        """Testing ReviewRequest.objects.to_user_directly"""
        user1 = User.objects.get(username='doc')
        user2 = User.objects.get(username='grumpy')
        group1 = self.create_review_group(name='group1')
        group1.users.add(user1)
        group2 = self.create_review_group(name='group2')
        group2.users.add(user2)
        review_request = self.create_review_request(summary='Test 1',
                                                    public=True,
                                                    submitter=user1)
        review_request.target_groups.add(group1)
        review_request.target_people.add(user2)
        review_request = self.create_review_request(summary='Test 2',
                                                    submitter=user2,
                                                    status='S')
        review_request.target_groups.add(group1)
        review_request.target_people.add(user2)
        review_request.target_people.add(user1)
        review_request = self.create_review_request(summary='Test 3',
                                                    public=True,
                                                    submitter=user2)
        review_request.target_groups.add(group1)
        review_request.target_groups.add(group2)
        review_request.target_people.add(user1)
        review_request = self.create_review_request(summary='Test 4',
                                                    public=True,
                                                    status='S',
                                                    submitter=user2)
        review_request.target_people.add(user1)
        self.assertValidSummaries(
            ReviewRequest.objects.to_user_directly("doc", local_site=None),
            [
                'Test 3',
            ])
        self.assertValidSummaries(
            ReviewRequest.objects.to_user_directly("doc", status=None),
            [
                'Test 4',
                'Test 3',
            ])
        self.assertValidSummaries(
            ReviewRequest.objects.to_user_directly(
                "doc", user2, status=None, local_site=None),
            [
                'Test 4',
                'Test 3',
                'Test 2',
            ])
    def test_from_user(self):
        """Testing ReviewRequest.objects.from_user"""
        user1 = User.objects.get(username='doc')
        self.create_review_request(summary='Test 1',
                                   public=True,
                                   submitter=user1)
        self.create_review_request(summary='Test 2',
                                   public=False,
                                   submitter=user1)
        self.create_review_request(summary='Test 3',
                                   public=True,
                                   status='S',
                                   submitter=user1)
            ReviewRequest.objects.from_user("doc", local_site=None),
            [
                'Test 1',
            ])
            ReviewRequest.objects.from_user("doc", status=None,
                                            local_site=None),
            [
                'Test 3',
                'Test 1',
            ])
            ReviewRequest.objects.from_user(
                "doc", user=user1, status=None, local_site=None),
            [
                'Test 3',
                'Test 2',
                'Test 1',
            ])
    def to_user(self):
        """Testing ReviewRequest.objects.to_user"""
        user1 = User.objects.get(username='doc')
        user2 = User.objects.get(username='grumpy')
        group1 = self.create_review_group(name='group1')
        group1.users.add(user1)
        group2 = self.create_review_group(name='group2')
        group2.users.add(user2)
        review_request = self.create_review_request(summary='Test 1',
                                                    publish=True,
                                                    submitter=user1)
        review_request.target_groups.add(group1)
        review_request = self.create_review_request(summary='Test 2',
                                                    submitter=user2,
                                                    status='S')
        review_request.target_groups.add(group1)
        review_request.target_people.add(user2)
        review_request.target_people.add(user1)
        review_request = self.create_review_request(summary='Test 3',
                                                    publish=True,
                                                    submitter=user2)
        review_request.target_groups.add(group1)
        review_request.target_groups.add(group2)
        review_request.target_people.add(user1)
        review_request = self.create_review_request(summary='Test 4',
                                                    publish=True,
                                                    status='S',
                                                    submitter=user2)
        review_request.target_groups.add(group1)
        review_request.target_groups.add(group2)
        review_request.target_people.add(user1)
            ReviewRequest.objects.to_user("doc", local_site=None),
            [
                'Test 3',
                'Test 1',
            ])
            ReviewRequest.objects.to_user("doc", status=None, local_site=None),
            [
                'Test 4',
                'Test 3',
                'Test 1',
            ])
            ReviewRequest.objects.to_user(
                "doc", user=user2, status=None, local_site=None),
            [
                'Test 4',
                'Test 3',
                'Test 2',
                'Test 1',
            ])
            self.assertTrue(summary in summaries,
                            u'summary "%s" not found in summary list'
                            % summary)
            self.assertTrue(summary in r_summaries,
                            u'summary "%s" not found in review request list'
                            % summary)
    fixtures = ['test_users', 'test_scmtools', 'test_site']
        review_request = self.create_review_request(publish=True)
        username = 'admin'
        summary = 'This is a test summary'
        description = 'This is my description'
        testing_done = 'Some testing'
        review_request = self.create_review_request(
            publish=True,
            submitter=username,
            summary=summary,
            description=description,
            testing_done=testing_done)
        response = self.client.get('/r/%s/' % review_request.pk)
        self.assertEqual(response.status_code, 200)
        request = self.getContextVar(response, 'review_request')
        self.assertEqual(request.submitter.username, username)
        self.assertEqual(request.summary, summary)
        self.assertEqual(request.description, description)
        self.assertEqual(request.testing_done, testing_done)
        self.assertEqual(request.pk, review_request.pk)
        review_request = self.create_review_request(create_repository=True,
                                                    publish=True)
        diffset = self.create_diffset(review_request)
        filediff = self.create_filediff(diffset)
        main_review = self.create_review(review_request, user=user1)
        main_comment = self.create_diff_comment(main_review, filediff,
                                                text=comment_text_1)
        reply1 = self.create_reply(
            main_review,
            user=user1,
            timestamp=(main_review.timestamp + timedelta(days=1)))
        self.create_diff_comment(reply1, filediff, text=comment_text_2,
                                 reply_to=main_comment)
        reply2 = self.create_reply(
            main_review,
            user=user2,
            timestamp=(main_review.timestamp + timedelta(days=2)))
        self.create_diff_comment(reply2, filediff, text=comment_text_3,
                                 reply_to=main_comment)
        comments = entry['comments']['diff_comments']
        filename = os.path.join(settings.STATIC_ROOT,
                                'rb', 'images', 'trophy.png')
                                              file=file,
                                              mimetype='image/png')
                                              file=file,
                                              mimetype='image/png')
                                              file=file,
                                              mimetype='image/png')
        comments = entry['comments']['file_attachment_comments']
        comments = entry['comments']['screenshot_comments']

        self.create_review_request(publish=True)

        self.create_review_request(summary='Test 1', publish=True)
        self.create_review_request(summary='Test 2', publish=True)
        self.create_review_request(summary='Test 3', publish=True)

        self.assertTrue(datagrid)
        self.assertEqual(len(datagrid.rows), 3)
        self.assertEqual(datagrid.rows[0]['object'].summary, 'Test 3')
        self.assertEqual(datagrid.rows[1]['object'].summary, 'Test 2')
        self.assertEqual(datagrid.rows[2]['object'].summary, 'Test 1')
        self.assertTrue(datagrid)
        self.create_review_group(name='devgroup')
        self.create_review_group(name='emptygroup')
        self.create_review_group(name='newgroup')
        self.create_review_group(name='privgroup')

        self.assertTrue(datagrid)
        user = User.objects.get(username='doc')

        review_request = self.create_review_request(summary='Test 1',
                                                    publish=True)
        review_request.target_people.add(user)

        review_request = self.create_review_request(summary='Test 2',
                                                    publish=True)
        review_request.target_people.add(user)

        review_request = self.create_review_request(summary='Test 3',
                                                    publish=True)

        self.assertTrue(datagrid)
        self.assertEqual(len(datagrid.rows), 2)
        self.assertEqual(datagrid.rows[0]['object'].summary, 'Test 2')
        self.assertEqual(datagrid.rows[1]['object'].summary, 'Test 1')
        user = User.objects.get(username='admin')

        self.create_review_request(summary='Test 1',
                                   submitter=user,
                                   publish=True)

        self.create_review_request(summary='Test 2',
                                   submitter=user,
                                   publish=True)

        self.create_review_request(summary='Test 3',
                                   submitter='grumpy',
                                   publish=True)

        self.assertTrue(datagrid)
        self.assertEqual(datagrid.rows[0]['object'].summary, 'Test 2')
        self.assertEqual(datagrid.rows[1]['object'].summary, 'Test 1')
        user = User.objects.get(username='doc')

        group = self.create_review_group()
        group.users.add(user)

        review_request = self.create_review_request(summary='Test 1',
                                                    publish=True)
        review_request.target_people.add(user)

        review_request = self.create_review_request(summary='Test 2',
                                                    publish=True)
        review_request.target_people.add(user)

        review_request = self.create_review_request(summary='Test 3',
                                                    publish=True)
        review_request.target_groups.add(group)

        self.assertTrue(datagrid)
        self.assertEqual(datagrid.rows[0]['object'].summary, 'Test 2')
        self.assertEqual(datagrid.rows[1]['object'].summary, 'Test 1')
        group = self.create_review_group(name='devgroup')

        review_request = self.create_review_request(summary='Test 1',
                                                    publish=True)
        review_request.target_groups.add(group)

        review_request = self.create_review_request(summary='Test 2',
                                                    publish=True)
        review_request.target_groups.add(group)

        review_request = self.create_review_request(summary='Test 3',
                                                    publish=True)
        review_request.target_groups.add(
            self.create_review_group(name='test-group'))

        self.assertTrue(datagrid)
        self.assertEqual(datagrid.rows[0]['object'].summary, 'Test 2')
        self.assertEqual(datagrid.rows[1]['object'].summary, 'Test 1')
        """Testing dashboard sidebar counts"""
        profile = Profile.objects.get(user=user)

        # Create all the test data.
        devgroup = self.create_review_group(name='devgroup')
        devgroup.users.add(user)

        privgroup = self.create_review_group(name='privgroup')
        privgroup.users.add(user)

        review_request = self.create_review_request(submitter=user,
                                                    publish=True)

        review_request = self.create_review_request(submitter='grumpy')
        draft = ReviewRequestDraft.create(review_request)
        draft.target_people.add(user)
        review_request.publish(review_request.submitter)
        review_request = self.create_review_request(submitter='grumpy')
        draft = ReviewRequestDraft.create(review_request)
        draft.target_groups.add(devgroup)
        review_request.publish(review_request.submitter)

        review_request = self.create_review_request(submitter='grumpy')
        draft = ReviewRequestDraft.create(review_request)
        draft.target_groups.add(privgroup)
        review_request.publish(review_request.submitter)
        profile.star_review_request(review_request)

        # Now get the counts.
        counts = self.getContextVar(response, 'sidebar_counts')
        self.assertEqual(counts['outgoing'], 1)
        self.assertEqual(counts['incoming'], 3)
        self.assertEqual(counts['to-me'], 1)
        self.assertEqual(counts['starred'], 1)
        self.assertEqual(counts['mine'], 1)
        self.assertEqual(counts['groups']['devgroup'], 1)
        self.assertEqual(counts['groups']['privgroup'], 1)
        review_request = self.create_review_request(create_repository=True,
                                                    publish=True)
        diffset = self.create_diffset(review_request, revision=1)
        self.create_filediff(
            diffset,
            source_file='/diffutils.py',
            dest_file='/diffutils.py',
            source_revision='6bba278',
            dest_detail='465d217',
            diff=(
                'diff --git a/diffutils.py b/diffutils.py\n'
                'index 6bba278..465d217 100644\n'
                '--- a/diffutils.py\n'
                '+++ b/diffutils.py\n'
                '@@ -1,3 +1,4 @@\n'
                '+# diffutils.py\n'
                ' import fnmatch\n'
                ' import os\n'
                ' import re\n'
            ))
        self.create_filediff(
            diffset,
            source_file='/readme',
            dest_file='/readme',
            source_revision='d6613f5',
            dest_detail='5b50866',
            diff=(
                'diff --git a/readme b/readme\n'
                'index d6613f5..5b50866 100644\n'
                '--- a/readme\n'
                '+++ b/readme\n'
                '@@ -1 +1,3 @@\n'
                ' Hello there\n'
                '+\n'
                '+Oh hi!\n'
            ))
        self.create_filediff(
            diffset,
            source_file='/newfile',
            dest_file='/newfile',
            source_revision='PRE-CREATION',
            dest_detail='',
            diff=(
                'diff --git a/new_file b/new_file\n'
                'new file mode 100644\n'
                'index 0000000..ac30bd3\n'
                '--- /dev/null\n'
                '+++ b/new_file\n'
                '@@ -0,0 +1 @@\n'
                '+This is a new file!\n'
            ))

        diffset = self.create_diffset(review_request, revision=2)
        self.create_filediff(
            diffset,
            source_file='/diffutils.py',
            dest_file='/diffutils.py',
            source_revision='6bba278',
            dest_detail='465d217',
            diff=(
                'diff --git a/diffutils.py b/diffutils.py\n'
                'index 6bba278..465d217 100644\n'
                '--- a/diffutils.py\n'
                '+++ b/diffutils.py\n'
                '@@ -1,3 +1,4 @@\n'
                '+# diffutils.py\n'
                ' import fnmatch\n'
                ' import os\n'
                ' import re\n'
            ))
        self.create_filediff(
            diffset,
            source_file='/readme',
            dest_file='/readme',
            source_revision='d6613f5',
            dest_detail='5b50867',
            diff=(
                'diff --git a/readme b/readme\n'
                'index d6613f5..5b50867 100644\n'
                '--- a/readme\n'
                '+++ b/readme\n'
                '@@ -1 +1,3 @@\n'
                ' Hello there\n'
                '+----------\n'
                '+Oh hi!\n'
            ))
        self.create_filediff(
            diffset,
            source_file='/newfile',
            dest_file='/newfile',
            source_revision='PRE-CREATION',
            dest_detail='',
            diff=(
                'diff --git a/new_file b/new_file\n'
                'new file mode 100644\n'
                'index 0000000..ac30bd4\n'
                '--- /dev/null\n'
                '+++ b/new_file\n'
                '@@ -0,0 +1 @@\n'
                '+This is a diffent version of this new file!\n'
            ))

        response = self.client.get('/r/1/diff/1-2/')
        self.assertEqual(
            self.getContextVar(response, 'diff_context')['num_diffs'],
            2)
        self.assertTrue(files)
        self.assertEqual(files[0]['depot_filename'], '/newfile')
        self.assertTrue('interfilediff' in files[0])
        self.assertEqual(files[1]['depot_filename'], '/readme')
        self.assertTrue('interfilediff' in files[1])
        review_request = self.create_review_request(create_repository=True,
                                                    publish=True)
        diffset = self.create_diffset(review_request, revision=1)
        self.create_filediff(
            diffset,
            source_file='/diffutils.py',
            dest_file='/diffutils.py',
            source_revision='6bba278',
            dest_detail='465d217',
            diff=(
                'diff --git a/diffutils.py b/diffutils.py\n'
                'index 6bba278..465d217 100644\n'
                '--- a/diffutils.py\n'
                '+++ b/diffutils.py\n'
                '@@ -1,3 +1,4 @@\n'
                '+# diffutils.py\n'
                ' import fnmatch\n'
                ' import os\n'
                ' import re\n'
            ))

        diffset = self.create_diffset(review_request, revision=2)
        self.create_filediff(
            diffset,
            source_file='/diffutils.py',
            dest_file='/diffutils.py',
            source_revision='6bba278',
            dest_detail='465d217',
            diff=(
                'diff --git a/diffutils.py b/diffutils.py\n'
                'index 6bba278..465d217 100644\n'
                '--- a/diffutils.py\n'
                '+++ b/diffutils.py\n'
                '@@ -1,3 +1,4 @@\n'
                '+# diffutils.py\n'
                ' import fnmatch\n'
                ' import os\n'
                ' import re\n'
            ))
        self.create_filediff(
            diffset,
            source_file='/newfile',
            dest_file='/newfile',
            source_revision='PRE-CREATION',
            dest_detail='',
            diff=(
                'diff --git a/new_file b/new_file\n'
                'new file mode 100644\n'
                'index 0000000..ac30bd4\n'
                '--- /dev/null\n'
                '+++ b/new_file\n'
                '@@ -0,0 +1 @@\n'
                '+This is a diffent version of this new file!\n'
            ))

        response = self.client.get('/r/1/diff/1-2/')
        self.assertEqual(
            self.getContextVar(response, 'diff_context')['num_diffs'],
            2)
        self.assertTrue(files)
        self.assertEqual(files[0]['depot_filename'], '/newfile')
        self.assertTrue('interfilediff' in files[0])
        self.create_review_request(summary='Test 1',
                                   submitter='doc',
                                   publish=True)
        self.create_review_request(summary='Test 2',
                                   submitter='doc',
                                   publish=True)
        self.create_review_request(summary='Test 3',
                                   submitter='grumpy',
                                   publish=True)

        self.assertTrue(datagrid is not None)
        self.assertEqual(datagrid.rows[0]['object'].summary, 'Test 2')
        self.assertEqual(datagrid.rows[1]['object'].summary, 'Test 1')
        review_request = self.create_review_request(create_repository=True,
                                                    publish=True)
        diffset = self.create_diffset(review_request)
        filediff = self.create_filediff(diffset)
        review = self.create_review(review_request, user=user)
        comment = self.create_diff_comment(review, filediff,
                                           issue_opened=True)
    fixtures = ['test_users', 'test_scmtools']
        self.assertTrue("summary" in fields)
        self.assertTrue("description" in fields)
        self.assertTrue("testing_done" in fields)
        self.assertTrue("branch" in fields)
        self.assertTrue("bugs_closed" in fields)
        review_request = self.create_review_request(publish=True)
        return ReviewRequestDraft.create(review_request)
    def test_long_bug_numbers(self):
    def test_no_summary(self):
    @add_fixtures(['test_users'])
    def test_commit_id(self):
        """Testing commit_id migration"""
        review_request = self.create_review_request()
        review_request.changenum = '123'

        self.assertEqual(review_request.commit_id, None)
        self.assertEqual(review_request.commit,
                         str(review_request.changenum))
        self.assertNotEqual(review_request.commit_id, None)


class PostCommitTests(SpyAgency, TestCase):
    fixtures = ['test_users', 'test_scmtools']

    def setUp(self):
        self.user = User.objects.create(username='testuser', password='')
        self.profile, is_new = Profile.objects.get_or_create(user=self.user)
        self.profile.save()

        self.testdata_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'scmtools', 'testdata')

        self.repository = self.create_repository(tool_name='Test')

    def test_update_from_committed_change(self):
        """Testing post-commit update"""
        commit_id = '4'

        def get_change(repository, commit_to_get):
            self.assertEqual(commit_id, commit_to_get)

            commit = Commit()
            commit.message = \
                'This is my commit message\n\nWith a summary line too.'
            diff_filename = os.path.join(self.testdata_dir, 'git_readme.diff')
            f = open(diff_filename, 'r')
            commit.diff = f.read()
            f.close()

            return commit

        def get_file_exists(repository, path, revision, base_commit_id=None,
                            request=None):
            return (path, revision) in [('/readme', 'd6613f5')]

        self.spy_on(self.repository.get_change, call_fake=get_change)
        self.spy_on(self.repository.get_file_exists, call_fake=get_file_exists)

        review_request = ReviewRequest.objects.create(self.user,
                                                      self.repository)
        review_request.update_from_commit_id(commit_id)

        self.assertEqual(review_request.summary, 'This is my commit message')
        self.assertEqual(review_request.description,
                         'With a summary line too.')

        self.assertEqual(review_request.diffset_history.diffsets.count(), 1)

        diffset = review_request.diffset_history.diffsets.get()
        self.assertEqual(diffset.files.count(), 1)

        fileDiff = diffset.files.get()
        self.assertEqual(fileDiff.source_file, '/readme')
        self.assertEqual(fileDiff.source_revision, 'd6613f5')

    def test_update_from_committed_change_without_repository_support(self):
        """Testing post-commit update failure conditions"""
        self.spy_on(self.repository.__class__.supports_post_commit.fget,
                    call_fake=lambda self: False)
        review_request = ReviewRequest.objects.create(self.user,
                                                      self.repository)

        self.assertRaises(NotImplementedError,
                          lambda: review_request.update_from_commit_id('4'))

    fixtures = ['test_users', 'test_scmtools']
        review_request = self.create_review_request(create_repository=True,
                                                    publish=True)
        diffset = self.create_diffset(review_request)
        filediff = self.create_filediff(diffset)
        master_review = self.create_review(review_request, user=user,
                                           body_top=body_top,
                                           body_bottom='')
        self.create_diff_comment(master_review, filediff, text=comment_text_1,
                                 first_line=1, num_lines=1)
        review = self.create_review(review_request, user=user,
                                    body_top='', body_bottom='')
        self.create_diff_comment(review, filediff, text=comment_text_2,
                                 first_line=1, num_lines=1)
        review = self.create_review(review_request, user=user,
                                    body_top='',
                                    body_bottom=body_bottom)
        self.create_diff_comment(review, filediff, text=comment_text_3,
                                 first_line=1, num_lines=1)
        self.assertTrue(review)
        self.assertEqual(len(default_reviewers), 2)
        self.assertTrue(default_reviewer1 in default_reviewers)
        self.assertTrue(default_reviewer2 in default_reviewers)
        self.assertEqual(len(default_reviewers), 1)
        self.assertTrue(default_reviewer2 in default_reviewers)
        default_reviewers = DefaultReviewer.objects.for_repository(
            None, test_site)
        self.assertEqual(len(default_reviewers), 1)
        self.assertTrue(default_reviewer1 in default_reviewers)
        self.assertEqual(len(default_reviewers), 1)
        self.assertTrue(default_reviewer2 in default_reviewers)
    fixtures = ['test_users']
    def test_group_invite_only_review_request_ownership(self):
        """Testing visibility of review requests assigned to invite-only groups by a non-member"""
        group = Group.objects.create(name='test-group', visible=False,
                                     invite_only=True)

        review_request = self.create_review_request(publish=True,
                                                    submitter=self.user)
        review_request.target_groups.add(group)

        self.assertTrue(review_request.is_accessible_by(self.user))

    @add_fixtures(['test_scmtools'])
    @add_fixtures(['test_scmtools'])
    @add_fixtures(['test_scmtools'])
    @add_fixtures(['test_scmtools'])
        review_request = self.create_review_request(publish=True)
        review_request = self.create_review_request(publish=True)
        review_request = self.create_review_request(publish=True)
    @add_fixtures(['test_scmtools'])
        review_request = self.create_review_request(create_repository=True,
                                                    publish=True)
    @add_fixtures(['test_scmtools'])
        review_request = self.create_review_request(create_repository=True,
                                                    publish=True)
    @add_fixtures(['test_scmtools'])
        review_request = self.create_review_request(create_repository=True,
                                                    publish=True)