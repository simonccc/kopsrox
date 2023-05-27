import common_config as common, sys, re
import kopsrox_k3s as k3s
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

# node needs a 3rd argument
try:
  if (sys.argv[3]):
    node  = str(sys.argv[3])
except:
  print('ERROR: pass a node')
  exit(0)

# get list of valid node names
vmnames = common.vmnames()

# look for node name in list
if not (re.search(node, str(vmnames))):
  print(node, 'not found! running nodes are:')
  for name in vmnames:
    print(name)
  exit(0)

# delete node
if passed_verb == 'destroy':
  print(node)
  k3s.k3s_rm(common.vmname2id(node))
