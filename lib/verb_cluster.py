#!/usr/bin/env python3

# functions
from kopsrox_config import *
from kopsrox_k3s import * 

# passed command
cmd = sys.argv[2]

# define kname
kname = 'cluster_'+cmd

# info
if cmd == 'info':
 cluster_info()

# update current cluster
if cmd == 'update':
  k3s_update_cluster()

# restore from latest etcd snapshot
if cmd == 'restore':
  k3s_rm_cluster()
  kmsg(kname,f'id:{cluster_id} name:{cluster_name}', 'sys')
  clone(masterid)
  k3s_init_node(masterid, 'restore')
  cluster_info()
  kmsg(kname,f'restore completed')
  k3s_update_cluster()

# create new cluster / master server
if cmd == 'create':

  # if masterid not found running 
  if not masterid in list_kopsrox_vm():
    kmsg(kname,f'creating {cluster_name} id {cluster_id} network {network_ip}', 'sys')
    clone(masterid)

  # install k3s on master
  k3s_init_node()

  # perform rest of cluster creation
  k3s_update_cluster()


# destroy the cluster
if cmd == 'destroy':
  kmsg(kname, f'{cluster_name}', 'err')
  k3s_rm_cluster()
