#!/usr/bin/env python3

import os, re, sys
import common_config as common

# proxmox init
import proxmox_config as kprox

# kopsrox config
conf = common.kopsrox_conf

from configparser import ConfigParser
kopsrox_config = ConfigParser()

# if cluster config exists
if not os.path.isfile(conf):
  common.init_kopsrox_ini()

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

#print('checking proxnode', proxnode)

# get list of nodes
nodes = kprox.prox.nodes.get()
if not (re.search(proxnode, (str(nodes)))):
  print(proxnode, 'node not found - working nodes are:')
  for i in nodes:
    print(i.get("node"))
  exit(0)

# check configured storage on cluster
storage = kprox.prox.nodes(proxnode).storage.get()
if not (re.search(proxstor, (str(storage)))):
  print(proxstor, 'storage not found - available storage:')
  for i in storage:
    print(i.get("storage"))
  exit(0)

# check configured bridge on cluster
bridge = kprox.prox.nodes(proxnode).network.get()
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

  # define name of expected kopsrox_img
  kopsrox_img = common.kopsrox_img(proxstor,proximgid)

  # get images listed on server to look for the kopsrox one
  images = kprox.prox.nodes(proxnode).storage(proxstor).content.get()

  # search the returned list of images
  if not (re.search(kopsrox_img, str(images))):
    print(kopsrox_img, 'not found on '+ proxnode + ':' + proxstor)
    print('run kopsrox image create')
    exit(1)
