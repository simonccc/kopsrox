import common_config as common
verbs = common.top_verbs

try:
  import sys
  if (sys.argv[1]):
    passed_verb = str(sys.argv[1])
except:
  print('ERROR: no command passed')
  print('kopsrox ', end='')
  common.verbs_help(verbs)
  exit(0)

if passed_verb in verbs:
  verb = __import__('verb_' + passed_verb)
  exit(0)

# if passed arg invalid
print('ERROR: \'' + passed_verb + '\' command not found.')
print('kopsrox ', end='')
common.verbs_help(verbs)
