#!/usr/bin/env python3

import os, sys

# use lib dir
sys.path[0:0] = ['lib/']

# check file exists
if not os.path.isfile('kopsrox.ini'):
  import kopsrox_ini as kopsrox_ini
  kopsrox_ini.init_kopsrox_ini()
  exit(0)

# kopsrox verbs and commands
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

# create list of verbs
verbs = list(cmds)

# print list of verbs
def verbs_help():
  for i in verbs:
    print(' * ',i)

# print verbs cmds
def cmds_help(verb):
  for i in list(cmds[verb]):
    print(' * ',i)

# handle verb
try:
  if (sys.argv[1]):
    verb = str(sys.argv[1])
except:
  verbs_help()
  exit(0)

# define kname
kname = 'kopsrox::'+verb+'::'

# got a verb now commands
if verb in verbs:

  try:
    if (sys.argv[2]):
      cmd = str(sys.argv[2])
  except:
    print(kname+'ERROR! pass a command')
    cmds_help(verb)
    exit(0)

  # unsupported verb
  if not cmd in list(cmds[verb]):
    print(kname+'ERROR! command \''+ cmd + '\' not found')
    cmds_help(verb)
    exit(0)

  # run passed verb
  exec_verb = __import__('verb_' + verb)
  exit(0)

# if passed arg invalid
verbs_help()
