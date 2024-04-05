#!/usr/bin/env python3

# imports
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# proxmoxer api
from proxmoxer import ProxmoxAPI

# prompt
kname = 'config-check'

# look for strings in responses
import re

# checks cmd line args - could be moved?
import sys

# local os commands
import subprocess

# datetime stuff for generating image date
from datetime import datetime

# colors
from termcolor import colored, cprint
from kopsrox_kmsg import kmsg

# read ini file into config
from configparser import ConfigParser
kopsrox_config = ConfigParser()
kopsrox_config.read('kopsrox.ini')

# kopsrox prompt
def kmsg_prompt():

  # needs to have cluster name defined
  try:
    cprint(cluster_name, "blue",attrs=["bold"], end='')
    cprint(':', "cyan", end='' )
  except:
    pass

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
    if not kopsrox_config.has_option(section,value):
      exit()
  except:
    kmsg(kname, f'[{section}]/{value} is missing','err')
    exit()

  # check value is not blank ( s3 section ok ) 
  try:
    if kopsrox_config.get(section, value) == '':
      exit()
  except:
    if not section in ['s3']:
      kmsg(kname, f'[{section}]/{value} - a value is required','err')
      exit()

  # define config_item
  config_item = kopsrox_config.get(section, value)

  # int check
  if value in ['port', 'vm_cpu', 'vm_ram', 'vm_disk', 'cluster_id', 'workers', 'masters']:

    # test if var is int
    try:
      test_var = int(config_item)
    except:
      kmsg(kname, f'[{section}]/{value} should be numeric: {config_item}', 'err')
      exit(0)

    # return int
    return(kopsrox_config.getint(section, value))
  else:
    # return string
    return(config_item)

# check config vars
# cluster name as required for error messages
cluster_name = conf_check('cluster', 'cluster_name')

# get cluster id
cluster_id = conf_check('cluster','cluster_id')

# proxmox
prox_endpoint = conf_check('proxmox','prox_endpoint')
port = conf_check('proxmox','port')
user = conf_check('proxmox','user')
token_name = conf_check('proxmox','token_name')
api_key = conf_check('proxmox','api_key')
node = conf_check('proxmox','node')
storage = conf_check('proxmox','storage')

# kopsrox config checks
cloud_image_url = conf_check('kopsrox','cloud_image_url')
vm_disk = int(conf_check('kopsrox','vm_disk'))
vm_cpu = int(conf_check('kopsrox','vm_cpu'))
vm_ram = int(conf_check('kopsrox','vm_ram'))

# cloudinit
cloudinituser = conf_check('kopsrox','cloudinituser')
cloudinitpass = conf_check('kopsrox','cloudinitpass')
cloudinitsshkey = conf_check('kopsrox','cloudinitsshkey')

# network
network_ip = conf_check('kopsrox','network_ip')
network_gw = conf_check('kopsrox','network_gw')
network_mask = conf_check('kopsrox','network_mask')
network_dns = conf_check('kopsrox', 'network_dns')
network_bridge = conf_check('kopsrox','network_bridge')

# variables for network and its IP for vmip function
network_octs = network_ip.split('.')
network_base = f'{network_octs[0]}.{network_octs[1]}.{network_octs[2]}.'
network_ip_prefix = int(network_octs[-1])

# master + check
masters = conf_check('cluster','masters')
if not (masters == 1 or masters == 3):
  kmsg(kname, f'[cluster] - masters: only 1 or 3 masters supported. You have: {masters}')
  exit(0)

# workers
workers = int(conf_check('cluster','workers'))

# k3s version
k3s_version = conf_check('cluster','k3s_version')

# s3 stuff
s3endpoint = conf_check('s3','endpoint')
access_key = conf_check('s3','access-key')
access_secret = conf_check('s3','access-secret')
bucket = conf_check('s3','bucket')

# region optional
region_string = ''
region = conf_check('s3','region')
if region:
  region_string = '--etcd-s3-region ' + region

# dict of all config items - legacy support
config = ({s:dict(kopsrox_config.items(s)) for s in kopsrox_config.sections()})

# generated string to use in s3 commands
s3_string = \
' --etcd-s3 ' + region_string + \
' --etcd-s3-endpoint ' + s3endpoint + \
' --etcd-s3-access-key ' + access_key + \
' --etcd-s3-secret-key ' + access_secret + \
' --etcd-s3-bucket ' + bucket + \
' --etcd-s3-skip-ssl-verify '

# define masterid
masterid = cluster_id + 1

# define vmnames
vmnames = {
(cluster_id): cluster_name +'-i0',
(cluster_id + 1 ): cluster_name + '-m1',
(cluster_id + 2 ): cluster_name + '-m2',
(cluster_id + 3 ): cluster_name + '-m3',
(cluster_id + 4 ): cluster_name + '-u1',
(cluster_id + 5 ): cluster_name + '-w1',
(cluster_id + 6 ): cluster_name + '-w2',
(cluster_id + 7 ): cluster_name + '-w3',
(cluster_id + 8 ): cluster_name + '-w4',
(cluster_id + 9 ): cluster_name + '-w5',
}

# proxmox api connection
try: 

  # api connection
  prox = ProxmoxAPI(
    prox_endpoint,
    port=port,
    user=user,
    token_name=token_name,
    token_value=api_key,
    verify_ssl=False,
    timeout=3)

  # check connection to cluster
  prox.cluster.status.get()

except:
  kmsg(kname, f'API connection to {prox_endpoint}:{port} failed check [proxmox] settings', 'err')

  # this could be improved
  #kmsg(kname, prox.cluster.status.get(), 'sys')
  exit()

# look up kopsrox_img name
def kopsrox_img():

  # list contents
  for image in prox.nodes(node).storage(storage).content.get():

    # map image_name
    image_name = image.get("volid")

    # if 123-disk-0 found in volid
    if re.search(f'{cluster_id}-disk-0', image_name):
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

    # if vmid is in kopsrox config range ie between cluster_id and cluster_id + 10
    # add vmid and node to dict
    if (vmid >= cluster_id) and (vmid < (cluster_id + 10)):
      vmids[vmid] = vm.get('node')

  # return sorted dict
  return(dict(sorted(vmids.items())))

# returns vmstatus
# why does it need node?
def vm_info(vmid,node=node):
  return(prox.nodes(node).qemu(vmid).status.current.get())

# print vminfo
def kmsg_vm_info(vmid):
   vms = list_kopsrox_vm()
   vmid = int(vmid)
   try:
     vmstatus = f'{vmid} [{vms[vmid]}] {vmip(vmid)}/{network_mask}'
     kmsg(kname,f'{vmnames[vmid]} - {vmstatus}', 'info')
   except:
     kmsg(kname, f'kmsg-vm-info {vmid} id not found', 'err')
     print(vms)
     exit()

# get list of nodes
nodes = [node.get('node', None) for node in prox.nodes.get()]

# if node not in list of nodes
if node not in nodes:
  kmsg_err('config-check', ('node not found. ('+ node + ')'))
  print('valid nodes:')
  for node in nodes:
    print(' - ' + node)
  exit()

# get list of storage in the cluster
storage_list = prox.nodes(node).storage.get()

# for each of the list 
for local_storage in storage_list:

  # if matched storage
  if storage == local_storage.get("storage"):

    # is storage local or shared?
    if local_storage.get("shared") == 0:
      storage_type = 'local'
    else: 
      storage_type = 'shared'

# if no storage_type we have no matched storage
try:
  if storage_type:
    pass
except:
  kmsg_err('config-check', ('storage not found. (' + storage + ')'))
  print('valid storage:')
  for storage in storage_list:
    print(' - ' + storage.get("storage"))
  exit()

# check configured bridge exist or is a sdn vnet
# configured bridge does not contain sdn/
if not re.search('sdn/', network_bridge):
  bridges = [bridge.get('iface', None) for bridge in prox.nodes(node).network.get(type = 'bridge')]
else:
  # map zone and get vnets
  sdn_params = network_bridge.split('/')
  zone = sdn_params[1]
  bridges = [bridge.get('vnet', None) for bridge in prox.nodes(node).sdn.zones(zone).content.get()]

  # map network_bridge var to passed vnet
  network_bridge = sdn_params[2]

# check configured bridge is in list
if network_bridge not in bridges:
  kmsg_err('config-check', ('network_bridge not found. (' + network_bridge + ')'))
  print('valid bridges:')
  for bridge in bridges:
    print(' - ' + bridge)
  exit()

# dummy cloud_image_vars overwritten below
cloud_image_size = 0
cloud_image_desc = ''
cloud_image_created = ''

# skip image check if image create is passed
try:
  # check for image create command line
  if sys.argv[1] == 'image' and sys.argv[2] == 'create':
    pass
  else:
    exit(0)

# image checks
except:

  # check image exists
  try:
    # exit if image does not exist
    if not kopsrox_img():
      exit(0)
  except:
    # no image found
    kmsg_err('config-image-check', 'no image run \'kopsrox image create\'')
    exit(0)

  # get image info
  try:
    cloud_image_data = prox.nodes(node).storage(storage).content(kopsrox_img()).get()

    # check image not too large for configured disk
    cloud_image_size = int(cloud_image_data['size'] / 1073741824 )
    if cloud_image_size > vm_disk:
      exit(0)

    # get image created and desc from template
    template_data = prox.nodes(node).qemu(cluster_id).config.get()
    cloud_image_created = str(datetime.fromtimestamp(int(template_data['meta'].split(',')[1].split('=')[1])))
    cloud_image_desc = template_data['description']

  except:
    kmsg_err('config-image-check', 'image size greater than configured vm_disk')
    exit(0)

# vm not powered on check
vms = list_kopsrox_vm()
for vmid in vms:

  # skip image
  if vmid != cluster_id:

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
  # last number of network + ( vmid - cluster_id ) 
  # eg 160 + ( 601 - 600 )  = 161 
  ip = f'{network_base}{(network_ip_prefix + (vmid - cluster_id))}'
  return(ip)

# cluster info
def cluster_info():
  kmsg_sys('cluster-info', f'{cluster_name} {cloud_image_desc}')

  # for kopsrox vms
  for vmid in list_kopsrox_vm():
    if not cluster_id == vmid:
      kmsg_vm_info(vmid)

  from kopsrox_k3s import kubectl
  kmsg_info('k3s-get-nodes', ('\n'+kubectl('get nodes')))

# run local os process 
def local_os_process(cmd):
  try:
    cmd_run = subprocess.run(['bash', "-c", cmd], text=True, capture_output=True)
    if (cmd_run.returncode == 1):
       exit()
  except:
    kmsg_err('local_os_process-error',cmd_run)
    exit()
  return(cmd_run)

# print image info
def image_info():
  kmsg_sys('image-info', 'displaying image info')
  kmsg_info('image-desc', cloud_image_desc)
  kmsg_info('image-storage', (kopsrox_img() + ' ('+ storage_type + ')'))
  kmsg_info('image-created', cloud_image_created)
  kmsg_info('image-size', (str(cloud_image_size)+'G'))
