#!/usr/bin/env python3

# functions
from kopsrox_config import prox, kmsg_info, kmsg_warn, kopsrox_img, kmsg_err, local_os_process, kmsg_sys, image_info
kopsrox_img = kopsrox_img()

# variables
from kopsrox_config import proxnode, proxstor, proximgid, cloud_image_url, network_bridge, cname, cloudinitsshkey, cloudinituser, cloudinitpass, network_gw, network, network_mask, storage_type, network_dns

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
  cloud_image = (cloud_image_url.split('/')[-1])

  # download image with wget if not present
  if not os.path.isfile(cloud_image):

    kmsg_info((kname+'-downloading'), cloud_image)
    wget.download(cloud_image_url)
    print()

    # patch image 
    kmsg_info((kname+'-virt-customize'), 'installing qemu-guest-agent')

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
    patch_cmd = 'sudo virt-customize -a ' + cloud_image + ' --run-command "' + install_qga + '"'
    local_os_process(patch_cmd)

  # destroy template if it exists
  try:
    destroy(proximgid)
  except:
    next

  # encode ssh key
  ssh_encode = urllib.parse.quote(cloudinitsshkey, safe='')

  # create new server
  task_status(prox.nodes(proxnode).qemu.post(
    vmid = proximgid,
    cores = 1,
    memory = 2048,
    cpu = ('cputype=host'),
    scsihw = 'virtio-scsi-pci',
    net0 = ('model=virtio,bridge=' + network_bridge),
    boot = 'c',
    name = (cname + '-i0'),
    ostype = 'l26',
    ide2 = (proxstor + ':cloudinit'),
    tags = cname,
    serial0 = 'socket',
    agent = ('enabled=true,fstrim_cloned_disks=1'),
    hotplug = 0,
    ciupgrade = 0,
    description = cloud_image,
    ciuser = cloudinituser, 
    cipassword = cloudinitpass,
    sshkeys = ssh_encode,
    nameserver = network_dns,
    ipconfig0 = ( 'gw=' + network_gw + ',ip=' + network + '/' + network_mask ), 
  ))

  # shell to import disk
  import_cmd = 'sudo qm set ' + str(proximgid) + \
  ' --virtio0 ' + proxstor + ':0,import-from=' + os.getcwd() + '/' + cloud_image + ' ; mv ' + cloud_image + ' ' + cloud_image + '.patched'

  # run shell command to import
  kmsg_info((kname+'-qm-import'), (proxstor + '/' + str(proximgid)))
  local_os_process(import_cmd)

  # convert to template via create base disk
  set_basedisk = prox.nodes(proxnode).qemu(proximgid).template.post()
  task_status(set_basedisk)

  # set also in vmconfig
  set_template = prox.nodes(proxnode).qemu(proximgid).config.post(template = 1)
  task_status(set_template)

# image info
if cmd == 'info':
  image_info()

# destroy image
if cmd == 'destroy':
  if (kopsrox_img):
    kmsg_warn('image-destroy', kopsrox_img)
    destroy(proximgid)
  else:
    kmsg_info('image-destroy', 'no image found')
