#!/usr/bin/env python

import gentoopm
import pickle
import sys


def main():
    pm = gentoopm.get_package_manager()
    maints = {}

    for p in pm.repositories['gentoo']:
        # include only explicitly proxied by g-p-m
        for m in p.maintainers:
            if m.email == 'proxy-maint@gentoo.org':
                break
        else:
            for m in p.maintainers:
                if m.email.endswith('@gentoo.org'):
                    break
            else:
                if p.maintainers:
                    print('Proxied maintainer without a proxy?! pkg %s, %s'
                          % (p, p.maintainers),
                          file=sys.stderr)
            continue

        for m in p.maintainers:
            # skip gentoo devs & projects
            if m.email.endswith('@gentoo.org'):
                continue
            maints[m.email.lower()] = m.name

    pickle.dump(maints, sys.stdout.buffer)


if __name__ == '__main__':
    main()
