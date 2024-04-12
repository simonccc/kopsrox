#!/usr/bin/env python3

# functions
from kopsrox_config import masterid,cluster_name,cluster_info,list_kopsrox_vm,cluster_id
from kopsrox_proxmox import clone,internet_check,qaexec
from kopsrox_k3s import k3s_update_cluster,kubeconfig,kubectl,k3s_rm_cluster,k3s_init_node,export_k3s_token
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
    kmsg(kname,f'{cluster_name}/{cluster_id}', 'sys')
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
  kmsg('kubectl_cmd', kcmd, 'sys')
  print(kubectl(kcmd))

# export kubeconfig to file
if cmd == 'kubeconfig':
  kubeconfig()

# destroy the cluster
if cmd == 'destroy':
  kmsg(kname, f'!! destroying {cluster_name} !!', 'sys')
  k3s_rm_cluster()

# write k3s token to file
if cmd == 'k3stoken':
  export_k3s_token()
