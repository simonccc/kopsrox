#!/usr/bin/env python3

# functions
from kopsrox_config import vmnames,cluster_info, cluster_id, vms, vmip, cloudinituser
from kopsrox_k3s import k3s_remove_node
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
if cmd in ['terminal', 'ssh', 'destroy', 'reboot', 'k3s-uninstall']:

  # for each vmid in list of vms generated in kopsrox_config
  for vmid in vms:

    # if passed arg matches vmname
    if arg == vmnames[vmid]:
      kmsg(kname, arg, 'sys')

      # terminal 
      if cmd == 'terminal':
        os.system(f'sudo qm terminal {vmid}')
        exit(0)

      # ssh command
      if cmd == 'ssh':
        os.system(f'ssh -l {cloudinituser} {vmip(vmid)} -o StrictHostKeyChecking=no ')
        exit(0)

      # destroy vm
      if cmd == 'destroy':
        k3s_remove_node(vmid)
        exit(0)

      # reboot
      if cmd == 'reboot':
        os.system(f'sudo qm reboot {vmid} &')
        exit(0)

      # k3s uninstall
      if cmd == 'k3s-uninstall':
        os.system(f'sudo qm guest exec {vmid} /usr/local/bin/k3s-uninstall.sh')
        exit(0)

  # vm not found 
  kmsg(kname, f'{arg} vm not found', 'err')

# create utility node
if cmd == 'utility':

  # define id of utility server
  utility_vm_id = cluster_id + 4 

  # check to see if already exists
  if utility_vm_id not in vms:
    kmsg(kname, 'creating utility node', 'sys')
    clone(utility_vm_id)
  else:
    kmsg(kname, 'utility node already exists')
  cluster_info()
