#!/usr/bin/env python3

import os
import common_config as common

# proxmox init
import proxmox_config as kprox

# kopsrox config
conf = common.kopsrox_conf

from configparser import ConfigParser
kopsrox_config = ConfigParser()

# if cluster config exists
if os.path.isfile(conf):

  # read kopsrox.ini
  kopsrox_config.read(conf)

  # config checks
  proxnode = common.conf_check(kopsrox_config,'proxmox','proxnode',conf)
  proxstore = common.conf_check(kopsrox_config,'proxmox','proxstor',conf)

  print('checking proxnode', proxnode)

  # get list of nodes
  nodes = kprox.prox.nodes.get()

  # set default state
  validated_node='false'
  for i in nodes:
   live_node = i.get("node")
   if live_node == proxnode:
       validated_node = proxnode

  if validated_node == 'false':
      print(proxnode, 'node not found - working nodes are:')
      for i in nodes:
        print(i.get("node"))
      exit(0)

else:
    print(conf, 'not found')
    kopsrox_config.read(conf)

    # default cluster template:
    kopsrox_config.add_section('proxmox')

    # node to operate on
    kopsrox_config.set('proxmox', 'proxnode', 'proxmox node to work on')

    # storage on node
    kopsrox_config.set('proxmox', 'proxstor', 'proxmox node storage to work on')

    with open(conf, 'w') as configfile:
      kopsrox_config.write(configfile)

    print('Please edit', conf, 'as required')
    exit(0)
