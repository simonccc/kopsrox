#!/usr/bin/env python3

import os
import common_config as common

# check proxmox config
import proxmox_config

conf = 'kopsrox.ini'
proxmox_conf = 'proxmox.ini'

from configparser import ConfigParser
kopsrox_config = ConfigParser()
proxmox_config = ConfigParser()

# if cluster config exists
if os.path.isfile(conf):

  # read kopsrox.ini
  kopsrox_config.read(conf)
  proxnode = kopsrox_config.get('proxmox', 'proxnode')
#  print('checking proxnode', proxnode)

  prox = common.prox_init()

  vms = prox.nodes.get()

  # set default state
  validated_node='false'
  for i in vms:
   live_node = i.get("node")
   if live_node == proxnode:
       validated_node = proxnode

  if validated_node == 'false':
      print(proxnode, 'node not found - working nodes are:')
      for i in vms:
        print(i.get("node"))

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
