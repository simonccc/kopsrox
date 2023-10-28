#!/usr/bin/env python3

# common include file
import kopsrox_config as kopsrox_config

# remove
import common_config as common

# other imports
import sys, os, re, time
import kopsrox_proxmox as proxmox
import kopsrox_k3s as k3s

# passed command
cmd = sys.argv[2]

# variables from config
proxnode = kopsrox_config.proxnode
proximgid = kopsrox_config.proximgid
workers = int(kopsrox_config.workers)
masters = int(kopsrox_config.masters)

# masterid
masterid = int(kopsrox_config.get_master_id())

# define kname
kname = 'kopsrox::cluster::'

# info
if cmd == 'info':
  print(kname + cmd)

  # map dict of ids and node
  vms = proxmox.list_kopsrox_vm()

  # for kopsrox vms
  for vmid in vms:

    # get vm status
    node = vms[vmid]
    vm_info = proxmox.vm_info(vmid,node)

    # vars
    vmname = vm_info.get('name')
    vmstatus = vm_info.get('status')
    ip = kopsrox_config.vmip(vmid)

    # print
    print(vmid, '-', vmname, "status:", vmstatus, 'ip:', ip + ' [' + node + ']')

  print(kname +'nodes')
  print(common.kubectl(masterid, 'get nodes'))

# update current cluster
if ( cmd == 'update' ):
  print(kname + cmd)
  k3s.k3s_update_cluster()

# create new cluster
if ( cmd == 'create' ):
  print(kname + cmd)

  # get list of runnning vms
  vmids = proxmox.list_kopsrox_vm()

  # clone new master
  if not (masterid in vmids):
    proxmox.clone(masterid)

  # map hostname
  vmname = common.vmname(masterid)

  # if init worked ok
  if not k3s.k3s_init_master(masterid):
    print('cluster::create: ERROR: master not installed')
    exit(0)

  # export kubeconfig
  common.kubeconfig(masterid)

  # perform rest of cluster creation
  k3s.k3s_update_cluster()

  # done
  print('cluster::create:'+ vmname + ' ok')

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
  print('cluster::kubectl:', kcmd)
  print(common.kubectl(masterid,kcmd))

# export kubeconfig to file
if cmd == 'kubeconfig':
  common.kubeconfig(masterid)

# destroy the cluster
if cmd == 'destroy':
  k3s.k3s_rm_cluster()
