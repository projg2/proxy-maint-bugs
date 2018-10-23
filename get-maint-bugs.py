#!/usr/bin/env python

import bugzilla
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
        print('Put bugzilla API key into ~/.bugz_token')
        return 1

    with open(maint_fn, 'rb') as f:
        maints = pickle.load(f)

    bz = bugzilla.Bugzilla('https://bugs.gentoo.org', api_key=token)
    q = bz.build_query(
        product='Gentoo Developers/Staff',
        component='Proxied maintainers')
    bugs = bz.query(q)

    found = set()
    for b in bugs:
        assignee = b.assigned_to.lower()
        if assignee in maints:
            found.add(assignee)
            if b.status == 'RESOLVED':
                print('Needs reopening: https://bugs.gentoo.org/%s' % b.id)
        else:
            if b.status != 'RESOLVED':
                print('Unmatched bug: https://bugs.gentoo.org/%s' % b.id)

    failed = set()
    for email, name in maints.items():
        if email in found:
            continue

        formatted_name = '%s AT %s' % tuple(email.split('@', 1))
        if name is not None:
            formatted_name = '%s (%s)' % (name, formatted_name)

        q = bz.build_createbug(
            product='Gentoo Developers/Staff',
            component='Proxied maintainers',
            version='unspecified',
            assigned_to=email,
            cc='proxy-maint@gentoo.org',
            summary='Maintainer: %s' % formatted_name,
            description=DESCRIPTION)

        try:
            ret = bz.createbug(q)
        except Exception as e:
            print(e)
            failed.add(email)
        else:
            print('Filed bug #%d' % ret.id)


    if failed:
        print('Failed addresses')
        print('================')
        print()
        for m in sorted(failed):
            print(m)


if __name__ == '__main__':
    main(*sys.argv[1:])
