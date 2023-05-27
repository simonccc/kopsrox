import common_config as common, sys, re
import kopsrox_proxmox as proxmox

# verb config
verb = 'etcd'
verbs = common.verbs_etcd

# check for arguments
try:
  if (sys.argv[2]):
    passed_verb = str(sys.argv[2])
except:
  print('ERROR: pass a command')
  print(verb, '', end='')
  common.verbs_help(verbs)
  exit(0)

# unsupported verb
if not passed_verb in verbs:
  print('ERROR:\''+ passed_verb + '\'- command not found')
  print('kopsrox', verb, '', end='')
  common.verbs_help(verbs)

# check for number of nodes

# snapshot
if passed_verb == 'snapshot':
  masterid = common.get_master_id()
  print('snapshot', masterid)
  snapout = proxmox.qaexec(masterid, 'k3s etcd-snapshot')
  for line in snapout.split():
    if (re.search('path', line)):
        rpath = line.split(':')
  path = rpath[8].replace('}', '')
  print(path)

