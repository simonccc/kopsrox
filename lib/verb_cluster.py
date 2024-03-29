#!/usr/bin/env python3

# functions
from kopsrox_config import masterid,cname,kmsg_info,kmsg_warn,cluster_info,kmsg_sys,list_kopsrox_vm,kmsg_err
from kopsrox_proxmox import clone,internet_check
from kopsrox_k3s import k3s_update_cluster,kubeconfig,kubectl,k3s_rm_cluster,k3s_init_node

# other imports
import sys, re

# passed command
cmd = sys.argv[2]

# define kname
kname = 'cluster-'+cmd

# info
if cmd == 'info':
 cluster_info()

# update current cluster
if cmd == 'update':
  internet_check(masterid)
  k3s_update_cluster()

# create new cluster / master server
if cmd == 'create':
  kmsg_sys(kname,'')

  # if masterid not found running 
  if not masterid in list_kopsrox_vm():
    clone(masterid)

  # install k3s on master
  k3s_init_node()

  # perform rest of cluster creation
  k3s_update_cluster()

# kubectl
if cmd == 'kubectl':
 
  # init kcmd
  kcmd= ''  

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
  kmsg_sys('kubectl', kcmd)
  print(kubectl(kcmd))

# export kubeconfig to file
if cmd == 'kubeconfig':
  kubeconfig()

# destroy the cluster
if cmd == 'destroy':
  k3s_rm_cluster()
