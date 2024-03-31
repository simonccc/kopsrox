#!/usr/bin/env python3

# functions
from kopsrox_config import vmnames
from kopsrox_k3s import k3s_rm

# other imports
import sys,re

# passed command
cmd = sys.argv[2]
arg = sys.argv[3]

# define kname
kname = 'node-'+cmd

# destroy
if cmd == 'destroy':

  # get list of valid hosts and ids and check for this hostname
  for vmid, hostname in vmnames.items():
    if hostname == arg:
      k3s_rm(vmid)
      exit(0)
  print('info')
