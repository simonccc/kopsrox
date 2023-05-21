import common_config as common, sys, os, wget, re, time, urllib.parse
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
import proxmox_config as kprox

# variables from config
proxnode = (config['proxmox']['proxnode'])
proximgid = (config['proxmox']['proximgid'])
workers = (config['cluster']['workers'])

# this assignment will need to be in config in future
masterid = common.get_master_id()

# info
if passed_verb == 'info':
  print('kopsrox vm info:')

  # for kopsrox vms
  for vm in common.list_kopsrox_vm():

    # get vm status
    vm_info = common.vm_info(vm)

    # vars
    vmname = vm_info.get('name')
    vmstatus = vm_info.get('status')
    ip = common.vmip(vm)

    # print
    print(vm, '-', vmname, "status:", vmstatus, 'ip:', ip)

  print('kopsrox cluster:')
  print(common.kubectl(masterid, 'get nodes'))
  print(common.kubectl(masterid, 'get events'))
  exit(1)

# create new cluster
if passed_verb == 'create':

  # get list of runnning vms
  vmids = common.list_kopsrox_vm()

  # clone new master
  if not (int(masterid) in vmids):
    common.clone(masterid)

  # install k3s 
  install_master = common.k3s_init_master(masterid)
  if ( install_master == 'true'):
    print('cluster-create: master', masterid,'ok')
  else:
    print('ERROR: master not installed')
    exit(0)

  # export kubeconfig
  common.kubeconfig(masterid)

  # export token
  common.k3stoken(masterid)

  # create new worker nodes per config
  if ( int(workers) > 0 ):
    print('cluster-create: checking workers ('+ workers +')')

    # first id in the loop
    worker_count = 1 

    # cycle through possible workers
    while ( worker_count <= int(workers) ):

      # calculate workerid
      workerid = str(int(proximgid) + 4 + worker_count)

      # if existing vm with this id found
      if (int(workerid) in vmids):
          worker_name = common.vmname(int(workerid))
          print('cluster: found existing', worker_name)
      else:
        common.clone(workerid)

      worker_count = worker_count + 1

      # checks worker has k3s installed first
      install_worker = common.k3s_init_worker(workerid)

  # check for extra workers
  for vm in vmids:
    if ( int(vm) > int(workerid)):
      worker_name = common.vmname(int(vm))
      print('cluster: removing extra worker', worker_name)
      common.remove_worker(vm)
  print(common.kubectl(masterid, 'get nodes'))

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
  print('cluster kubectl:', cmd)
  print(common.kubectl(masterid,cmd))

# export kubeconfig to file
if passed_verb == 'kubeconfig':
    common.kubeconfig(masterid)

# destroy
if passed_verb == 'destroy':
  print('destroying cluster')
  vmids = common.list_kopsrox_vm()
  for i in vmids:
      if ( int(i) != int(proximgid)):
        print('destroying vmid', i)
        common.destroy(i)
