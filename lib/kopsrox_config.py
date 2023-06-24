#!/usr/bin/env python3

import os, re, sys
import kopsrox_ini as ini

# skip check for config example.ini
try:
  if ((str(sys.argv[1]) == str('config')) and (str(sys.argv[2]) == str('example.ini'))):
    print('config::example.ini: generating')
    try:
      os.remove('example.ini')
    except:
      next
    ini.init_kopsrox_ini(conf = 'example.ini')
except:
  next

# generate barebones kopsrox.ini if it doesn't exist
conf = ini.conf
if not os.path.isfile(conf):
  ini.init_kopsrox_ini()
  exit(0)

from configparser import ConfigParser
config = ConfigParser()

# read ini files
config.read(conf)

# check value
def conf_check(section,value):
  try:
    return(config.get(section, value))
  except:
    print('kopsrox::conf_check: ERROR: no value found for ' + section + ':' + value + ' in ' + conf)
    exit(0)

# proxmox checks
endpoint = conf_check('proxmox','endpoint')
user = conf_check('proxmox','user')
token_name = conf_check('proxmox','token_name')
api_key = conf_check('proxmox','api_key')

# proxmox -> kopsrox config checks
proxnode = conf_check('proxmox','proxnode')
proxstor = conf_check('proxmox','proxstor')
proximgid = conf_check('proxmox','proximgid')
up_image_url = conf_check('proxmox','up_image_url')
proxbridge = conf_check('proxmox','proxbridge')

# kopsrox config checks
vm_disk = conf_check('kopsrox','vm_disk')
vm_cpu = conf_check('kopsrox','vm_cpu')
vm_ram = conf_check('kopsrox','vm_ram')

# cloudinit
cloudinituser = conf_check('kopsrox','cloudinituser')
cloudinitpass = conf_check('kopsrox','cloudinitpass')
cloudinitsshkey = conf_check('kopsrox','cloudinitsshkey')

# network
network = conf_check('kopsrox','network')
networkgw = conf_check('kopsrox','networkgw')
netmask = conf_check('kopsrox','netmask')

# cluster level checks
masters = conf_check('cluster','masters')
workers = conf_check('cluster','workers')
k3s_version = conf_check('cluster','k3s_version')

# s3
s3_endpoint = conf_check('s3','endpoint')
s3_key = conf_check('s3','access-key')
s3_secret = conf_check('s3','access-secret')
s3_bucket = conf_check('s3','bucket')

# safe to import these now ( has to be this order ) 
import kopsrox_proxmox as proxmox
import common_config as common

# master check - can only be 1 or 3
if not ( (int(masters) == 1) or(int(masters) == 3)):
  print ('ERROR: only 1 or 3 masters supported. You have:', masters)
  exit(0)

# check connection to proxmox
prox = proxmox.prox_init()
# if unable to get cluster status
if not prox.cluster.status.get():
  print('ERROR: unable to connect to proxmox - check proxmox.ini')
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
    exit(0)

# check any existing vm's are powered on
for vmid in (proxmox.list_kopsrox_vm()):

  # vm not powered on check
  vmi = proxmox.vm_info(vmid)

  # power on all nodes aside from image
  if (( vmi.get('status') == 'stopped') and ( int(vmid) != int(proximgid) )):
    print('WARN: powering on', vmi.get('name'))
    poweron = prox.nodes(proxnode).qemu(vmid).status.start.post()
    proxmox.task_status(prox, str(poweron), proxnode)
