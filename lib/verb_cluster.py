#!/usr/bin/env python3

# common include file - review
import kopsrox_config as kopsrox_config

# functions
from kopsrox_config import masterid,cname
from kopsrox_config import kmsg_info, kmsg_warn, cluster_info, kmsg_sys, list_kopsrox_vm, kmsg_err

from kopsrox_proxmox import clone
from kopsrox_k3s import k3s_update_cluster, kubeconfig, kubectl, k3s_init_master, k3s_rm_cluster

# other imports
import sys, re

# passed command
cmd = sys.argv[2]

# define kname
kname = ('cluster-'+cmd)

# cluster info is a function that prints its own header
if not cmd == 'info':
  kmsg_sys(kname,'')

# info
if cmd == 'info':
 cluster_info()

# update current cluster
if cmd == 'update':
  k3s_update_cluster()

# create new cluster / master server
if cmd == 'create':

  # if masterid not found running 
  if not masterid in list_kopsrox_vm():
    clone(masterid)

  # check master status
  try:
    init = k3s_init_master(masterid)
  except:
    kmsg_err(kname, 'problem installing master')
    print(init)
    exit()

  # perform rest of cluster creation
  kmsg_info(('cluster-'+cname),'ready')
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
  print(kname + kcmd)
  print(kubectl(kcmd))

# export kubeconfig to file
if cmd == 'kubeconfig':
  kubeconfig(masterid)

# destroy the cluster
if cmd == 'destroy':
  k3s_rm_cluster()
