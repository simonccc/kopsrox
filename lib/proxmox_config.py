#!/usr/bin/env python3

import os
import common_config as common
from proxmoxer import ProxmoxAPI
from configparser import ConfigParser
proxmox_config = ConfigParser()

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

conf = 'proxmox.ini'

# check for config
if os.path.isfile(conf):
  print('validating', conf)

  # read config
  proxmox_config.read(conf)
  endpoint = proxmox_config.get('proxmox', 'endpoint')
  user = proxmox_config.get('proxmox', 'user')
  token_name = proxmox_config.get('proxmox', 'token_name')
  api_key = proxmox_config.get('proxmox', 'api_key')

  # make a test api call to test creds
  prox = ProxmoxAPI(
endpoint,
user=user,
token_name=token_name,
token_value=api_key,
verify_ssl=False,
timeout=10)

  if prox.cluster.status.get():
    print('proxmox access ok')
  else:
    print('problem in proxmox.ini')
    exit(0)
else:
  print(common.kopsrox_prompt, 'no ', conf,  ' found generating...')
  proxmox_config.add_section('proxmox')
  proxmox_config.set('proxmox', 'endpoint', 'domain or ip')
  proxmox_config.set('proxmox', 'user', 'example user eg root@pam')
  proxmox_config.set('proxmox', 'token_name', 'token name')
  proxmox_config.set('proxmox', 'api_key', 'xxxxxxxxxxxxx')
  with open(conf, 'w') as configfile:
    proxmox_config.write(configfile)
  print('Please edit proxmox.ini as required')
  exit(0)
