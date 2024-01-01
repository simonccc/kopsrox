#!/usr/bin/env python3 

# imports
from kopsrox_config import masterid, config, k3s_version, masters, workers, cname, vmnames, kmsg_info, kmsg_err, vmip, cluster_info, list_kopsrox_vm, kmsg_sys, kmsg_warn

# standard imports
from kopsrox_proxmox import qaexec, destroy, internet_check, clone

# standard imports
import re, time

# define k3s commands
k3s_install_base = 'cat /k3s.sh | INSTALL_K3S_VERSION="' + k3s_version + '" '
k3s_install_master = k3s_install_base + 'sh -s - server --cluster-init'

# check for k3s status
def k3s_check(vmid):
    
  # check k3s installed
  k3sbincheck = qaexec(vmid, 'if [ ! -e /usr/local/bin/k3s ] ; then echo nok3sbin; fi')

  if k3sbincheck == 'nok3sbin':
    exit()

  # test call
  get_node = kubectl('get node ' + vmnames[int(vmid)])

  # if not found or Ready
  if ( re.search('NotReady', get_node) or re.search('NotFound', get_node)):
    return False

  # return true if Ready
  if re.search('Ready', get_node):
    return True

  # failsafe
  return False

# wait for node
def k3s_check_mon(vmid):

  # check count
  count = int(0)

  # run k3s_check
  while not k3s_check(vmid):

    # counter + sleep
    count += 1
    time.sleep(1)

    # timeout after 30 secs
    if count == 30:
      kmsg_err('k3s-check-mon', ('timed out after 30s for '+ vmnames[vmid]))
      exit(0)

  return True

# init 1st master
def k3s_init_master(vmid):
    
  # if master check fails
  try:
    k3s_check(vmid)
  except:
    kmsg_info('k3s-init-master', vmnames[vmid])

    # check vm has internet 
    internet_check(vmid)

    # install command
    qaexec(vmid,k3s_install_master)

    try:
      # loops until k3s is up
      k3s_check_mon(vmid)
    except:
      kmsg_err(('k3s-init-' + vmid), ('failed to install k3s on '+ vmname))
      exit()

  # export kubeconfig
  kubeconfig(vmid)

# additional master
def k3s_init_slave(vmid):
  try:
    k3s_check(vmid)
  except:
    kmsg_info('k3s-init-slave', vmnames[vmid])
    ip = vmip(masterid)
    token = get_token()

    cmd = 'cat /k3s.sh | INSTALL_K3S_VERSION="' + k3s_version + '" K3S_TOKEN=\"' + token + '\" sh -s - server --server ' + 'https://' + ip + ':6443'
    qaexec(vmid,cmd)

    # wait for node to join cluster
    k3s_check_mon(vmid)
  return True

# init worker node
def k3s_init_worker(vmid):
  try:
    k3s_check(vmid)
  except:
    kmsg_info('k3s-init-worker', vmnames[vmid])
    ip = vmip(masterid)
    token = get_token()
    cmd = 'cat /k3s.sh | INSTALL_K3S_VERSION="' + k3s_version + '" K3S_URL=\"https://' + ip + ':6443\" K3S_TOKEN=\"' + token + '\" sh -s'
    qaexec(vmid,cmd)
    k3s_check_mon(vmid)
  return True

# remove a node
def k3s_rm(vmid):
  vmname = vmnames[vmid]
  kmsg_info('k3s-remove-node', vmname)

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
    if restore:
      if vmname == ( cname + '-m1' ):
        continue

    # do not delete image
    if vmname == ( cname + '-i0' ):
      continue

    # remove node from cluster and proxmox
    #print(vmname)
    if vmname ==  ( cname + '-m1' ):
      destroy(vmid)
    else:
      k3s_rm(vmid)

# builds or removes other nodes from the cluster as required per config
def k3s_update_cluster():

 # refresh the master token
 token = qaexec(masterid, 'cat /var/lib/rancher/k3s/server/node-token')
 with open('kopsrox.k3stoken', 'w') as k3s:
   k3s.write(token)

 # get list of running vms
 vmids = list_kopsrox_vm()

 # do we need to run any more masters
 if ( masters > 1 ):
  master_count = int(1)

  while ( master_count <=  2 ):

    # so eg 601 + 1 = 602 = m2
    slave_masterid = int(masterid) + master_count
    slave_hostname = vmnames[slave_masterid]
    kmsg_info('k3s-cluster-check', slave_hostname)

    # existing server
    if slave_masterid not in vmids:
      clone(slave_masterid)

    # install k3s on slave and join it to master
    if not k3s_init_slave(slave_masterid):
      kmsg_err('k3s-init-slave', ('failed to install slave ' + slave_hostname))
      exit()

    # next possible master ( m3 ) 
    master_count = master_count + 1

 # check for extra masters
 if ( masters == 1 ):
   for vm in vmids:
     # is this required?
     vm = int(vm)

     # if vm is in the range of masterids
     if vm == (masterid + 1 ) or vm == (masterid + 2 ):
       # remove the vm
       k3s_rm(vm)

   # define default workerid ( -1 ) 
 workerid = masterid + 3

 # create new worker nodes per config
 if ( workers > 0 ):

   # first id in the loop
   worker_count = int(1)

   # cycle through possible workers
   while ( worker_count <= workers ):
     # calculate workerid
     workerid = masterid + 3 + worker_count
     kmsg_info('k3s-workers-check', vmnames[workerid])

     # if existing vm with this id found
     if workerid not in vmids:
       clone(workerid)

     # checks worker has k3s installed first
     k3s_init_worker(workerid) 
     worker_count = worker_count + 1

   # remove extra workers
 for vm in vmids:
   if vm > workerid:
     kmsg_info('k3s-extra-worker', vmnames[vm])
     k3s_rm(vm)

 # display cluster info
 cluster_info()

# kubeconfig
def kubeconfig(masterid):
  kubeconfig = qaexec(masterid, 'cat /etc/rancher/k3s/k3s.yaml')

  # replace localhost with masters ip
  kubeconfig = kubeconfig.replace('127.0.0.1', vmip(masterid))

  # write file out
  with open('kopsrox.kubeconfig', 'w') as kubeconfig_file:
    kubeconfig_file.write(kubeconfig)

# kubectl
def kubectl(cmd):
  k3s_cmd = '/usr/local/bin/k3s kubectl ' + str(cmd)
  kcmd = qaexec(masterid,k3s_cmd)
  # strip line break
  return(kcmd)

# get local token with line break removed
def get_token():
  k3stoken = open("kopsrox.k3stoken", "r")
  token = k3stoken.read().rstrip()
  k3stoken.close()
  return(token)
