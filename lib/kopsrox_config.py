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

# colors
from termcolor import colored, cprint

# read ini file into config
from configparser import ConfigParser
config = ConfigParser()
config.read('kopsrox.ini')

# kopsrox prompt
def kmsg_prompt():
  cprint(cname, "blue",attrs=["bold"], end='')
  cprint(':', "cyan", end='' )

# print normal output
def kmsg_info(kname, msg):
  kmsg_prompt()
  cprint(kname, "green", end='')
  cprint(': ', "cyan", end='' )
  print(msg)

# print warning
def kmsg_warn(kname, msg):
  kmsg_prompt()
  cprint(kname, "red", attrs=["bold"], end='')
  cprint(': ', "cyan", end='')
  print(msg)

# system lvl
def kmsg_sys(kname, msg):
  kmsg_prompt()
  cprint(kname, "magenta",  attrs=["bold"], end='')
  cprint(': ', "cyan", end='')
  print(msg)

# print error msg
def kmsg_err(kname, msg):
  kmsg_prompt()
  cprint(kname, "red", attrs=["bold"], end='')
  cprint(': ', "cyan", end='' )
  if not msg == '':
    print(msg)

# check section and value exists in kopsrox.ini
def conf_check(section,value):

  # check option exists
  try:
    if not config.has_option(section,value):
      exit()
  except:
    kmsg_err(kname, ('check [' + section + '] \'' + value + '\' in kopsrox.ini'))
    exit()

  try:
    # check value is not blank
    if not (config.get(section, value) == ''):
      # return value
      return(config.get(section, value))
    # value is blank
    exit()
  except:
    kmsg_err(kname, ('check [' + section + '] \'' + value + '\' in kopsrox.ini'))
    exit()

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

# variables for network and its IP for vmip function
octs = network.split('.')
network_base = octs[0] + '.' + octs[1] + '.' + octs[2] + '.'
network_ip = int(octs[-1])

# cluster level checks
cname = conf_check('cluster', 'name')

# master check
masters = int(conf_check('cluster','masters'))
if not (masters == 1 or masters == 3):
  kmsg_err(kname, ('[cluster] - masters: only 1 or 3 masters supported. You have: '+str(masters)))
  exit(0)

# workers
workers = int(conf_check('cluster','workers'))
k3s_version = conf_check('cluster','k3s_version')

# dict of all config items - legacy support
config = ({s:dict(config.items(s)) for s in config.sections()})

# s3 stuff
s3endpoint = config['s3']['endpoint']
access_key = config['s3']['access-key']
access_secret = config['s3']['access-secret']
bucket = config['s3']['bucket']

# region optional
region_string = ''
region = config['s3']['region']
if region:
  region_string = '--etcd-s3-region ' + region

# generated string to use in s3 commands
s3_string = \
' --etcd-s3 ' + region_string + \
' --etcd-s3-endpoint ' + s3endpoint + \
' --etcd-s3-access-key ' + access_key + \
' --etcd-s3-secret-key ' + access_secret + \
' --etcd-s3-bucket ' + bucket + \
' --etcd-s3-skip-ssl-verify '

# define masterid
masterid = proximgid + 1

# define vmnames
vmnames = {
(proximgid): cname +'-i0',
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
    timeout=3)

  # check connection to cluster
  prox.cluster.status.get()

except:
  kmsg_err(kname, ('API connection to ' + endpoint + ':' + port + ' failed check [proxmox] settings'))
  kmsg_sys(kname, prox.cluster.status.get())
  exit()

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
    if (vmid >= proximgid) and (vmid < (proximgid + 10)):
      vmids[vmid] = vm.get('node')

  # return sorted dict
  return(dict(sorted(vmids.items())))

# returns vmstatus
# why does it need node?
def vm_info(vmid,node=proxnode):
  return(prox.nodes(node).qemu(vmid).status.current.get())

# print vminfo
def kmsg_vm_info(vmid, prefix=''):
   vms = list_kopsrox_vm()
   vmid = int(vmid)
   try:
     vmstatus = str(vmid) + ' [' + vms[vmid] + '] ' + vmip(vmid) + '/' + netmask
     kmsg_info((prefix+vmnames[vmid]), vmstatus)
   except:
     kmsg_err('kmsg-vm-info', (vmid, 'id not found', vms))
     exit()

# get list of proxnodes
nodes = [node.get('node', None) for node in prox.nodes.get()]

# if proxnode not in list of nodes
if proxnode not in nodes:
  kmsg_err('config-check', ('proxnode not found. ('+ proxnode + ')'))
  print('valid nodes:')
  for node in nodes:
    print(' - ' + node)
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
  kmsg_err('config-check', ('proxstor not found. (' + proxstor + ')'))
  print('valid storage:')
  for storage in storage_list:
    print(' - ' + storage.get("storage"))
  exit()

# check configured bridge exist or is a sdn vnet
# configured proxbridge does not contain sdn/
if not re.search('sdn/', proxbridge):
  bridges = [bridge.get('iface', None) for bridge in prox.nodes(proxnode).network.get(type = 'bridge')]
else:
  # map zone and get vnets
  sdn_params = proxbridge.split('/')
  zone = sdn_params[1]
  bridges = [bridge.get('vnet', None) for bridge in prox.nodes(proxnode).sdn.zones(zone).content.get()]

  # map proxbridge var to passed vnet
  proxbridge = sdn_params[2]

# check configured bridge is in list
if proxbridge not in bridges:
  kmsg_err('config-check', ('proxbridge not found. (' + proxbridge + ')'))
  print('valid bridges:')
  for bridge in bridges:
    print(' - ' + bridge)
  exit()

# skip image check if image create is passed
try:
  # check for image create command line
  if not (str(sys.argv[1]) == str('image')) and (str(sys.argv[2]) == str('create')):
    # skip to create
    exit()
except:
  try:
    # check for image
    if not kopsrox_img():
      exit()
  except:
    # no image found
    kmsg_err('config-image-check', 'no image run \'kopsrox image create\'')
    exit()

# vm not powered on check
vms = list_kopsrox_vm()
for vmid in vms:

  # skip image
  if vmid != proximgid:

    # map node
    pnode = vms[vmid]

    # get vminfo
    vmi = vm_info(vmid,pnode)

    # start stopped nodes
    if vmi['status'] == 'stopped':
      kmsg_warn('power-on', vmi['name'])
      prox.nodes(pnode).qemu(vmid).status.start.post()

# return ip for vmid
def vmip(vmid):
  vmid = int(vmid)
  # last number of network + ( vmid - proximgid ) 
  # eg 160 + ( 601 - 600 )  = 161 
  ip = network_base + str(network_ip + ( vmid - proximgid))
  return(ip)

# cluster info
def cluster_info():
  kmsg_sys('cluster-info','')

  # for kopsrox vms
  for vmid in list_kopsrox_vm():
    if not proximgid == vmid:
      kmsg_vm_info(vmid)

  from kopsrox_k3s import kubectl
  kmsg_info('k3s-get-nodes', ('\n'+kubectl('get nodes')))
