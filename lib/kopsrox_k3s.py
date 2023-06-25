import common_config as common
import kopsrox_proxmox as proxmox
import re, time

# config
config = common.read_kopsrox_ini()
k3s_version = (config['cluster']['k3s_version'])
masterid = common.get_master_id()

# check for k3s status
def k3s_check(vmid):

    # get masterid
    node_name = common.vmname(vmid)

    # check for exiting k3s
    cmd = 'if [ -f /usr/local/bin/k3s ] ; then echo -n present; else echo -n fail;fi'
    k3s_check = proxmox.qaexec(vmid,cmd)

    # fail early
    if ( k3s_check == 'fail' ):
      #3print('k3s_check: no k3s bin found')
      return('fail')

    # check node is healthy
    if (k3s_check == 'present'):

      # test call
      k = common.kubectl(masterid, ('get node ' + node_name))

      # check for node not ready or not yet joined cluster
      while ( re.search('NotReady', k) or re.search('NotFound', k)):
        k = common.kubectl(masterid, ('get node ' + node_name))
        print('k3s_check:', node_name, 'not ready')
        time.sleep(10)

      return('true')

    # else return fail
    return('fail')

# init 1st master
def k3s_init_master(vmid):

    # check for existing k3s
    status = k3s_check(vmid)

    # if master check fails
    if ( status == 'fail'):
      print('k3s_init_master: installing k3s on', vmid)
      cmd = 'curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="' + k3s_version + '" sh -s - server --cluster-init'
      proxmox.qaexec(vmid,cmd)

    status = k3s_check(vmid)
    return(status)

# additional master
def k3s_init_slave(vmid):

    # check for existing k3s
    status = k3s_check(vmid)

    # if master check fails
    if ( status == 'fail'):
      ip = common.vmip(masterid)
      token = common.get_token()
      print('k3s_init_slave: installing k3s on', vmid)
      cmd = 'curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="' + k3s_version + '" K3S_TOKEN=\"' + token + '\" sh -s - server --server ' + 'https://' + ip + ':6443'
      proxmox.qaexec(vmid,cmd)

    status = k3s_check(vmid)
    return(status)

# init worker node
def k3s_init_worker(vmid):

  # check for existing k3s
  status = k3s_check(vmid)

  # if check fails
  if ( status == 'fail'):

    print('k3s_init_worker: installing k3s on', vmid)
    ip = common.vmip(masterid)
    token = common.get_token()

    cmd = 'curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="' + k3s_version + '" K3S_URL=\"https://' + ip + ':6443\" K3S_TOKEN=\"' + token + '\" sh -s'
    proxmox.qaexec(vmid,cmd)
     
    status = k3s_check(vmid)
    return(status)
  print('k3s_init_worker:', vmid, 'ok')

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
      if vmname == 'kopsrox-m1':
        continue

    # do not delete image
    if ( vmname =='kopsrox-image'):
      continue

    # do not delete utility server
    if ( vmname =='kopsrox-u1'):
      continue
    
    # remove node from cluster and proxmox
    #print(vmname)
    if vmname == 'kopsrox-m1':
      proxmox.destroy(vmid)
    else:
      k3s_rm(vmid)
