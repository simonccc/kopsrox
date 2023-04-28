import common_config as common
verb = 'create'
verbs = common.verbs_create

try:
  import sys
  if (sys.argv[2]):
    passed_verb = str(sys.argv[2])
except:
  common.verbs_help(verbs)
  exit(0)

if passed_verb in verbs:
  print(passed_verb)
  verbm = __import__('verb_'+ verb + '_' + passed_verb)
  exit(0)

# if passed arg invalid
print('ERROR: \'',passed_verb,'\' command not found.')
common.verbs_help(verbs)
