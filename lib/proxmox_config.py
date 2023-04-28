#!/usr/bin/env python3

import os
import common_config as common

conf = common.proxmox_conf

# check for config
if os.path.isfile(conf):
#  print('proxmox_config: validating', conf)
  prox = common.prox_init()

  if prox.cluster.status.get():
    next
  else:
    print(common.kopsrox_prompt, 'problem in proxmox.ini')
    exit(0)
else:
  print(common.kopsrox_prompt, 'no ', conf,  ' found generating...')
  proxmox_config = ConfigParser()
  proxmox_config.add_section('proxmox')
  proxmox_config.set('proxmox', 'endpoint', 'domain or ip')
  proxmox_config.set('proxmox', 'user', 'example user eg root@pam')
  proxmox_config.set('proxmox', 'token_name', 'token name')
  proxmox_config.set('proxmox', 'api_key', 'xxxxxxxxxxxxx')
  with open(conf, 'w') as configfile:
    proxmox_config.write(configfile)
  print('Please edit proxmox.ini as required')
  exit(0)
