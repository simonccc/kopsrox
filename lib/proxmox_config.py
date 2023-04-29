#!/usr/bin/env python3

import os
import common_config as common

# check for config
if not os.path.isfile(common.proxmox_conf):
  # if file not exists generate and exit
  common.init_proxmox_ini()

# init connection to prox
prox = common.prox_init()

# if unable to get cluster status
if not prox.cluster.status.get():
  print('ERROR: unable to connect -problem in proxmox.ini')
  exit(0)

# get current tasks
tasklist = prox.cluster.tasks.get()
for tasks in tasklist:
  if (tasks.get("status") == 'RUNNING'):
    print(tasks)

