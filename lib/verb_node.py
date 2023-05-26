import common_config as common, sys
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

print(node)
