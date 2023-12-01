#!/usr/bin/env python3

# common include file
import kopsrox_config as kopsrox_config
from kopsrox_config import masterid,cname
from kopsrox_config import kmsg_info, kmsg_warn, cluster_info

# other imports
import sys, os, re, time
import kopsrox_proxmox as proxmox
import kopsrox_k3s as k3s

# passed command
cmd = sys.argv[2]

# define kname
kname = ('cluster-'+cmd)

# info
if cmd == 'info':
 kmsg_info(kname, '')
 cluster_info()

# update current cluster
if cmd == 'update':
  k3s.k3s_update_cluster()

# create new cluster / master server
if cmd == 'create':
  kmsg_info(kname, ('creating '+ cname))

  # get list of runnning vms
  vmids = kopsrox_config.list_kopsrox_vm()

  # clone new master
  if not (masterid in vmids):
    proxmox.clone(masterid)

  # if init worked ok
  try:
    k3s.k3s_init_master(masterid)
  except:
    print(kname + 'ERROR: master not installed')
    exit(0)

  # export kubeconfig
  k3s.kubeconfig(masterid)

  # perform rest of cluster creation
  k3s.k3s_update_cluster()

# kubectl
if cmd == 'kubectl':

  # convert command line into string
  kcmd= '';  

  # convert command line into string
  for arg in sys.argv[1:]:          
    if ' ' in arg:
      # Put the quotes back in
      kcmd+='"{}" '.format(arg) ;  
    else:
      # Assume no space => no quotes
      kcmd+="{} ".format(arg) ;   

  # remove first 2 commands
  kcmd = kcmd.replace('cluster kubectl ','')

  # run command and show output
  print(kname + kcmd)
  print(k3s.kubectl(kcmd))

# export kubeconfig to file
if cmd == 'kubeconfig':
  k3s.kubeconfig(masterid)

# destroy the cluster
if cmd == 'destroy':
  kmsg_warn(kname, ('destroying '+cname))
  k3s.k3s_rm_cluster()
