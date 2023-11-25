#!/usr/bin/env python3

import os, sys
sys.path[0:0] = ['lib/']

from termcolor import cprint

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

def kmsg(msg):
  cprint('kopsrox', "blue",attrs=["bold"], end='')
  cprint('::', "cyan", end='' )
  print(msg)

# print list of verbs
def verbs_help():
  kmsg('kopsrox [verb] [command]')
  cprint('verbs:', "yellow", attrs=["bold"])
  for i in verbs:
    print(' * ',i)

# print verbs cmds
def cmds_help(verb):
  kmsg(verb+' [command]')
  print('commands:')
  for i in list(cmds[verb]):
    print(' * ',i)

# handle verb
try:

  # check for 1st argument
  if (sys.argv[1]):

    # map 1st arg to verb
    verb = str(sys.argv[1])

    # if verb not found in cmds dict
    if not verb in verbs:
      exit(0)
except:
  verbs_help()
  exit(0)

# handle command
try:
  if (sys.argv[2]):
    cmd = str(sys.argv[2])
    if not cmd in list(cmds[verb]):
      exit(0)
except:
  cmds_help(verb)
  exit(0)

# run passed verb
exec_verb = __import__('verb_' + verb)
