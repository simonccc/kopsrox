#!/usr/bin/env python3

# functions
from kopsrox_config import vmnames,cluster_info, cluster_id, vms
from kopsrox_k3s import k3s_rm
from kopsrox_proxmox import clone
from kopsrox_kmsg import kmsg

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
kname = 'node_'+cmd

# terminal + destroy
if cmd == 'terminal' or cmd == 'destroy':
  kmsg(kname, arg, 'sys')
  for vmid in vms:
    if arg == vmnames[vmid]:

      # terminal 
      if cmd == 'terminal':
        os.system(f'sudo qm terminal {vmid}')
        exit(0)

      # destroy
      if cmd == 'destroy':
        k3s_rm(vmid)
        exit(0)

  # vm not found 
  kmsg(kname, f'{arg} vm not found', 'err')

# create utility node
if cmd == 'utility':

  # define id of utility server
  utility_vm_id = cluster_id + 4 

  # check to see if already exists
  if utility_vm_id not in vms():
    kmsg(kname, 'creating utility node', 'sys')
    clone(utility_vm_id)
  else:
    kmsg(kname, 'utility node already exists')
  cluster_info()
