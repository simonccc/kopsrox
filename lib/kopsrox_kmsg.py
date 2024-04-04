#!/usr/bin/env python3

# import
from termcolor import cprint

# kmsg
def kmsg(kname = 'kopsrox',msg = 'no msg', sev = 'info'):

  try:
    from kopsrox_config import cluster_name
    cprint(cluster_name, "blue",attrs=["bold"], end='')
  except:
    cprint('kopsrox', "blue",attrs=["bold"], end='')
  cprint('::', "cyan", end='' )

  if sev == 'info':
    cprint(kname, "green", end='')

  if sev == 'err':
    cprint(kname, "red", attrs=["bold"], end='')

  cprint(':: ', "cyan", end='')

  print(msg)
