#!/usr/bin/env python

import bugz.bugzilla
import gentoopm
import os.path
import pickle
import sys

DESCRIPTION = '''
This is a proxied maintainer bug.

Please keep this bug open and assigned to you as long as you maintain at least
one package in Gentoo. Please use this bug to communicate:

- e-mail address changes,
- extended periods of unavailability,
- possible resignation from proxied maintainer status,
- and any other events related to your maintainer status.

Please make sure to read the bug mail from the bug tracker and reply to
requests as soon as possible.
'''.strip()


def main(maint_fn):
    token_file = os.path.expanduser('~/.bugz_token')
    try:
        with open(token_file, 'r') as f:
            token = f.read().strip()
    except IOError:
        print('! Bugz token not found, please run "bugz login" first')
        return 1

    with open(maint_fn, 'rb') as f:
        maints = pickle.load(f)

    bz = bugz.bugzilla.BugzillaProxy('https://bugs.gentoo.org/xmlrpc.cgi')
    res = bz.Bug.search({
        'Bugzilla_token': token,
        'product': 'Gentoo Developers/Staff',
        'component': 'Proxied maintainers',
    })

    found = set()
    for b in res['bugs']:
        assignee = b['assigned_to'].lower()
        if assignee in maints:
            found.add(assignee)
        else:
            print('Unmatched bug: https://bugs.gentoo.org/%s' % b['id'])

    failed = set()
    for email, name in maints.items():
        if email in found:
            continue

        formatted_name = '%s AT %s' % tuple(email.split('@', 1))
        if name is not None:
            formatted_name = '%s (%s)' % (name, formatted_name)

        new_bug = {
            'Bugzilla_token': token,
            'product': 'Gentoo Developers/Staff',
            'component': 'Proxied maintainers',
            'version': 'All',
            'assigned_to': email,
            'cc': 'proxy-maint@gentoo.org',
            'summary': 'Maintainer: %s' % formatted_name,
            'description': DESCRIPTION,
        }

        try:
            ret = bz.Bug.create(new_bug)
        except Exception as e:
            print(e)
            failed.add(email)
        else:
            print('Filed bug #%d' % ret['id'])


    if failed:
        print('Failed addresses')
        print('================')
        print()
        for m in sorted(failed):
            print(m)


if __name__ == '__main__':
    main(*sys.argv[1:])
