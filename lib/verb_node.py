#!/usr/bin/env python3

# functions
from kopsrox_config import vmnames,cluster_info, kmsg_err, kmsg_sys, cluster_id, list_kopsrox_vm, kmsg_info
from kopsrox_k3s import k3s_rm
from kopsrox_proxmox import clone

# other imports
import sys

# passed command
cmd = sys.argv[2]

# map arg if passed
try:
  arg = sys.argv[3]
except:
  pass

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

# create utility node
if cmd == 'utility':
  uid = cluster_id + 4 
  if uid not in list_kopsrox_vm():
    kmsg_sys(kname, 'creating utility node')
    clone(uid)
  else:
    kmsg_info(kname, 'utility node already exists')
  cluster_info()
