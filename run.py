#!/usr/bin/python2.7

import models as mod
import os

def _help():
    print 'run.py {-s topo.yaml|-d}'
    print '-s for setup, -d for destroy'
    os.sys.exit(1)

if os.getuid() != 0:
    print 'Need run as root.'
    os.sys.exit(1)

argv = os.sys.argv
method = argv[1] if len(argv) > 1 else ''
method = {'-s': 'setup', '-d': 'destroy'}.get(method)
if not method:
    _help()

if method == 'destroy':
    topo_yaml = open(mod.LOCK).read().strip()
elif len(argv) > 2 and method == 'setup':
    topo_yaml = argv[2]
else:
    print 'Need a topology yaml file.'
    os.sys.exit(1)

if not os.path.exists(topo_yaml):
    print 'Topology yaml file not exists.'
    os.sys.exit(1)

if os.path.exists(mod.LOCK) and method == 'setup':
    print (
        "It's in topology %(topo)s, no more topo can get setup before "
        "destroy %(topo)s\nOr, you can remove lock file %(lock)s, if "
        "you confirm there is no topo yet" % {
            'topo': open(mod.LOCK).read(), 'lock': mod.LOCK})
    os.sys.exit(1)
elif not os.path.exists(mod.LOCK) and method == 'destroy':
    print 'No topo currently, nothing to destroy'
    os.sys.exit(0)

mod.setup_or_destroy(topo_yaml, method)
