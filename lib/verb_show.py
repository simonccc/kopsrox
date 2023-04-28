import common_config as common
verb = 'show'
verbs = common.verbs_show

try:
  import sys
  if (sys.argv[2]):
    passed_verb = str(sys.argv[2])
except:
  print(verb)
  common.verbs_help(verbs)
  exit(0)

if passed_verb in verbs:
  print(passed_verb)
  verbm = __import__('verb_'+ verb + '_' + passed_verb)
  exit(0)

# if passed arg invalid
print(verb)
print('ERROR: \'',passed_verb,'\' command not found.')
common.verbs_help(verbs)
