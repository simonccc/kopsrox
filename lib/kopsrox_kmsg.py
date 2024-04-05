#!/usr/bin/env python3

# import
from termcolor import cprint

# kmsg
def kmsg(kname = 'kopsrox',msg = 'no msg', sev = 'info'):

  # kname parts
  kname_parts = kname.split('_')

  # print cluster name
  cprint(kname_parts[0], "blue",attrs=["bold"], end='')
  cprint(':', "cyan", end='' )

  try:
    if kname_parts[1] and sev == 'info':
      cprint(kname_parts[1], "green", end='')
    if kname_parts[1] and sev == 'err':
      cprint(kname_parts[1], "red", attrs=["bold"],end='')
    if kname_parts[1] and sev == 'sys':
      cprint(kname_parts[1], "magenta", attrs=["bold"],end='')
    if kname_parts[1] and sev == 'warn':
      cprint(kname_parts[1], "yellow", end='')
  except:
      cprint('parse error', "yellow", end='')

  # final output
  cprint(': ', "cyan", end='')
  print(msg)
