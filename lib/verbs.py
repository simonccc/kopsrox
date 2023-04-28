verbs = ['create', 'show']

# verbs helper
def verbs_help():
  print('pass a verb:', '\n')
  for i in verbs:
    print(i)

try:
  import sys
  if (sys.argv[1]):
    passed_verb = str(sys.argv[1])
except:
  verbs_help()
  exit(0)

if passed_verb in verbs:
  print(passed_verb)
  exit(0)

# if passed arg invalid
verbs_help()
