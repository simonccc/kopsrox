#!/usr/bin/env python3

# functions
from kopsrox_config import prox, kmsg_info, kmsg_warn, kopsrox_img, kmsg_err, local_os_process, kmsg_sys, image_info, cloud_image_desc
kopsrox_img = kopsrox_img()

# variables
from kopsrox_config import node, storage, cluster_id, cloud_image_url, network_bridge, cluster_name, cloudinitsshkey, cloudinituser, cloudinitpass, network_gw, network, network_mask, storage_type, network_dns

# general imports
import wget,sys,os

# used to encode ssh key
import urllib.parse

# proxmox functions
from kopsrox_proxmox import task_status, destroy

# define command
cmd = sys.argv[2]
kname = 'image-'+cmd

# create image
if cmd == 'create':

  # get image name from url 
  cloud_image = cloud_image_url.split('/')[-1]
  kmsg_sys(kname, cloud_image)

  # will this always overwrite?
  wget.download(cloud_image_url)
  print()

  # patch image 
  kmsg_info(f'{kname}-virt-customize','installing qemu-guest-agent')

  # script to install qemu-guest-agent on multiple os's disable selinux on Rocky
  install_qga = '''
curl -sfL https://get.k3s.io > /k3s.sh 
if [ ! -f /usr/bin/qemu-ga ] 
then
  if [ -f /bin/yum ]  
  then 
    yum install -y qemu-guest-agent
  else
    apt update && apt install qemu-guest-agent -y 
  fi 
fi  
if [ -f /etc/selinux/config ] 
then
  sed -i s/enforcing/disabled/g /etc/selinux/config
fi 
if [ -f /etc/sysconfig/qemu-ga ]
then
  cp /dev/null /etc/sysconfig/qemu-ga 
fi'''
  patch_cmd = f'sudo virt-customize -a {cloud_image} --run-command "{install_qga}"'
  local_os_process(patch_cmd)

  # destroy template if it exists
  try:
    destroy(cluster_id)
  except:
    pass

  # encode ssh key
  ssh_encode = urllib.parse.quote(cloudinitsshkey, safe='')

  # create new server
  task_status(prox.nodes(node).qemu.post(
    vmid = cluster_id,
    cores = 1,
    memory = 2048,
    cpu = ('cputype=host'),
    scsihw = 'virtio-scsi-pci',
    net0 = (f'model=virtio,bridge={network_bridge}'),
    boot = 'c',
    name = (f'{cluster_name}-i0'),
    ostype = 'l26',
    ide2 = (f'{storage}:cloudinit'),
    tags = cluster_name,
    serial0 = 'socket',
    agent = ('enabled=true,fstrim_cloned_disks=1'),
    hotplug = 0,
    ciupgrade = 0,
    description = cloud_image,
    ciuser = cloudinituser, 
    cipassword = cloudinitpass,
    sshkeys = ssh_encode,
    nameserver = network_dns,
    ipconfig0 = (f'gw={network_gw},ip={network}/{network_mask}'), 
  ))

  # shell to import disk
  import_cmd = f'\
sudo qm set {cluster_id} --virtio0 {storage}:0,import-from={os.getcwd()}/{cloud_image} ; \
mv {cloud_image} {cloud_image}.patched'

  # run shell command to import
  kmsg_info(f'{kname}-qm-import', f'{storage}/{cluster_id}')
  local_os_process(import_cmd)

  # convert to template via create base disk also vm config
  task_status(prox.nodes(node).qemu(cluster_id).template.post())
  task_status(prox.nodes(node).qemu(cluster_id).config.post(template = 1))

# image info
if cmd == 'info':
  image_info()

# destroy image
if cmd == 'destroy':
  # check image exists
  if (kopsrox_img):
    kmsg_sys(kname, f'{kopsrox_img}/{cloud_image_desc}')
    destroy(cluster_id)
  else:
    kmsg_info(kname, 'no image found')
