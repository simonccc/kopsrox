#!/usr/bin/env python3 

# imports
from kopsrox_config import masterid, k3s_version, masters, workers, cluster_name, vmnames, vmip, cluster_info, list_kopsrox_vm

# standard imports
from kopsrox_proxmox import qaexec, destroy, internet_check, clone
from kopsrox_kmsg import kmsg

# standard imports
import re, time

# check for k3s status
def k3s_check(vmid):

  vmid = int(vmid)
    
  # check k3s installed
  if 'nok3sbin' == qaexec(vmid, 'if [ ! -e /usr/local/bin/k3s ] ; then echo nok3sbin; fi'):
    exit()

  # test call
  get_node = kubectl('get node ' + vmnames[vmid])

  # if not found or Ready
  if re.search('NotReady', get_node) or re.search('NotFound', get_node):
    return False

  # return true if Ready
  if re.search('Ready', get_node):
    return True

  # failsafe
  return False

# wait for node
def k3s_check_mon(vmid):

  # how long to wait for
  wait = int(30)

  # check count
  count = int(0)

  # run k3s_check
  while not k3s_check(vmid):

    # counter + sleep
    count += 1
    time.sleep(1)

    # timeout after 30 secs
    if count == wait:
      kmsg('k3s_check-mon', f'timed out after {wait}s for {vmnames[vmid]}', 'err')
      exit(0)

  return True

# create a master/slave/worker
def k3s_init_node(vmid = masterid,nodetype = 'master'):

  k3s_install_base = f'cat /k3s.sh | INSTALL_K3S_VERSION="{k3s_version}"'
  k3s_install_flags = ' --disable servicelb'
  k3s_install_master = f'{k3s_install_base} sh -s - server --cluster-init {k3s_install_flags}'
  k3s_install_worker = f'{k3s_install_base} K3S_URL="https://{vmip(masterid)}:6443" '
  
  # nodetype error check
  if nodetype not in ['master', 'slave', 'worker']:
    kmsg('k3s_init-node', f'{nodetype} invalid nodetye', 'err')
    exit()
 
  # check status of node
  try:
    k3s_check(vmid)
  except:
    kmsg(f'k3s_{nodetype}-init', vmnames[vmid])

    # check vm has internet
    internet_check(vmid)

    # master
    if nodetype == 'master':
      init_cmd = k3s_install_master

    # get k3s token
    token = qaexec(masterid, 'cat /var/lib/rancher/k3s/server/node-token')
    k3s_token_cmd = f' K3S_TOKEN="{token}"'

    # slave
    if nodetype == 'slave':
      init_cmd = f'{k3s_install_base}{k3s_token_cmd} sh -s - server --server https://{vmip(masterid)}:6443 {k3s_install_flags}'

    # worker
    if nodetype == 'worker':
      init_cmd = f'{k3s_install_worker}{k3s_token_cmd} sh -s'

    # run command
    print(init_cmd)
    init_cmd_out = qaexec(vmid,init_cmd)

    # wait until ready
    try:
      k3s_check_mon(vmid)
    except:
      kmsg(f'k3s_{nodetype}-init', f'{vmnames[vmid]} {init_cmd_out}', 'err')
      exit()

    # export kubeconfig 
    if nodetype == 'master':
      kubeconfig()

# remove a node
def k3s_remove_node(vmid):
  vmname = vmnames[vmid]
  kmsg('k3s_remove-node', vmname)

  # kubectl commands to remove node
  # should add some error checking
  kubectl('cordon ' + vmname)
  kubectl('drain --timeout=5s --ignore-daemonsets --force ' + vmname)
  kubectl('delete node ' + vmname)

  # destroy vm
  destroy(vmid)

# remove cluster - leave master if restore = true
def k3s_rm_cluster(restore = False):

  # list all kopsrox vm id's
  for vmid in sorted(list_kopsrox_vm(), reverse = True):

    # map hostname
    vmname = vmnames[vmid]

    # do not delete m1 if restore is true 
    if restore and vmname == f'{cluster_name}-m1':
      continue

    # do not delete image or utility node
    if vmname == f'{cluster_name}-i0' or vmname == f'{cluster_name}-u1':
      continue

    # remove node from cluster and proxmox
    #print(vmname)
    if vmname == f'{cluster_name}-m1':
      destroy(vmid)
    else:
      k3s_remove_node(vmid)

# builds or removes other nodes from the cluster as required per config
def k3s_update_cluster():
 kmsg('k3s_update-cluster', f'checking: {masters} masters {workers} workers', 'sys')

 # get list of running vms
 vmids = list_kopsrox_vm()

 # do we need to run any more masters
 if ( masters > 1 ):
  master_count = int(1)

  while ( master_count <=  2 ):

    # so eg 601 + 1 = 602 = m2
    slave_masterid = int(masterid) + master_count
    slave_hostname = vmnames[slave_masterid]
    kmsg('k3s_slave-check', slave_hostname)

    # existing server
    if slave_masterid not in vmids:
      clone(slave_masterid)

    # install k3s on slave and join master
    k3s_init_node(slave_masterid,'slave')

    # next possible master ( m3 ) 
    master_count = master_count + 1

 # check for extra masters
 if masters == 1:
   for vm in vmids:
     # is this required?
     vm = int(vm)

     # if vm is in the range of masterids
     if vm == (masterid + 1 ) or vm == (masterid + 2 ):
       # remove the vm
       k3s_remove_node(vm)

 # define default workerid ( -1 ) 
 workerid = masterid + 3

 # create new worker nodes per config
 if workers > 0:

   # first id in the loop
   worker_count = int(1)

   # cycle through possible workers
   while ( worker_count <= workers ):
     # calculate workerid
     workerid = masterid + 3 + worker_count
     kmsg('k3s_worker-check', vmnames[workerid])

     # if existing vm with this id found
     if workerid not in vmids:
       clone(workerid)

     # checks worker has k3s installed first
     k3s_init_node(workerid,'worker')
     worker_count = worker_count + 1

 # remove extra workers
 for vm in vmids:
   if vm > workerid:
     kmsg('k3s_extra-worker', vmnames[vm])
     k3s_remove_node(vm)

 # display cluster info
 cluster_info()

# kubeconfig
def kubeconfig():
  # replace 127.0.0.1 with m1 ip
  kconfig = qaexec(masterid, 'cat /etc/rancher/k3s/k3s.yaml').replace('127.0.0.1', vmip(masterid))

  # write file out
  with open(f'{cluster_name}.kubeconfig','w') as kfile:
    kfile.write(kconfig)
  kmsg('k3s_kubeconfig', ('saved ' + (cluster_name +'.kubeconfig')))

# kubectl
def kubectl(cmd):
  k3s_cmd = '/usr/local/bin/k3s kubectl ' + str(cmd)
  kcmd = qaexec(masterid,k3s_cmd)
  # strip line break
  return(kcmd)

# export k3s token
def export_k3s_token():
  token = qaexec(masterid, 'cat /var/lib/rancher/k3s/server/token')
  token_name = f'{cluster_name}.k3stoken'
  with open(token_name, 'w') as token_file:
    token_file.write(token)
  kmsg('k3s_export-token', f'created: {token_name}', 'sys')
