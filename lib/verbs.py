#!/usr/bin/env python3

import sys

verbs = ['create', 'show']

try:
  if (sys.argv[1]):
    passed_verb = str(sys.argv[1])
    if passed_verb in verbs:
      print(passed_verb)
    for i in verbs:
      print(i)

except:
  print('pass a verb:', '\n')
  for i in verbs:
    print(i)
