#!/usr/bin/env python3

import os, re, sys
import common_config as common
import kopsrox_ini as ini
import kopsrox_proxmox as proxmox
prox = proxmox.prox_init()

# kopsrox config
conf = common.kopsrox_conf

from configparser import ConfigParser
kopsrox_config = ConfigParser()

# if cluster config exists
if not os.path.isfile(conf):
  ini.init_kopsrox_ini()

# read kopsrox.ini
kopsrox_config.read(conf)

# proxmox -> kopsrox config checks
proxnode = common.conf_check(kopsrox_config,'proxmox','proxnode',conf)
proxstor = common.conf_check(kopsrox_config,'proxmox','proxstor',conf)
proximgid = common.conf_check(kopsrox_config,'proxmox','proximgid',conf)
up_image_url = common.conf_check(kopsrox_config,'proxmox','up_image_url',conf)
proxbridge = common.conf_check(kopsrox_config,'proxmox','proxbridge',conf)

# kopsrox config checks
vm_disk = common.conf_check(kopsrox_config,'kopsrox','vm_disk',conf)
vm_cpu = common.conf_check(kopsrox_config,'kopsrox','vm_cpu',conf)
vm_ram = common.conf_check(kopsrox_config,'kopsrox','vm_ram',conf)

# cloudinit
cloudinituser = common.conf_check(kopsrox_config,'kopsrox','cloudinituser',conf)
cloudinitsshkey = common.conf_check(kopsrox_config,'kopsrox','cloudinitsshkey',conf)

# network
network = common.conf_check(kopsrox_config,'kopsrox','network',conf)
networkgw = common.conf_check(kopsrox_config,'kopsrox','networkgw',conf)

# cluster level checks
masters = common.conf_check(kopsrox_config,'cluster','masters',conf)
workers = common.conf_check(kopsrox_config,'cluster','workers',conf)
k3s_version = common.conf_check(kopsrox_config,'cluster','k3s_version',conf)

# master check - can only be 1 or 3
if not ( (int(masters) == 1) or(int(masters) == 3)):
  print ('ERROR: only 1 or 3 masters supported. You have:', masters)
  exit(0)

# get list of nodes
nodes = prox.nodes.get()
if not (re.search(proxnode, (str(nodes)))):
  print(proxnode, 'node not found - working nodes are:')
  for i in nodes:
    print(i.get("node"))
  exit(0)

# check configured storage on cluster
storage = prox.nodes(proxnode).storage.get()
if not (re.search(proxstor, (str(storage)))):
  print(proxstor, 'storage not found - available storage:')
  for i in storage:
    print(i.get("storage"))
  exit(0)

# check configured bridge on cluster
bridge = prox.nodes(proxnode).network.get()
if not (re.search(proxbridge, (str(bridge)))):
  print(proxbridge, 'bridge not found - available:')
  for i in bridge:
    if i.get("type") == 'bridge':
      print(i.get("iface"))
  exit(0)

# skip image check if image create is passed
try:
  # check for image create command line
  if not ((str(sys.argv[1]) == str('image')) and (str(sys.argv[2]) == str('create'))):
    exit(1)
except:
  kopsrox_img = common.kopsrox_img(proxstor,proximgid)
  images = prox.nodes(proxnode).storage(proxstor).content.get()

  # search the returned list of images
  if not (re.search(kopsrox_img, str(images))):
    print(kopsrox_img, 'not found on '+ proxnode + ':' + proxstor)
    print('run kopsrox image create')
    exit(1)

# check any existing vm's are powered on
for vmid in (proxmox.list_kopsrox_vm()):

  # vm not powered on check
  vmi = common.vm_info(vmid)

  if (( vmi.get('status') == 'stopped') and ( int(vmid) != int(proximgid) )):
    print('WARN: powering on', vmi.get('name'))
    poweron = prox.nodes(proxnode).qemu(vmid).status.start.post()
    proxmox.task_status(prox, str(poweron), proxnode)
