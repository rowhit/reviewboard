from django.utils import simplejson
                                 '%(github_public_repo_name)s/issues#issue/%%s',
    supports_bug_trackers = True
                body=simplejson.dumps(body))
                rsp = simplejson.loads(data)
            return simplejson.loads(data)
                rsp = simplejson.loads(data)