#!/usr/bin/env python

from collections import defaultdict
import gentoopm
import pickle
import sys


extra_maints = defaultdict(list)


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
                if not m.email.endswith('@gentoo.org'):
                    extra_maints[m.email].append(p)
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
    for maint, data in sorted(extra_maints.items()):
        other_maints = defaultdict(set)
        for p in data:
            other_maints[tuple(sorted(x.email for x in p.maintainers if x.email.endswith('@gentoo.org')))].add(p.key)

        print('%s' % maint)
        for om, pkgs in sorted(other_maints.items()):
            print('\t%s' % (' '.join(om) or '(none)'))
            for p in sorted(pkgs):
                print('\t\t%s' % p)
        print()


if __name__ == '__main__':
    main()
