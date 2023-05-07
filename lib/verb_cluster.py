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
masterid = str(int(proximgid) + 1)

# info
if passed_verb == 'info':
  print('kopsrox cluster info:')

  # for kopsrox vms
  for vm in common.list_kopsrox_vm():

    # get vm status
    vm_info = kprox.prox.nodes(proxnode).qemu(vm).status.current.get()

    # vars
    vmid = vm_info.get('vmid')
    vmname = vm_info.get('name')
    vmstatus = vm_info.get('status')
    vmuptime = vm_info.get('uptime')
    vmcpu = vm_info.get('cpu')

    # print
    print(vmid, '-', vmname, "status:", vmstatus, 'uptime:', vmuptime, 'cpu:', vmcpu)

    # if vm is running run kubectl
    if ( vmstatus == 'running'):
      print('kubectl')
      kubectl = common.kubectl(vmid, 'get nodes')
      print(kubectl)

  #print(vms)
  exit(0)

# create new cluster
# check for existing install
# check files as well 
if passed_verb == 'create':
  print('create: cluster')

  # get list of runnning vms
  vmids = common.list_kopsrox_vm()

  # handle master install
  if (int(masterid) in vmids):
    print('create: found existing master vm', masterid)
  else:
    common.clone(masterid)

  # install k3s 
  install_master = common.k3s_init_master(masterid)
  if ( install_master == 'true'):
    print('create: master', masterid,'ok')
  else:
    print('ERROR: master not installed')
    exit(0)

  # create new nodes per config
  print('build', workers, 'workers')

# kubectl
if passed_verb == 'kubectl':

  # convert command line into string
  cmd= '';  
  for arg in sys.argv[1:]:          # skip sys.argv[0] since the question didn't ask for it
    if ' ' in arg:
      cmd+= '"{}" '.format(arg) ;   # Put the quotes back in
    else:
      cmd+="{} ".format(arg) ;      # Assume no space => no quotes

  cmd = cmd.replace('cluster kubectl ','')
  print('cluster kubectl: ', cmd)
  k = common.kubectl(masterid,cmd)
  print(k)


# destroy
if passed_verb == 'destroy':
  print('destroying cluster')
  vmids = common.list_kopsrox_vm()
  for i in vmids:
      if ( int(i) != int(proximgid)):
        print('destroying vmid', i)
        common.destroy(i)
