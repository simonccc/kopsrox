#!/usr/bin/env python3

# functions
from kopsrox_config import masterid,cluster_name,cluster_info,list_kopsrox_vm,cluster_id
from kopsrox_proxmox import clone,internet_check,qaexec
from kopsrox_k3s import k3s_update_cluster,k3s_rm_cluster,k3s_init_node,export_k3s_token
from kopsrox_kmsg import kmsg

# other imports
import sys

# passed command
cmd = sys.argv[2]

# define kname
kname = 'cluster_'+cmd

# info
if cmd == 'info':
 cluster_info()

# update current cluster
if cmd == 'update':
  internet_check(masterid)
  k3s_update_cluster()

# create new cluster / master server
if cmd == 'create':

  # if masterid not found running 
  if not masterid in list_kopsrox_vm():
    kmsg(kname,f'creating {cluster_name} cluster id {cluster_id}', 'sys')
    clone(masterid)

  # install k3s on master
  k3s_init_node()

  # perform rest of cluster creation
  k3s_update_cluster()

# destroy the cluster
if cmd == 'destroy':
  kmsg(kname, f'!! destroying {cluster_name} !!', 'sys')
  k3s_rm_cluster()
