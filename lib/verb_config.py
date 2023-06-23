#!/usr/bin/env python3
import sys, os
import common_config as common
import kopsrox_ini as ini

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

# dump ini to example.ini
if passed_verb == 'example.ini':
  print('config::example.ini: generating')
  try:
    os.remove('example.ini')
  except:
    next
  ini.init_kopsrox_ini(conf = 'example.ini')
