#!/usr/bin/env python3

# functions
from kopsrox_config import prox, local_os_process, image_info, cloud_image_desc, kopsrox_img

# variables
from kopsrox_config import node, storage, cluster_id, cloud_image_url, cluster_name, cloudinitsshkey, cloudinituser, cloudinitpass

# general imports
import wget,sys,os

# proxmox functions
from kopsrox_proxmox import task_status, prox_destroy

# kmsg
from kopsrox_kmsg import kmsg

# define command
cmd = sys.argv[2]
kname = 'image_'+cmd

# create image
if cmd == 'create':

  # get image name from url 
  cloud_image = cloud_image_url.split('/')[-1]
  kmsg(kname, f'[{cluster_name}] creating new image based on {cloud_image}', 'sys')

  # check img can be downloaded
  try:
    wget.download(cloud_image_url)
    print()
  except:
    kmsg(kname, f'unable to download {cloud_image_url}', 'err')
    exit(0)

  # patch image 
  kmsg(f'{kname}', 'installing qemu-guest-agent')

  # script to install qemu-guest-agent on multiple os's disable selinux on Rocky
  install_qga = '''
curl -sfL https://get.k3s.io > /k3s.sh 
export INSTALL_K3S_SKIP_ENABLE=true
export INSTALL_K3S_SKIP_SELINUX_RPM=true
bash /k3s.sh 
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
  patch_out = local_os_process(patch_cmd)

  # destroy template if it exists
  try:
    prox_destroy(cluster_id)
  except:
    pass

  # create new server
  task_status(prox.nodes(node).qemu.post(
    vmid = cluster_id,
    cores = 1,
    memory = 1024,
    cpu = ('cputype=host'),
    scsihw = 'virtio-scsi-single',
    boot = 'c',
    name = (f'{cluster_name}-i0'),
    ostype = 'l26',
    ide2 = (f'{storage}:cloudinit'),
    tags = cluster_name,
    serial0 = 'socket',
    agent = ('enabled=true'),
    hotplug = 0,
    ciupgrade = 0,
    description = cloud_image,
    ciuser = cloudinituser, 
    cipassword = cloudinitpass,
    sshkeys = cloudinitsshkey,
  ))

  # shell to import disk
  import_cmd = f'\
sudo qm set {cluster_id} --scsi0 {storage}:0,import-from={os.getcwd()}/{cloud_image},iothread=true,aio=native,discard=on,ssd=1 ; \
mv {cloud_image} {cloud_image}.patched'

  # run shell command to import
  kmsg(f'{kname}', f'qm import to {storage}/{cluster_id}')
  local_os_process(import_cmd)

  # convert to template via create base disk also vm config
  task_status(prox.nodes(node).qemu(cluster_id).template.post())
  task_status(prox.nodes(node).qemu(cluster_id).config.post(template = 1))

# image info
if cmd == 'info':
  image_info()

# destroy image
if cmd == 'destroy':
   kmsg(kname, f'{kopsrox_img()}/{cloud_image_desc}', 'warn')
   prox_destroy(cluster_id)
