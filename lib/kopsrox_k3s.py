#!/usr/bin/env python3 

# imports
from kopsrox_config import *
from kopsrox_proxmox import * 

# check for k3s status
def k3s_check(vmid: int):

  # test call
  try:
    get_node = kubectl('get node ' + vmnames[vmid])
  except:
    exit(0)

  # if not found or Ready
  if re.search('NotReady', get_node) or re.search('NotFound', get_node):
    exit(0)

  # return true if Ready
  if re.search('Ready', get_node):
    return True
  else:
    exit(0)

# create a master/slave/worker
def k3s_init_node(vmid: int = masterid,nodetype = 'master'):

  # nodetype error check
  if nodetype not in ['master', 'slave', 'worker', 'restore']:
    kmsg('k3s_init-node', f'{nodetype} invalid nodetype', 'err')
    exit(0)

  # check node has internet
  try:
    internet_check(vmid)
  except:
    kmsg('k3s_init-node', f'{vmid} no internet', 'err')
    exit(0)
 
  # check status of node
  # what does this check?
  try:
    if not k3s_check(vmid):
      exit(0)
  except:
    kmsg(f'k3s_{nodetype}-init', f'configuring {k3s_version} on {vmnames[vmid]}')

    # get existing token if it exists
    token_fname = f'{cluster_name}.k3stoken'
    if os.path.isfile(token_fname):
      token = open(token_fname, "r").read()
      token_cmd = f' --token {token}'

    # defines
    k3s_install_options = f'--kubelet-arg --cloud-provider=external --kubelet-arg --provider-id=proxmox://{cluster_name}/{vmid} {token_cmd}'
    k3s_install_version = f'cat /k3s.sh | INSTALL_K3S_VERSION={k3s_version}'
    k3s_install_master = f'{k3s_install_version} sh -s - server --cluster-init --disable=servicelb,local-storage --node-label="topology.kubernetes.io/zone={proxmox_node}" {k3s_install_options}'
    k3s_install_slave = f'{k3s_install_version} sh -s - server --server https://{network_ip}:6443 {k3s_install_options}'
    k3s_install_worker = f'rm -rf /etc/rancher/k3s/* && {k3s_install_version} sh -s - agent --server="https://{network_ip}:6443" {k3s_install_options}'

    # master
    if nodetype == 'master':
      init_cmd = k3s_install_master

    # slave
    if nodetype == 'slave':
      init_cmd = k3s_install_slave

    # worker
    if nodetype == 'worker':
      init_cmd = k3s_install_worker

    # restore
    if nodetype == 'restore':
      # get latest snapshot
      bs_cmd = f'{k3s_install_master} && /usr/local/bin/k3s etcd-snapshot ls 2>&1 && systemctl stop k3s && rm -rf /var/lib/rancher'
      bs_cmd_out = qaexec(vmid,bs_cmd)

      # sort ls output so last is latest snapshot
      for snap in sorted(bs_cmd_out.split('\n')):
        if re.search(f'kopsrox-{cluster_name}', snap.split()[0]):
            latest = snap.split()[0]

      kmsg(f'k3s_restore', f'restoring {latest}')
      init_cmd = f'/usr/local/bin/k3s server --cluster-reset --cluster-reset-restore-path={latest} --token={token} 2>&1 && systemctl start k3s'

    # write log of install on node
    init_cmd = init_cmd + f' > /k3s_{nodetype}_install.log 2>&1'

    # run command
    qaexec(vmid,init_cmd)

    # wait until ready
    wait: int = 20
    count: int = 1 
    status = ''
    while not status == 'Ready':

      try:
        if not k3s_check(vmid):
          exit(0)
        else:
          status = 'Ready'
      except:
        count += 1
        if count == wait:
          kmsg('k3s_check', f'timed out after {wait}s for {vmnames[vmid]}', 'err')
          exit(0)
        time.sleep(1)

    # final steps for first master / restore export kubeconfig and token 
    if nodetype in ['master', 'restore']:
      kubeconfig()
      export_k3s_token()

# remove a node
def k3s_remove_node(vmid: int):
  
  # get vmname
  vmname = vmnames[vmid]
  kmsg('k3s_remove-node', vmname)

  if vmname != f'{cluster_name}-m1':
    kubectl('cordon ' + vmname)
    kubectl('drain --timeout=10s --delete-emptydir-data --ignore-daemonsets --force ' + vmname)
    kubectl('delete node ' + vmname)

  # destroy vm
  prox_destroy(vmid)

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
    if vmname == f'{cluster_name}-m1':
      prox_destroy(vmid)
    else:
      k3s_remove_node(vmid)

# builds or removes other nodes from the cluster as required per config
def k3s_update_cluster():
 kmsg('k3s_update-cluster', f'{cluster_name}/{k3s_version} - checking {masters} masters and {workers} workers', 'sys')

 # checks the master node
 k3s_init_node()

 # get list of running vms
 vmids = list_kopsrox_vm()

 # do we need to run any more masters
 if masters > 1:
  master_count = int(1)

  while ( master_count <=  2 ):

    # so eg 601 + 1 = 602 = m2
    slave_masterid = masterid + master_count
    slave_hostname = vmnames[slave_masterid]

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
   worker_count: int = 1

   # cycle through possible workers
   while ( worker_count <= workers ):
     # calculate workerid
     workerid = masterid + 3 + worker_count

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

  # define filename
  kubeconfig_file = f'{cluster_name}.kubeconfig'
  # replace 127.0.0.1 with vip ip
  kconfig = qaexec(masterid, 'cat /etc/rancher/k3s/k3s.yaml').replace('127.0.0.1', network_ip)
  with open(kubeconfig_file, 'w') as kubeconfig_file_handle:
    kubeconfig_file_handle.write(kconfig)
  kmsg('k3s_kubeconfig', f'saved {kubeconfig_file}')

# kubectl
def kubectl(cmd):
  k3s_cmd = f'/usr/local/bin/kubectl {cmd} 2>&1'
  kcmd = qaexec(masterid,k3s_cmd)
  return(kcmd)

# run k3s check config
def k3s_check_config():
  kmsg('k3s_check-config', 'checking k3s config')
  k3s_cmd = f'/usr/local/bin/k3s check-config'
  kcmd = qaexec(masterid,k3s_cmd)
  print(kcmd)

# export k3s token
def export_k3s_token():

  # define token file name
  token_name = f'{cluster_name}.k3stoken'
  # get masters token
  live_token = qaexec(masterid, 'cat /var/lib/rancher/k3s/server/token')

  # check existing token
  if os.path.isfile(token_name):

    saved_token = open(token_name, "r").read()
    # difference between live and local token
    if not saved_token == live_token:

      # passwords are different..
      if not saved_token.split(':')[3]  == live_token.split(':')[3]:
        kmsg('k3s_export-token', 'passwords different between live system and local token! exiting', 'err')
        exit(0)

      # CA is different - expected on a new cluster
      kmsg('k3s_export-token', f'found: {token_name} updating CA')
      with open(token_name, 'w') as token_file:
        token_file.write(live_token)

    # existing token file matches live    
    else:
      kmsg('k3s_export-token', f'found: {token_name} OK')

  # no token found so write new one 
  else:
    with open(token_name, 'w') as token_file:
      token_file.write(live_token)
    kmsg('k3s_export-token', f'created: {token_name}')

# cluster info
def cluster_info():

  # live nodes in cluster 
  cluster_info_vms = list_kopsrox_vm()

  # check m1 id exists
  if not masterid in cluster_info_vms:
    kmsg(kname, f'cluster {cluster_name} does not exist', 'err')
    exit(0)

  kmsg(f'cluster_info', '', 'sys')
  curr_master = get_kube_vip_master()

  # for kopsrox vms
  for vmid in cluster_info_vms:
    if not cluster_id == vmid:
      hostname = vmnames[vmid]
      vmstatus = f'[{cluster_info_vms[vmid]}] {vmip(vmid)}/{network_mask}'
      if hostname == curr_master:
        vmstatus += f' vip {network_ip}/{network_mask}'
      kmsg(f'{hostname}_{vmid}', f'{vmstatus}')

  # fix this
  kmsg('kubectl_get-nodes', f'\n{kubectl("get nodes")}')

# return current vip master
def get_kube_vip_master():
  kubevip_q = f'get nodes --selector kube-vip.io/has-ip={network_ip}'
  kubevip_o = kubectl(kubevip_q)
  try:
    kubevip_m = kubevip_o.split()[5]
  except:
    kubevip_m = ''
  return(kubevip_m)
