#!/usr/bin/env python3

# standard imports
import os, sys
sys.path[0:0] = ['lib/']

# kopsrox
from kopsrox_ini import init_kopsrox_ini
from kopsrox_kmsg import kmsg

# check file exists
if not os.path.isfile('kopsrox.ini'):
  init_kopsrox_ini()
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
    "kubectl" : 'cmd',
    "kubeconfig" : '',
    "k3stoken" : '',
  },
  "etcd": {
    "snapshot" : '',
    "restore" : 'snapshot',
    "restore-latest" : '',
    "list" : '',
    "prune" : '',
  },
  "node": {
    "destroy" : 'hostname',
    "utility" : '',
    "terminal" : 'hostname',
  },
}

# create list of verbs
verbs = list(cmds)

# print list of verbs
def verbs_help():
  kmsg('kopsrox_usage', '[verb] [command]')
  print('verbs:')
  for i in verbs:
    print(' * ',i)

# print verbs cmds
def cmds_help(verb):
  kmsg(f'kopsrox_{verb}', '[command]')
  print('commands:')
  for i in list(cmds[verb]):
    print(' * ',i)

# handle verb
try:

  # check for 1st argument
  if sys.argv[1]:

    # map 1st arg to verb
    verb = sys.argv[1]

    # if verb not found in cmds dict
    if not verb in verbs:
      exit()
except:
  verbs_help()
  exit()

# handle command
try:

  # 2nd arg
  if sys.argv[2]:

    # map 2nd arg to cmd
    cmd = sys.argv[2]

    # if cmd not in list of commands
    if not cmd in list(cmds[verb]):
      exit()

except:
  cmds_help(verb)
  exit()

# handle args
try:
  if cmds[verb][cmd] and sys.argv[3]:
    pass
except:
  kmsg(f'kopsrox {verb} {cmd} [{cmds[verb][cmd]}]')
  exit(0)

# run passed verb
exec_verb = __import__('verb_' + verb)
