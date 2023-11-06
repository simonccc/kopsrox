#!/usr/bin/env python3 

# common import
import kopsrox_config as kopsrox_config

# standard imports
import kopsrox_proxmox as proxmox
import re, time

# config
config = kopsrox_config.config

# vars
k3s_version = kopsrox_config.k3s_version
masters = int(config['cluster']['masters'])
workers = int(config['cluster']['workers'])
masterid = int(kopsrox_config.get_master_id())

# cluster name
cname = config['cluster']['name']

# vmnames 
vmnames = kopsrox_config.vmnames

# kname
kname = 'kopsrox::k3s::'

# check for k3s status
def k3s_check(vmid):

    # test call
    k = kubectl('get node ' + vmnames[int(vmid)])

    # if not found or Ready
    if ( re.search('NotReady', k) or re.search('NotFound', k)):
      return False

    # return true if Ready
    if ( re.search('Ready', k)) :
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
      print(kname + 'k3s_check_mon: ERROR: k3s_check timed out after 30s for ', vmnames[vmid])
      exit(0)

  return True

# init 1st master
def k3s_init_master(vmid):

    # get hostname
    vmname = vmnames[vmid]

    # if master check fails
    if not k3s_check(vmid):
      print('k3s::k3s_init_master: installing k3s on', vmname)
      cmd = 'cat /k3s.sh | INSTALL_K3S_VERSION="' + k3s_version + '" sh -s - server --cluster-init'
      cmd_out = proxmox.qaexec(vmid,cmd)
      k3s_check_mon(vmid)

    return True

# additional master
def k3s_init_slave(vmid):

    # if master check fails
    if not k3s_check(vmid):
      ip = kopsrox_config.vmip(masterid)

      token = get_token()
      vmname = vmnames[vmid]
      print('k3s::k3s_init_slave: installing k3s on', vmname)

      # cmd
      cmd = 'cat /k3s.sh | INSTALL_K3S_VERSION="' + k3s_version + '" K3S_TOKEN=\"' + token + '\" sh -s - server --server ' + 'https://' + ip + ':6443'
      cmdout = proxmox.qaexec(vmid,cmd)

      # wait for node to join cluster
      k3s_check_mon(vmid)
      return True

    return False

# init worker node
def k3s_init_worker(vmid):

  # map vmname
  vmname = vmnames[int(vmid)]

  # if check fails
  if not k3s_check(vmid):

    ip = kopsrox_config.vmip(masterid)
    token = get_token()
    cmd = 'cat /k3s.sh | INSTALL_K3S_VERSION="' + k3s_version + '" K3S_URL=\"https://' + ip + ':6443\" K3S_TOKEN=\"' + token + '\" sh -s'

    print('k3s::k3s_init_worker: installing k3s on', vmid)
    proxmox.qaexec(vmid,cmd)
    k3s_check_mon(vmid)
     
  print('k3s::k3s_init_worker:',vmname, 'ok')
  return True

# remove a node
def k3s_rm(vmid):
  vmname = vmnames[vmid]
  print('k3s::k3s_rm:', vmname)

  # kubectl commands to remove node
  kubectl('cordon ' + vmname)
  kubectl('drain --timeout=5s --ignore-daemonsets --force ' + vmname)
  kubectl('delete node ' + vmname)

  # destroy vm
  proxmox.destroy(vmid)

# remove cluster - leave master if restore = true
def k3s_rm_cluster(restore = False):

  # list all kopsrox vm id's
  for vmid in sorted(kopsrox_config.list_kopsrox_vm(), reverse = True):

    # map hostname
    vmname = vmnames[vmid]

    # do not delete m1 if restore is true 
    if restore:
      if vmname == ( cname + '-m1' ):
        continue

    # do not delete image
    if vmname == ( cname + '-image' ):
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
   token = proxmox.qaexec(masterid, 'cat /var/lib/rancher/k3s/server/node-token')
   with open('kopsrox.k3stoken', 'w') as k3s:
     k3s.write(token)

   # get list of running vms
   vmids = kopsrox_config.list_kopsrox_vm()

   # do we need to run any more masters
   if ( masters > 1 ):
    master_count = int(1)

    while ( master_count <=  2 ):

      # so eg 601 + 1 = 602 = m2
      slave_masterid = (int(masterid) + master_count)
      slave_hostname = vmnames[slave_masterid]

      print(kname + 'k3s_update_cluster: checking', slave_hostname)

      # existing server
      if (slave_masterid in vmids):
          print('k3s::k3s_update_cluster: existing vm for', slave_hostname)
      else:
        proxmox.clone(slave_masterid)

      # install k3s on slave and join it to master
      if not k3s_init_slave(slave_masterid):
        print(kname + 'ERROR! failed to install slave ' + slave_hostname)
        exit(0)

      # next possible master ( m3 ) 
      master_count = master_count + 1

   # check for extra masters
   if ( masters == 1 ):
     for vm in vmids:
       # if vm is a master ??
       if ( (int(vm) == ((masterid + 1 ))) or (int(vm) == ((masterid + 2 )))):
         master_name = vmnames[int(vm)]
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
          worker_name = vmnames[(int(workerid))]
          print('k3s::k3s_update_cluster: found existing', worker_name)
       else:
         proxmox.clone(workerid)

       worker_count = worker_count + 1
       # checks worker has k3s installed first
       install_worker = k3s_init_worker(workerid) 

   # remove extra workers
   for vm in vmids:
     if ( int(vm) > int(workerid)):
       worker_name = vmnames[(int(vm))]
       print('k3s::k3s_update_cluster: removing extra worker', worker_name)
       k3s_rm(vm)
   kopsrox_config.cluster_info()

# kubeconfig
def kubeconfig(masterid):
    ip = kopsrox_config.vmip(masterid)
    kubeconfig = proxmox.qaexec(masterid, 'cat /etc/rancher/k3s/k3s.yaml')

    # replace localhost with masters ip
    kubeconfig = kubeconfig.replace('127.0.0.1', ip)

    # write file out
    with open('kopsrox.kubeconfig', 'w') as kubeconfig_file:
      kubeconfig_file.write(kubeconfig)
    print(kname + 'kopsrox.kubeconfig written')

# kubectl
def kubectl(cmd):
  k3s_cmd = str(('/usr/local/bin/k3s kubectl ' +cmd))
  kcmd = proxmox.qaexec(masterid,k3s_cmd)
  # strip line break
  return(kcmd.rstrip())

# get local token with line break removed
def get_token():
  k3stoken = open("kopsrox.k3stoken", "r")
  token = k3stoken.read().rstrip()
  k3stoken.close()
  return(token)
