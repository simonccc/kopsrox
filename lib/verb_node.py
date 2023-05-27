import common_config as common, sys, re
import kopsrox_k3s as k3s

# verb info
verb = 'node'
verbs = common.verbs_node

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
  exit(0)

# list of valid vm names
vmnames = common.vmnames()

# node needs a 3rd argument
try:
  if (sys.argv[3]):
    node = str(sys.argv[3])
except:
  print('ERROR: pass a node. ')
  exit(0)

# error checking for protected vms
if ( node == 'kopsrox-image' ):
  print('ERROR: run image destroy to remove image')
  exit(0)
if ( node == 'kopsrox-m1' ):
  print('ERROR: run cluster destroy to remove master')
  exit(0)

# look for node name in list
if not (re.search(node, str(vmnames))):
  print(node, 'not found! running nodes are:')
  for name in vmnames:
    print(name)
  exit(0)

# delete node
if passed_verb == 'destroy':
  k3s.k3s_rm(common.vmname2id(node))
