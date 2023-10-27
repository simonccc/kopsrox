#!/usr/bin/env python3

import os, sys

# use lib dir
sys.path[0:0] = ['lib/']

# check file exists
if not os.path.isfile('kopsrox.ini'):
  import kopsrox_ini as kopsrox_ini
  kopsrox_ini.init_kopsrox_ini()
  exit(0)

# top level verbs
verbs = ['image', 'cluster', 'etcd']
verbs_image = ['info', 'create', 'destroy']
verbs_cluster = ['info', 'create', 'update', 'destroy', 'kubectl', 'kubeconfig']
verbs_etcd = ['snapshot', 'restore', 'list', 'prune']

cmds = {
    "image": {
        "info" : '',
        "create" : '',
        "destroy": '',
    },
    "cluster": {
        "info" : '',
        "create" : '',
        "update" : '',
        "destroy" : '',
        "kubectl" : '',
        "kubeconfig" : '',
    },
    "etcd": {
        "snapshot" : '',
        "restore" : '',
        "list" : '',
        "prune" : '',
    },
}

def verbs_help(verbs):
  print('commands:', '\n')
  for i in verbs:
    print(' * ',i)

def cmds_help(verb):
  for i in list(cmds[verb]):
    print(i)

try:
  if (sys.argv[1]):
    passed_verb = str(sys.argv[1])
except:
  print('ERROR: no command passed')
  print('kopsrox ', end='')
  verbs_help(verbs)
  exit(0)

kname = 'koprox::'+passed_verb

# got a verb now commands
if passed_verb in verbs:

  try:
    if (sys.argv[2]):
      cmd = str(sys.argv[2])
  except:
    print(kname, 'ERROR: pass a command')
    cmds_help(passed_verb)
    exit(0)

  # unsupported verb
  if not cmd in list(cmds[passed_verb]):
    print(kname, 'ERROR:\''+ cmd + '\'- command not found')
    cmds_help(passed_verb)

  verb = __import__('verb_' + passed_verb)
  exit(0)

# if passed arg invalid
print('ERROR: \'' + passed_verb + '\' command not found.')
print('kopsrox ', end='')
verbs_help(verbs)

# checks config
#import kopsrox_config as kopsrox_config
