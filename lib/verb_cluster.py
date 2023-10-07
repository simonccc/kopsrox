import common_config as common, sys, os, re, time
import kopsrox_proxmox as proxmox
import kopsrox_k3s as k3s

verb = 'cluster'
verbs = common.verbs_cluster

# check for arguments
try:
  if (sys.argv[2]):
    passed_verb = str(sys.argv[2])
except:
  print('ERROR: pass a command')
  print('kopsrox', verb, '', end='')
  common.verbs_help(verbs)
  exit(0)

# unsupported verb
if not passed_verb in verbs:
  print('ERROR: \''+ passed_verb + '\'- command not found')
  print('kopsrox', verb, '', end='')
  common.verbs_help(verbs)
  exit(0)

# import config
config = common.read_kopsrox_ini()

# variables from config
proxnode = config['proxmox']['proxnode']
proximgid = config['proxmox']['proximgid']
workers = int(config['cluster']['workers'])
masters = int(config['cluster']['masters'])

# masterid
masterid = common.get_master_id()

# info
if passed_verb == 'info':
  print('cluster::info:')

  # map dict of ids and node
  vms = proxmox.list_kopsrox_vm()

  # for kopsrox vms
  for vm in vms:

    # get vm status
    node = vms[vm]
    vm_info = proxmox.vm_info(vm,node)

    # vars
    vmname = vm_info.get('name')
    vmstatus = vm_info.get('status')
    ip = common.vmip(vm)

    # print
    print(vm, '-', vmname, "status:", vmstatus, 'ip:', ip + ' [' + node + ']')

  print('cluster::k3s::nodes')
  print(common.kubectl(masterid, 'get nodes'))

# update current cluster
if ( passed_verb == 'update' ):
  print('cluster::update: running')
  k3s.k3s_update_cluster()

# create new cluster
if ( passed_verb == 'create' ):
  print('cluster::create: running')

  # get list of runnning vms
  vmids = proxmox.list_kopsrox_vm()

  # clone new master
  if not (int(masterid) in vmids):
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
if passed_verb == 'kubectl':

  # convert command line into string
  cmd= '';  
  for arg in sys.argv[1:]:          
    if ' ' in arg:
      # Put the quotes back in
      cmd+='"{}" '.format(arg) ;  
    else:
      # Assume no space => no quotes
      cmd+="{} ".format(arg) ;   

  # remove first 2 commands
  cmd = cmd.replace('cluster kubectl ','')

  # run command and show output
  print('cluster::kubectl:', cmd)
  print(common.kubectl(masterid,cmd))

# export kubeconfig to file
if passed_verb == 'kubeconfig':
  common.kubeconfig(masterid)

# destroy the cluster
if passed_verb == 'destroy':
  k3s.k3s_rm_cluster()
