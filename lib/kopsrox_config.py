#!/usr/bin/env python3

# imports
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from proxmoxer import ProxmoxAPI

# prompt
kname = 'config'

# look for strings in responses
import re

# checks cmd line args - could be moved?
import sys
from termcolor import colored, cprint

# read ini file into config
from configparser import ConfigParser
config = ConfigParser()
config.read('kopsrox.ini')

# kopsrox prompt
def kmsg_prompt():
    cprint('kopsrox', "blue",attrs=["bold"], end='')
    cprint('::', "cyan", end='' )

# print normal output
def kmsg_info(kname, msg):
    kmsg_prompt()
    cprint(kname, "green", end='')
    cprint(':: ', "cyan", end='' )
    print(msg)

# print warning
def kmsg_warn(kname, msg):
    kmsg_prompt()
    cprint(kname, "red", attrs=["bold"], end='')
    cprint(':: ', "cyan", end='')
    print(msg)

# print error msg
def kmsg_err(kname, msg):
    kmsg_prompt()
    cprint(kname, "yellow", attrs=["bold"], end='')
    cprint('::', "cyan", end='' )
    cprint('ERROR', "red", attrs=["bold"])
    print('-',msg)

# check section and value exists in kopsrox.ini
def conf_check(section,value):
  try:
    # check value is not blank
    if not (config.get(section, value) == ''):
      # return value
      return(config.get(section, value))
    # value is blank
    exit(0)
  except:
    kmsg_err(kname, ('check [' + section + '] \'' + value + '\' in kopsrox.ini'))
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

# master check
masters = int(conf_check('cluster','masters'))
if not ((masters == 1) or (masters == 3)):
  kmsg_err(kname, ('[cluster] - masters: only 1 or 3 masters supported. You have: '+str(masters)))
  exit(0)

# workers
workers = int(conf_check('cluster','workers'))
k3s_version = conf_check('cluster','k3s_version')

# dict of all config items - legacy support
config = ({s:dict(config.items(s)) for s in config.sections()})

# define masterid
masterid = int((proximgid) + 1)

# define vmnames
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

# proxmox api connection
try: 

  # api connection
  prox = ProxmoxAPI(
    endpoint,
    port=port,
    user=user,
    token_name=token_name,
    token_value=api_key,
    verify_ssl=False,
    timeout=5)

  # check connection to cluster
  prox.cluster.status.get()
except:
  kmsg_err(kname, 'API connection failed check [proxmox] settings in kopsrox.ini')
  exit(0)

# look up kopsrox_img name
def kopsrox_img():

  # list contents
  for image in prox.nodes(proxnode).storage(proxstor).content.get():

    # map image_name
    image_name = image.get("volid")

    # if 123-disk-0 found in volid
    if re.search((str(proximgid) + '-disk-0'), image_name):
      return(image_name)

  # unable to find image name
  return False

# return dict of kopsrox vms by node
def list_kopsrox_vm():

  # init dict
  vmids = {}

  # get all vms running on proxmox
  for vm in prox.cluster.resources.get(type = 'vm'):

    # map id
    vmid = int(vm.get('vmid'))

    # if vmid is in kopsrox config range ie between proximgid and proximgid + 10
    # add vmid and node to dict
    if ((vmid >= proximgid) and (vmid < (proximgid + 10))):
      vmids[vmid] = vm.get('node')

  # return sorted dict
  return(dict(sorted(vmids.items())))

# returns vmstatus
def vm_info(vmid,node):
  return(prox.nodes(node).qemu(vmid).status.current.get())

# get list of proxnodes
nodes = [node.get('node', None) for node in prox.nodes.get()]

# if proxnode not in list of nodes
if proxnode not in nodes:
  kmsg_err('config-check', ('proxnode listed in kopsrox.ini not found. ('+ proxnode + ')'))
  # print list of discovered proxmox nodes
  print('- valid proxnodes:')
  for node in nodes:
    print(' * ' + node)
  exit()

# get list of storage in the cluster
storage_list = prox.nodes(proxnode).storage.get()

# for each of the list 
for storage in storage_list:

  # if matched proxstor
  if proxstor == storage.get("storage"):

    # is storage local or shared?
    if storage.get("shared") == 0:
      storage_type = 'local'
    else: 
      storage_type = 'shared'

# if no storage_type we have no matched storage
try:
  if storage_type:
    pass
except:
  kmsg_err('config-check', ('proxstor listed in kopsrox.ini not found. (' + proxstor + ')'))

  # print available storage
  print('- valid proxstor:')
  for storage in storage_list:
    print(' * ' + storage.get("storage"))
  exit()

# check configured bridge on cluster
bridges = [bridge.get('iface', None) for bridge in prox.nodes(proxnode).network.get(type = 'bridge')]

# check configured bridge is in list
if proxbridge not in bridges:
  kmsg_err('config-check', ('proxbridge listed in kopsrox.ini not found. (' + proxbridge + ')'))
  print('- valid bridges:')
  for bridge in bridges:
    print(' * ' + bridge)
  exit()

# skip image check if image create is passed
try:
  # check for image create command line
  if not ((str(sys.argv[1]) == str('image')) and (str(sys.argv[2]) == str('create'))):
    # skip to create
    exit(0)
except:
  try:
    # check for image
    if not kopsrox_img():
      exit()
  except:
    # no image found
    kmsg_err('config-image-check', 'no image run \'kopsrox image create\'')
    exit()

# get dict of vms
vms = list_kopsrox_vm()
for vmid in vms:

  # map node
  proxnode = vms[vmid]

  # vm not powered on check
  vmi = vm_info(vmid,proxnode)

  # power on all nodes aside from image
  if (( vmi.get('status') == 'stopped') and ( int(vmid) != int(proximgid) )):
    print('WARN: powering on', vmi.get('name'))
    poweron = prox.nodes(proxnode).qemu(vmid).status.start.post()
    exit(0)

# return ip for vmid
def vmip(vmid):
  network_octs = network.split('.')
  basenetwork = ( network_octs[0] + '.' + network_octs[1] + '.' + network_octs[2] + '.' )

  # generate the last ip
  ip = basenetwork + str(int(network_octs[-1]) + ( int(vmid) - int(proximgid)))
  return(ip)

# legacy function
def vmname(vmid):
    vmid = int(vmid)
    return(vmnames[vmid])

# cluster info
def cluster_info():
  # map dict of ids and node
  vms = list_kopsrox_vm()

  # for kopsrox vms
  for vmid in vms:

    # get vm status
    node = vms[vmid]
    v_info = vm_info(vmid,node)

    # vars
    vmname = v_info.get('name')
    vmstatus = v_info.get('status')
    ip = vmip(vmid)

    # print
    print(str(vmid) + ' ['+  vmstatus + '] ' + ip + '/' + netmask +' [' + node + '] ' + vmname)

  from kopsrox_k3s import kubectl
  print(kubectl('get nodes'))
