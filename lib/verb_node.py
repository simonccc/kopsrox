#!/usr/bin/env python3

# functions
from kopsrox_config import vmnames,cluster_info, kmsg_err, kmsg_sys
from kopsrox_k3s import k3s_rm

# other imports
import sys

# passed command
cmd = sys.argv[2]
arg = sys.argv[3]

# define kname
kname = 'node-'+cmd

# destroy
if cmd == 'destroy':

  # get list of valid hosts and ids and check for this hostname
  for vmid, hostname in vmnames.items():
    # if hostname match
    if hostname == arg:
      kmsg_sys(kname, arg)
      k3s_rm(vmid)
      exit(0)

  # passed hostname not found 
  kmsg_err(kname, (arg+ ' vm not found'))
  cluster_info()
