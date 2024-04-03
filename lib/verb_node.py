#!/usr/bin/env python3

# functions
from kopsrox_config import vmnames,cluster_info, kmsg_err, kmsg_sys, cluster_id, list_kopsrox_vm, kmsg_info, list_kopsrox_vm
from kopsrox_k3s import k3s_rm
from kopsrox_proxmox import clone

# other imports
import sys,os

# passed command
cmd = sys.argv[2]

# map arg if passed
try:
  arg = sys.argv[3]
except:
  pass

# define kname
kname = 'node-'+cmd

# terminal + destroy
if cmd == 'terminal' or cmd == 'destroy':
  kmsg_sys(kname, arg)
  for vmid in list_kopsrox_vm():
    if arg == vmnames[vmid]:
      if cmd == 'terminal':
        os.system(f'sudo qm terminal {vmid}')
        exit(0)
      if cmd == 'destroy':
        k3s_rm(vmid)
        exit(0)
  kmsg_err(kname, f'{arg} vm not found')

# create utility node
if cmd == 'utility':
  uid = cluster_id + 4 
  if uid not in list_kopsrox_vm():
    kmsg_sys(kname, 'creating utility node')
    clone(uid)
  else:
    kmsg_info(kname, 'utility node already exists')
  cluster_info()
