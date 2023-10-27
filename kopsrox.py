#!/usr/bin/env python3

import os, sys

# use lib dir
sys.path[0:0] = ['lib/']

# check file exists
if not os.path.isfile('kopsrox.ini'):
  import kopsrox_ini as kopsrox_ini
  kopsrox_ini.init_kopsrox_ini()
  exit(0)

verbs = ['image', 'cluster', 'etcd']
verbs_image = ['info', 'create', 'destroy']
verbs_cluster = ['info', 'create', 'update', 'destroy', 'kubectl', 'kubeconfig']
verbs_etcd = ['snapshot', 'restore', 'list', 'prune']

def verbs_help(verbs):
  print('commands:', '\n')
  for i in verbs:
    print(' * ',i)

try:
  if (sys.argv[1]):
    passed_verb = str(sys.argv[1])
except:
  print('ERROR: no command passed')
  print('kopsrox ', end='')
  verbs_help(verbs)
  exit(0)

if passed_verb in verbs:
  verb = __import__('verb_' + passed_verb)
  exit(0)

# if passed arg invalid
print('ERROR: \'' + passed_verb + '\' command not found.')
print('kopsrox ', end='')
verbs_help(verbs)

# checks config
import kopsrox_config as kopsrox_config
