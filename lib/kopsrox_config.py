#!/usr/bin/env python3

# prompt
kname = 'kopsrox::config::'

# look for strings in responses
import re

# checks cmd line args - could be moved?
import sys

# read ini file into config
from configparser import ConfigParser
config = ConfigParser()
config.read('kopsrox.ini')

# check section and value exists
def conf_check(section,value):
  try:
    # check value is not blank
    if not (config.get(section, value) == ''):
      # return value
      return(config.get(section, value))
    # value is blank
    exit(0)
  except:
    print(kname + 'conf_check: ERROR! check [' + section + '] \'' + value + '\' in ' + ini.conf)
    exit(0)

# proxmox checks
endpoint = conf_check('proxmox','endpoint')
port = conf_check('proxmox','port')
user = conf_check('proxmox','user')
token_name = conf_check('proxmox','token_name')
api_key = conf_check('proxmox','api_key')

# proxmox -> kopsrox config checks
proxnode = conf_check('proxmox','proxnode')
proxstor = conf_check('proxmox','proxstor')
proximgid = int(conf_check('proxmox','proximgid'))
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
cname = conf_check('cluster', 'name')
masters = int(conf_check('cluster','masters'))
workers = int(conf_check('cluster','workers'))
k3s_version = conf_check('cluster','k3s_version')

# dict of all config items - legacy support
config = ({s:dict(config.items(s)) for s in config.sections()})

# returns masterid ported from common config
def get_master_id():
  return(int(proximgid) + 1)

# safe to import these now ( has to be this order ) 
import kopsrox_proxmox as proxmox
prox = proxmox.prox

# master check - can only be 1 or 3
if not ( (masters == 1) or (masters == 3)):
  print (kname +' ERROR! only 1 or 3 masters supported. You have:', masters)
  exit(0)

# if unable to get cluster status from api
if not prox.cluster.status.get():
  print(kname + 'ERROR: unable to connect to proxmox')
  exit(0)

# get list of nodes
nodes = prox.nodes.get()

# if proxnode not in listed nodes
if not re.search(proxnode, str(nodes)):
  print(proxnode, 'kopsrox::config: ERROR!' + proxnode + ' not found - working nodes are:')

  # print list of discovered proxmox nodes
  for node in nodes:
    print(node.get("node"))

  exit(0)

# get list of storage in the cluster
storage_list = prox.nodes(proxnode).storage.get()

# for each of the list 
for storage in storage_list:

  # if matched proxstor
  if proxstor == storage.get("storage"):

    # is storage local or shared?
    if storage.get("shared") == "0":
      storage_type = 'local'
    else: 
      storage_type = 'shared'

# if no storage_type we have no matched storage
try:
  if storage_type:
    pass
except:
  print('kopsrox::config:', proxstor, 'storage not found - available storage:')

  # print available storage
  for storage in storage_list:
    print(storage.get("storage"))
  exit(0)

# if storage is shared we can launch on other nodes
# to be used later on
#print(proxstor, storage_type)

# check configured bridge on cluster
bridge = str(prox.nodes(proxnode).network.get())

# check configured bridge is in list
if not re.search(proxbridge, bridge):
  print(proxbridge, 'bridge not found - available:')
  for i in bridge:
    if i.get("type") == 'bridge':
      print(i.get("iface"))
  exit(0)

# skip image check if image create is passed
try:
  # check for image create command line
  if not ((str(sys.argv[1]) == str('image')) and (str(sys.argv[2]) == str('create'))):

    # skip to create
    exit(0)
except:

  # look for existing image
  kopsrox_img = proxmox.kopsrox_img(proxstor,proximgid)

  # if no image returned
  if kopsrox_img == 'no image':
    print(kname + ' ERROR: no image found - run kopsrox image create')
    exit(0)

  images = prox.nodes(proxnode).storage(proxstor).content.get()

  # search the returned list of images
  if not (re.search(kopsrox_img, str(images))):
    print('kopsrox::config:', kopsrox_img, 'not found on '+ proxnode + ':' + proxstor)
    print('run kopsrox image create')
    exit(0)

# get dict of vms
vms = proxmox.list_kopsrox_vm()
for vmid in vms:

  # map node
  proxnode = vms[vmid]

  # vm not powered on check
  vmi = proxmox.vm_info(vmid,proxnode)

  # power on all nodes aside from image
  if (( vmi.get('status') == 'stopped') and ( int(vmid) != int(proximgid) )):
    print('WARN: powering on', vmi.get('name'))
    poweron = prox.nodes(proxnode).qemu(vmid).status.start.post()
    proxmox.task_status(prox, str(poweron), proxnode)

# return ip for vmid
def vmip(vmid):
  network_octs = network.split('.')
  basenetwork = ( network_octs[0] + '.' + network_octs[1] + '.' + network_octs[2] + '.' )

  # generate the last ip
  ip = basenetwork + str(int(network_octs[-1]) + ( int(vmid) - int(proximgid)))
  return(ip)

# return the vname for an id
vmnames = {
(proximgid): cname +'-image',
(proximgid + 1 ): cname + '-m1',
(proximgid + 2 ): cname + '-m2',
(proximgid + 3 ): cname + '-m3',
(proximgid + 4 ): cname + '-u1',
(proximgid + 5 ): cname + '-w1',
(proximgid + 6 ): cname + '-w2',
(proximgid + 7 ): cname + '-w3',
(proximgid + 8 ): cname + '-w4',
(proximgid + 9 ): cname + '-w5',
}

# legacy function
def vmname(vmid):
    vmid = int(vmid)
    return(vmnames[vmid])
