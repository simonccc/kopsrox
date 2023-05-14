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
    vmid = vm_info.get('vmid')
    vmname = vm_info.get('name')
    vmstatus = vm_info.get('status')

    ip = common.vmip(vmid)

    # print
    print(vmid, '-', vmname, "status:", vmstatus, 'ip:', ip)

  #print(vms)
  print('kopsrox cluster:')
  k = common.kubectl(masterid, 'get nodes')
  print(k)
  print('events')
  print(common.kubectl(masterid, 'get events'))
  exit(0)

# create new cluster
# check for existing install
# check files as well 
if passed_verb == 'create':
  print('checking cluster state')

  # get list of runnning vms
  vmids = common.list_kopsrox_vm()

  # handle master install
  if (int(masterid) in vmids):
    print('found existing master vm', masterid)
  else:
    common.clone(masterid)

  # install k3s 
  install_master = common.k3s_init_master(masterid)
  if ( install_master == 'true'):
    print('create: master', masterid,'ok')
  else:
    print('ERROR: master not installed')
    exit(0)

  # export kubeconfig
  common.kubeconfig(masterid)

  # export token
  common.k3stoken(masterid)

  # create new worker nodes per config
  if ( int(workers) > 0 ):
    print('checking', workers, 'workers')

    # first id in the loop
    worker_count = 1 

    # cycle through possible workers
    while ( worker_count <= int(workers) ):

      # calculate workerid
      workerid = str(int(proximgid) + 4 + worker_count)

      # if existing vm with this id found
      if (int(workerid) in vmids):
          print('found existing worker', workerid)
      else:
        common.clone(workerid)
      worker_count = worker_count + 1
      install_worker = common.k3s_init_worker(workerid)

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
