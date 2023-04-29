#!/usr/bin/env python3

import os
import common_config as common

conf = common.proxmox_conf

# check for config
if not os.path.isfile(conf):
  common.init_proxmox_ini()

# init connection to prox
prox = common.prox_init()

# if unable to get cluster status
if not prox.cluster.status.get():
  print('ERROR: unable to connect -problem in proxmox.ini')
  exit(0)
