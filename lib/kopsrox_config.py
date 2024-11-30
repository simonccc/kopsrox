#!/usr/bin/env python3

# external imports
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import urllib.parse
import wget
from datetime import datetime
from proxmoxer import ProxmoxAPI

# look for strings in responses
import re

# checks cmd line args file ops and processes
import os,sys,subprocess

# kmsg
from kopsrox_kmsg import kmsg

# read ini file into config
from configparser import ConfigParser
kopsrox_config = ConfigParser()
kopsrox_config.read('kopsrox.ini')

# kname 
kname='kopsrox_config-check'

# check section and value exists in kopsrox.ini
def conf_check(section,value):

  # check option exists
  try:
    if not kopsrox_config.has_option(section,value):
      exit(0)
  except:
    kmsg(kname, f'[{section}]/{value} is missing','err')
    exit(0)

  # check value is not blank ( s3 section ok ) 
  try:
    if kopsrox_config.get(section, value) == '':
      exit(0)
  except:
    if not section in ['s3']:
      kmsg(kname, f'[{section}]/{value} - a value is required','err')
      exit(0)

  # define config_item
  config_item = kopsrox_config.get(section, value)

  # int check
  if value in ['port', 'vm_cpu', 'vm_ram', 'vm_disk', 'cluster_id', 'workers', 'masters', 'network_mtu']:

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
kname = cluster_name + '_config-check'

# get cluster id
cluster_id = conf_check('cluster','cluster_id')
if cluster_id < 100:
  kmsg(kname, f' cluster_id is too low - should be over 100', 'err')
  exit(0)

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
vm_disk = conf_check('kopsrox','vm_disk')
vm_cpu = conf_check('kopsrox','vm_cpu')
vm_ram = conf_check('kopsrox','vm_ram')

# cloudinit
cloudinituser = conf_check('kopsrox','cloudinituser')
cloudinitpass = conf_check('kopsrox','cloudinitpass')

# check ssh key can be encoded correctly
try:
  cloudinitsshkey = urllib.parse.quote(conf_check('kopsrox','cloudinitsshkey'), safe='')
except:
  kmsg(kname, f'[kopsrox]/cloudinitsshkey - invalid ssh key', 'err')
  exit(0)

# network
network_ip = conf_check('kopsrox','network_ip')
network_gw = conf_check('kopsrox','network_gw')
network_mask = conf_check('kopsrox','network_mask')
network_dns = conf_check('kopsrox', 'network_dns')
network_bridge = conf_check('kopsrox','network_bridge')
network_mtu = conf_check('kopsrox','network_mtu')

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
workers = conf_check('cluster','workers')

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
    timeout=5)

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

# get list of nodes
discovered_nodes = [node.get('node', None) for node in prox.nodes.get()]

# if node not in list of nodes
if node not in discovered_nodes:
  kmsg(kname, f'"{node}" not found - discovered nodes: {discovered_nodes}', 'err')
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
  kmsg(kname, f'"{storage}" not found. discovered storage:', 'err')
  for discovered_storage in storage_list:
    print(' - ' + discovered_storage.get("storage"))
  exit(0)

# check configured bridge exists or is a sdn vnet
# configured bridge does not contain the string 'sdn/'
if not re.search('sdn/', network_bridge):

  # discover available traditional bridges
  discovered_bridges = [bridge.get('iface', None) for bridge in prox.nodes(node).network.get(type = 'bridge')]

# sdn bridges / zones
else:
  # check we can map zone and get vnets
  try:
    sdn_params = network_bridge.split('/')
    if not sdn_params[1] or not sdn_params[2]:
      exit(0)
    else:
      zone = sdn_params[1]
      network_bridge = sdn_params[2]
  except:
    kmsg(kname, f'unable to parse sdn config: "{network_bridge}"', 'err')
    exit(0)

  # discover available sdn bridges
  discovered_bridges = [bridge.get('vnet', None) for bridge in prox.nodes(node).sdn.zones(zone).content.get()]

# check configured bridge is in list
if network_bridge not in discovered_bridges:
  kmsg(kname, f'"{network_bridge}" not found. valid bridges: {discovered_bridges}', 'err')
  exit(0)

# dummy cloud_image_vars overwritten below
cloud_image_size = 0
cloud_image_desc = ''

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

    # assign variable name
    kopsrox_image_name = kopsrox_img()

  except:
    # no image found
    kmsg(kname, f'{cluster_name} image not found - please run "kopsrox image create"', 'err')
    exit(0)

  # get image info
  try:
    cloud_image_data = prox.nodes(node).storage(storage).content(kopsrox_image_name).get()

    # check image not too large for configured disk
    cloud_image_size = int(cloud_image_data['size'] / 1073741824 )
    if cloud_image_size > vm_disk:
      exit(0)

    # get image created and desc from template
    template_data = prox.nodes(node).qemu(cluster_id).config.get()
    cloud_image_desc = template_data['description']

  except:
    kmsg(kname, f'image size ({cloud_image_size}G) is greater than configured vm_disk ({vm_disk}G)', 'err')
    exit(0)

# vm not powered on check
# vms var used in other code now and needs renaming
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
      kmsg(kname, f'powering on {vmi["name"]}', 'sys')
      prox.nodes(pnode).qemu(vmid).status.start.post()

# end of checks
# functions used in other code

# return ip for vmid
def vmip(vmid: int):
  # last number of network + ( vmid - cluster_id ) 
  # eg 160 + ( 601 - 600 )  = 161 
  ip = f'{network_base}{(network_ip_prefix + (vmid - cluster_id))}'
  return(ip)

# cluster info
def cluster_info():
  kmsg(f'cluster_info', '', 'sys')
  from kopsrox_k3s import kubectl, get_kube_vip_master
  curr_master = get_kube_vip_master()
  info_vms = list_kopsrox_vm()

  # for kopsrox vms
  for vmid in info_vms:
    if not cluster_id == vmid:
      hostname = vmnames[vmid]
      vmstatus = f'[{info_vms[vmid]}] {vmip(vmid)}/{network_mask}'
      if hostname == curr_master:
        vmstatus += f' vip {network_ip}/{network_mask}'
      kmsg(f'{hostname}_{vmid}', f'{vmstatus}')

  # fix this 
  kmsg('kubectl_get-nodes', f'\n{kubectl("get nodes")}')

# run local os process 
def local_os_process(cmd):
  try:
    cmd_run = subprocess.run(['bash', "-c", cmd], text=True, capture_output=True)

    # if return code 1 or any stderr
    if (cmd_run.returncode == 1 or cmd_run.stderr != ''):
       exit(0)
  except:
    kmsg('local_os-process-error', f'{cmd_run} - {cmd_run.stderr.strip()}', 'err')
    exit(0)
  return(cmd_run)

# print image info
def image_info():
  kname = f'image_'
  kmsg(f'{kname}desc', cloud_image_desc)
  kmsg(f'{kname}storage', f'{kopsrox_image_name} ({storage_type})')
  kmsg(f'{kname}size', f'{cloud_image_size}G')
