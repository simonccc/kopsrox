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
    workername = common.vmname(vmid)
    print('k3s_rm:', workername)

    # kubectl commands to remove node
    common.kubectl(masterid, ('cordon ' + workername))
    common.kubectl(masterid, ('drain --timeout=5s --ignore-daemonsets --force ' +  workername))
    common.kubectl(masterid, ('delete node ' + workername))

    # destroy vm
    print('proxmox:destroy:', vmid)
    proxmox.destroy(vmid)
