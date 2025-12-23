#!/usr/bin/env python3

# import
from termcolor import cprint

# kmsg
def kmsg(kname = 'kopsrox',msg = 'no msg', sev = 'info'):

  # kname format is blue_cyan text
  knamea = kname.split('_')

  try:
    if knamea[1] and sev == 'info':
      cprint(knamea[0] + '-', "blue",attrs=["bold"], end='')
      cprint(knamea[1], "green",end='')
    if knamea[1] and sev == 'err':
      cprint('🚨 ' + knamea[0] + '-', "blue",attrs=["bold"], end='')
      cprint(knamea[1], "red", attrs=["bold"],end='')
    if knamea[1] and sev == 'sys':
      cprint(knamea[0] + '-', "blue",attrs=["bold"], end='')
      cprint(knamea[1], "yellow", attrs=["bold"],end='')
  except:
    cprint('parse error ', "magenta", attrs=["bold"], end='')
    print(kname,msg)

  # final output
  print(f': {msg}')

