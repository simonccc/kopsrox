#!/usr/bin/env python3

import os
# disable insecure warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from proxmoxer import ProxmoxAPI

# check proxmox config
import proxmox_config

conf = 'kopsrox.ini'
proxmox_conf = 'proxmox.ini'

from configparser import ConfigParser
kopsrox_config = ConfigParser()
proxmox_config = ConfigParser()

# if cluster config exists
if os.path.isfile(conf):

  # read proxmox info
  proxmox_config.read(proxmox_conf)
  endpoint = proxmox_config.get('proxmox', 'endpoint')
  user = proxmox_config.get('proxmox', 'user')
  token_name = proxmox_config.get('proxmox', 'token_name')
  api_key = proxmox_config.get('proxmox', 'api_key')

  # read kopsrox.ini
  kopsrox_config.read(conf)
  proxnode = kopsrox_config.get('proxmox', 'proxnode')
  print('checking proxnode', proxnode)

  prox = ProxmoxAPI(
endpoint,
user=user,
token_name=token_name,
token_value=api_key,
verify_ssl=False,
timeout=10)

  vms = prox.nodes.get()
  validated_node='false'
  for i in vms:
   live_node = i.get("node")
   if live_node == proxnode:
       validated_node = proxnode

  if validated_node == 'false':
      print(proxnode, 'node not found - working nodes are:')
      for i in vms:
        print(i.get("node"))



  exit(0)

else:
    print(conf, 'not found')
    kopsrox_config.read(conf)

    # default cluster template:
    kopsrox_config.add_section('proxmox')

    # node to operate on
    kopsrox_config.set('proxmox', 'proxnode', 'proxmox node to work on')

    with open(conf, 'w') as configfile:
      kopsrox_config.write(configfile)

    print('Please edit', conf, 'as required')
    exit(0)

exit(0)
