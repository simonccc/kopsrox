#!/usr/bin/env python3

import os, re
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
  proxstor = common.conf_check(kopsrox_config,'proxmox','proxstor',conf)

  #print('checking proxnode', proxnode)

  # get list of nodes
  nodes = kprox.prox.nodes.get()
  if not (re.search(proxnode, (str(nodes)))):
    print(proxnode, 'node not found - working nodes are:')
    for i in nodes:
      print(i.get("node"))
    exit(0)

  # get storage on proxnode
  storage = kprox.prox.nodes(proxnode).storage.get()
  if not (re.search(proxstor, (str(storage)))):
    print(proxstor, 'storage not found - available storage:')
    for i in storage:
      print(i.get("storage"))
    exit(0)

else:
    print(conf, 'not found')
    kopsrox_config.read(conf)

    # default cluster template:
    kopsrox_config.add_section('proxmox')

    # node to operate on
    kopsrox_config.set('proxmox', 'proxnode', 'proxmox')

    # storage on node
    kopsrox_config.set('proxmox', 'proxstor', 'local')

    # write default config
    with open(conf, 'w') as configfile:
      kopsrox_config.write(configfile)

    print('Please edit', conf, 'as required')
    exit(0)
