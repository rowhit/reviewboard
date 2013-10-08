import httplib
import json
from django.conf import settings
from django.core.cache import cache
from reviewboard.hostingsvcs.errors import (AuthorizationError,
                                            InvalidPlanError,
                                            SSHKeyAssociationError)
from reviewboard.scmtools.core import Branch, Commit
                                 '%(github_public_repo_name)s/'
                                 'issues#issue/%%s',
    supports_post_commit = True
    supports_repositories = True
    supports_ssh_key_association = True
    # This should be the prefix for every field on the plan forms.
    plan_field_prefix = 'github'

    def get_api_url(self, hosting_url):
        """Returns the API URL for GitHub.

        This can be overridden to provide more advanced lookup (intended
        for the GitHub Enterprise support).
        """
        assert not hosting_url
        return 'https://api.github.com/'

    def get_plan_field(self, plan, plan_data, name):
        """Returns the value of a field for plan-specific data.

        This takes into account the plan type and hosting service ID.
        """
        key = '%s_%s_%s' % (self.plan_field_prefix, plan.replace('-', '_'),
                            name)
        return plan_data[key]

    def authorize(self, username, password, hosting_url,
                  local_site_name=None, *args, **kwargs):
            body = {
                'scopes': [
                    'user',
                    'repo',
                ],
                'note': 'Access for Review Board',
                'note_url': site_url,
            }

            # If the site is using a registered GitHub application,
            # send it in the requests. This will gain the benefits of
            # a GitHub application, such as higher rate limits.
            if (hasattr(settings, 'GITHUB_CLIENT_ID') and
                hasattr(settings, 'GITHUB_CLIENT_SECRET')):
                body.update({
                    'client_id': settings.GITHUB_CLIENT_ID,
                    'client_secret': settings.GITHUB_CLIENT_SECRET,
                })

                url=self.get_api_url(hosting_url) + 'authorizations',
                body=json.dumps(body))
                rsp = json.loads(data)
    def get_branches(self, repository):
        results = []

        url = self._build_api_url(repository, 'git/refs/heads')
        try:
            rsp = self._api_get(url)
        except Exception, e:
            logging.warning('Failed to fetch commits from %s: %s',
                            url, e)
            return results

        for ref in rsp:
            refname = ref['ref']

            if not refname.startswith('refs/heads/'):
                continue

            name = refname.split('/')[-1]
            results.append(Branch(name, ref['object']['sha'],
                                  default=(name == 'master')))

        return results

    def get_commits(self, repository, start=None):
        results = []

        resource = 'commits'
        url = self._build_api_url(repository, resource)
        if start:
            url += '&sha=%s' % start

        try:
            rsp = self._api_get(url)
        except Exception, e:
            logging.warning('Failed to fetch commits from %s: %s',
                            url, e)
            return results

        for item in rsp:
            commit = Commit(
                item['commit']['author']['name'],
                item['sha'],
                item['commit']['committer']['date'],
                item['commit']['message'])
            if item['parents']:
                commit.parent = item['parents'][0]['sha']

            results.append(commit)

        return results

    def get_change(self, repository, revision):
        # Step 1: fetch the commit itself that we want to review, to get
        # the parent SHA and the commit message. Hopefully this information
        # is still in cache so we don't have to fetch it again.
        commit = cache.get(repository.get_commit_cache_key(revision))
        if commit:
            author_name = commit.author_name
            date = commit.date
            parent_revision = commit.parent
            message = commit.message
        else:
            url = self._build_api_url(repository, 'commits')
            url += '&sha=%s' % revision

            commit = self._api_get(url)[0]

            author_name = commit['commit']['author']['name']
            date = commit['commit']['committer']['date'],
            parent_revision = commit['parents'][0]['sha']
            message = commit['commit']['message']

        # Step 2: fetch the "compare two commits" API to get the diff.
        url = self._build_api_url(
            repository, 'compare/%s...%s' % (parent_revision, revision))
        comparison = self._api_get(url)

        tree_sha = comparison['base_commit']['commit']['tree']['sha']
        files = comparison['files']

        # Step 3: fetch the tree for the original commit, so that we can get
        # full blob SHAs for each of the files in the diff.
        url = self._build_api_url(repository, 'git/trees/%s' % tree_sha)
        url += '&recursive=1'
        tree = self._api_get(url)

        file_shas = {}
        for file in tree['tree']:
            file_shas[file['path']] = file['sha']

        diff = []

        for file in files:
            filename = file['filename']
            status = file['status']
            patch = file['patch']

            diff.append('diff --git a/%s b/%s' % (filename, filename))

            if status == 'modified':
                old_sha = file_shas[filename]
                new_sha = file['sha']
                diff.append('index %s..%s 100644' % (old_sha, new_sha))
                diff.append('--- a/%s' % filename)
                diff.append('+++ b/%s' % filename)
            elif status == 'added':
                new_sha = file['sha']

                diff.append('new file mode 100644')
                diff.append('index %s..%s' % ('0' * 40, new_sha))
                diff.append('--- /dev/null')
                diff.append('+++ b/%s' % filename)
            elif status == 'removed':
                old_sha = file_shas[filename]

                diff.append('deleted file mode 100644')
                diff.append('index %s..%s' % (old_sha, '0' * 40))
                diff.append('--- a/%s' % filename)
                diff.append('+++ /dev/null')

            diff.append(patch)

        diff = '\n'.join(diff)

        # Make sure there's a trailing newline
        if not diff.endswith('\n'):
            diff += '\n'

        commit = Commit(author_name, revision, date, message, parent_revision)
        commit.diff = diff
        return commit

    def is_ssh_key_associated(self, repository, key):
        if not key:
            return False

        formatted_key = self._format_public_key(key)

        # The key might be a deploy key (associated with a repository) or a
        # user key (associated with the currently authorized user account),
        # so check both.
        deploy_keys_url = self._build_api_url(repository, 'keys')
        api_url = self.get_api_url(self.account.hosting_url)
        user_keys_url = ('%suser/keys?access_token=%s'
                         % (api_url,
                            self.account.data['authorization']['token']))

        for url in (deploy_keys_url, user_keys_url):
            keys_resp = self._key_association_api_call(self._json_get, url)

            keys = [
                item['key']
                for item in keys_resp
                if 'key' in item
            ]

            if formatted_key in keys:
                return True

        return False

    def associate_ssh_key(self, repository, key, *args, **kwargs):
        url = self._build_api_url(repository, 'keys')

        if key:
            post_data = {
                'key': self._format_public_key(key),
                'title': 'Review Board (%s)' %
                         Site.objects.get_current().domain,
            }

            self._key_association_api_call(self._http_post, url,
                                           content_type='application/json',
                                           body=json.dumps(post_data))

    def _key_association_api_call(self, instance_method, *args,
                                  **kwargs):
        """Returns response of API call, or raises SSHKeyAssociationError.

        The `instance_method` should be one of the HostingService http methods
        (e.g. _http_post, _http_get, etc.)
        """
        try:
            response, headers = instance_method(*args, **kwargs)
            return response
        except (urllib2.HTTPError, urllib2.URLError), e:
            try:
                rsp = json.loads(e.read())
                status_code = e.code
            except:
                rsp = None
                status_code = None

            if rsp and status_code:
                api_msg = self._get_api_error_message(rsp, status_code)
                raise SSHKeyAssociationError('%s (%s)' % (api_msg, e))
            else:
                raise SSHKeyAssociationError(str(e))

    def _format_public_key(self, key):
        """Return the server's SSH public key as a string (if it exists)

        The key is formatted for POSTing to GitHub's API.
        """
        # Key must be prepended with algorithm name
        return '%s %s' % (key.get_name(), key.get_base64())

    def _get_api_error_message(self, rsp, status_code):
        """Return the error(s) reported by the GitHub API, as a string

        See: http://developer.github.com/v3/#client-errors
        """
        if 'message' not in rsp:
            msg = _('Unknown GitHub API Error')
        elif 'errors' in rsp and status_code == httplib.UNPROCESSABLE_ENTITY:
            errors = [e['message'] for e in rsp['errors'] if 'message' in e]
            msg = '%s: (%s)' % (rsp['message'], ', '.join(errors))
        else:
            msg = rsp['message']

        return msg

        if plan in ('public', 'private'):
        elif plan in ('public-org', 'private-org'):
            owner = self.get_plan_field(plan, repository.extra_data, 'name')
        else:
            raise InvalidPlanError(plan)

        return '%srepos/%s/%s/' % (
            self.get_api_url(self.account.hosting_url),
            owner,
            self.get_plan_field(plan, repository.extra_data, 'repo_name'))

    def _api_get(self, url):
        try:
            data, headers = self._http_get(url)
            return json.loads(data)
        except (urllib2.URLError, urllib2.HTTPError), e:
            data = e.read()

            try:
                rsp = json.loads(data)
            except:
                rsp = None

            if rsp and 'message' in rsp:
                raise Exception(rsp['message'])
            else:
                raise Exception(str(e))