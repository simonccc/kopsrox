#!/usr/bin/env python3 

import common_config as common
import kopsrox_proxmox as proxmox
import re, time

# config
config = common.read_kopsrox_ini()
k3s_version = config['cluster']['k3s_version']
masters = int(config['cluster']['masters'])
workers = int(config['cluster']['workers'])
masterid = int(common.get_master_id())
cname = config['cluster']['name']

# check for k3s status
def k3s_check(vmid):

    # get masterid
    node_name = common.vmname(vmid)

    # test call
    k = common.kubectl(masterid, ('get node ' + node_name))
    if ( re.search('NotReady', k) or re.search('NotFound', k)):
      print('k3s::k3s_check:', node_name, 'not ready')
      return('fail')
    # return true if Ready
    if ( re.search('Ready', k)) :
      return('true')

    # failsafe
    #print(k)
    return('fail')

# wait for node
def k3s_check_mon(vmid):
  while ( k3s_check(vmid) != 'true' ):
    time.sleep(10)

# init 1st master
def k3s_init_master(vmid):

    # get hostname
    vmname = common.vmname(vmid)

    # check for existing k3s
    status = k3s_check(vmid)

    # if master check fails
    if ( status == 'fail'):
      print('k3s::k3s_init_master: installing k3s on', vmname)
      cmd = 'cat /k3s.sh | INSTALL_K3S_VERSION="' + k3s_version + '" sh -s - server --cluster-init'
      cmd_out = proxmox.qaexec(vmid,cmd)
      k3s_check_mon(vmid)
      return('true')

    return(status)

# additional master
def k3s_init_slave(vmid):

    # check for existing k3s
    status = k3s_check(vmid)

    # if master check fails
    if ( status == 'fail'):
      ip = common.vmip(masterid)
      token = common.get_token()
      vmname = common.vmname(vmid)
      print('k3s::k3s_init_slave: installing k3s on', vmname)

      # cmd
      cmd = 'cat /k3s.sh | INSTALL_K3S_VERSION="' + k3s_version + '" K3S_TOKEN=\"' + token + '\" sh -s - server --server ' + 'https://' + ip + ':6443'
      cmdout = proxmox.qaexec(vmid,cmd)

      # wait for node to join cluster
      k3s_check_mon(vmid)
      return('true')

    return(status)

# init worker node
def k3s_init_worker(vmid):

  # check for existing k3s
  status = k3s_check(vmid)
 
  # map vmname
  vmname = common.vmname(vmid)

  # if check fails
  if ( status == 'fail'):

    ip = common.vmip(masterid)
    token = common.get_token()
    cmd = 'cat /k3s.sh | INSTALL_K3S_VERSION="' + k3s_version + '" K3S_URL=\"https://' + ip + ':6443\" K3S_TOKEN=\"' + token + '\" sh -s'

    print('k3s::k3s_init_worker: installing k3s on', vmid)
    proxmox.qaexec(vmid,cmd)
    k3s_check_mon(vmid)
     
  status = k3s_check(vmid)
  print('k3s::k3s_init_worker:',vmname, 'ok')
  return(status)

# remove a node
def k3s_rm(vmid):
  vmname = common.vmname(vmid)
  print('k3s::k3s_rm:', vmname)

  # kubectl commands to remove node
  common.kubectl(masterid, ('cordon ' + vmname))
  common.kubectl(masterid, ('drain --timeout=5s --ignore-daemonsets --force ' + vmname))
  common.kubectl(masterid, ('delete node ' + vmname))

  # destroy vm
  proxmox.destroy(vmid)

# remove cluster - leave master if restore = true
def k3s_rm_cluster(restore = False):

  # list all kopsrox vm id's
  for vmid in sorted(proxmox.list_kopsrox_vm(), reverse = True):

    # map hostname
    vmname = common.vmname(vmid)

    # do not delete m1 if restore is true 
    if restore:
      if vmname == ( cname + '-m1' ):
        continue

    # do not delete image
    if vmname == ( cname + '-image' ):
      continue

    # do not delete utility server
    if vmname == ( cname + '-u1' ):
      continue
    
    # remove node from cluster and proxmox
    #print(vmname)
    if vmname ==  ( cname + '-m1' ):
      proxmox.destroy(vmid)
    else:
      k3s_rm(vmid)

# builds or removes other nodes from the cluster as required per config
def k3s_update_cluster():

   # refresh the master token
   common.k3stoken(masterid)

   # get list of running vms
   vmids = proxmox.list_kopsrox_vm()

   # do we need to run any more masters
   if ( masters > 1 ):
    print('k3s::k3s_update_cluster: checking masters ('+ str(masters) +')')
    master_count = 1
    while ( master_count <=  ( int(masters) - 1 )):

      # so eg 601 + 1 = 602 = m2
      slave_masterid = (int(masterid) + int(master_count))
      slave_hostname = common.vmname(slave_masterid)

      print('cluster: checking', slave_hostname)

      # existing server
      if (slave_masterid in vmids):
          print('k3s::k3s_update_cluster: existing vm for', slave_hostname)
      else:
        proxmox.clone(slave_masterid)

      # install k3s on slave and join it to master
      install_slave = k3s_init_slave(slave_masterid)

      # next possible master ( m3 ) 
      master_count = master_count + 1

   # check for extra masters
   if ( masters == 1 ):
     for vm in vmids:
       # if vm is a master ??
       if ( (int(vm) == ((masterid + 1 ))) or (int(vm) == ((masterid + 2 )))):
         master_name = common.vmname(int(vm))
         print('k3s::k3s_update_cluster: removing extra master-slave', master_name)
         k3s_rm(vm)

   # define default workerid
   workerid = str(int(masterid) + 3)

   # create new worker nodes per config
   if ( workers > 0 ):
     print('k3s::k3s_update_cluster: checking workers ('+ str(workers) +')')

     # first id in the loop
     worker_count = 1

     # cycle through possible workers
     while ( worker_count <= workers ):

       # calculate workerid
       workerid = str(masterid + 3 + worker_count)

       # if existing vm with this id found
       if (int(workerid) in vmids):
          worker_name = common.vmname(int(workerid))
          print('k3s::k3s_update_cluster: found existing', worker_name)
       else:
         proxmox.clone(workerid)

       worker_count = worker_count + 1

      # checks worker has k3s installed first
     install_worker = k3s_init_worker(workerid) 

   # remove extra workers
   for vm in vmids:
     if ( int(vm) > int(workerid)):
       worker_name = common.vmname(int(vm))
       print('k3s::k3s_update_cluster: removing extra worker', worker_name)
       k3s_rm(vm)
   print(common.kubectl(masterid, 'get nodes'))
   
