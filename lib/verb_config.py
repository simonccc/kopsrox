#!/usr/bin/env python3
import common_config as common, sys, re, time
#import kopsrox_proxmox as proxmox
#import kopsrox_k3s as k3s

# verb info
verb = 'config'
verbs = common.verbs_config

# check for arguments
try:
  if (sys.argv[2]):
    passed_verb = str(sys.argv[2])
except:
  print('ERROR: pass a command')
  print(verb, '', end='')
  common.verbs_help(verbs)
  exit(0)

# unsupported verb
if not passed_verb in verbs:
  print('ERROR:\''+ passed_verb + '\'- command not found')
  print('kopsrox', verb, '', end='')
  common.verbs_help(verbs)
  exit(0)
