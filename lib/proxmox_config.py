#!/usr/bin/env python3
import common_config as common, kopsrox_ini as ini, os

# check for config
if not os.path.isfile(common.proxmox_conf):
  # if file not exists generate and exit
  ini.init_proxmox_ini()

# init connection to prox
prox = common.prox_init()

# if unable to get cluster status
if not prox.cluster.status.get():
  print('ERROR: unable to connect problem in proxmox.ini?')
  exit(0)
