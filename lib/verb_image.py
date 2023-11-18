#!/usr/bin/env python3

import kopsrox_config as kopsrox_config
from kopsrox_config import kmsg_info

# general imports
import wget, re, time
import sys, os, subprocess

# used to convert timestamps
from datetime import datetime

# used to encode ssh key
import urllib.parse

# proxmox connection
import kopsrox_proxmox as proxmox
prox = kopsrox_config.prox

# map config values
proxnode = kopsrox_config.proxnode
proxstor = kopsrox_config.proxstor
proximgid = kopsrox_config.proximgid

# generate image name
kopsrox_img = kopsrox_config.kopsrox_img()

# define command
cmd = sys.argv[2]
kname = 'image-'+cmd

# create image
if (cmd == 'create'):

  # get image name
  up_image = (kopsrox_config.up_image_url.split('/')[-1])

  # download image with wget if not present
  if not os.path.isfile(up_image):

    kmsg_info(kname, ('downloading: ' + up_image))
    wget.download(kopsrox_config.up_image_url)
    print('')

    # patch image 
    kmsg_info(kname, ('patching: ' + up_image))
    patch_cmd = 'sudo virt-customize -a ' + up_image + ' --install qemu-guest-agent,nfs-common --run-command "curl -sfL https://get.k3s.io > /k3s.sh"'

    result = subprocess.run(
      ['bash', "-c", patch_cmd], capture_output=True, text=True
    )

    # resize image with vm_disk size from config
    #resize_patch = 'sudo qemu-img resize ' + up_image + ' ' + kopsrox_config.vm_disk 

  # destroy template if it exists
  try:
    proxmox.destroy(proximgid)
  except:
    next

  # create new server
  create = prox.nodes(proxnode).qemu.post(
          vmid = proximgid,
          scsihw = 'virtio-scsi-pci',
          memory = '1024',
          net0 = ('model=virtio,bridge=' + kopsrox_config.proxbridge),
          boot = 'c',
          bootdisk = 'virtio0',
          name = ( kopsrox_config.cname + '-image'),
          ostype = 'l26',
          ide2 = (proxstor + ':cloudinit'),
          tags = kopsrox_config.cname,
          serial0 = 'socket',
          agent = ('enabled=true'),
          hotplug = 0,
          )
  proxmox.task_status(prox, str(create), proxnode)

  # shell to import disk
  cwd = os.getcwd()
  import_cmd = 'sudo qm set ' + str(proximgid) + ' --ciupgrade 0 --virtio0 ' + proxstor + ':0,import-from=' + cwd + '/' + up_image 
  # run shell command to import
  kmsg_info(kname, ('importing '+up_image))
  result = subprocess.run(
    ['bash', "-c", import_cmd], capture_output=True, text=True
  )

  # resize disk to suitable size
  disc = prox.nodes(proxnode).qemu(proximgid).resize.put(
        disk = 'virtio0',
        size = kopsrox_config.vm_disk,
        )
  proxmox.task_status(prox, str(disc), proxnode)

  # url encode ssh key for cloudinit
  ssh_encode = urllib.parse.quote(kopsrox_config.cloudinitsshkey, safe='')

  # cloud init user setup
  cloudinit = prox.nodes(proxnode).qemu(proximgid).config.post(
          ciuser = kopsrox_config.cloudinituser, 
          cipassword = kopsrox_config.cloudinitpass,
          ipconfig0 = ( 'gw=' + kopsrox_config.networkgw + ',ip=' + kopsrox_config.network + '/' + kopsrox_config.netmask ), 
          sshkeys = ssh_encode )
  proxmox.task_status(prox, str(cloudinit), proxnode)

  # convert to template via create base disk
  set_basedisk = prox.nodes(proxnode).qemu(proximgid).template.post()
  proxmox.task_status(prox, str(set_basedisk), proxnode)

  # set also in vmconfig
  set_template = prox.nodes(proxnode).qemu(proximgid).config.post(template = 1)
  proxmox.task_status(prox, str(set_template), proxnode)

# list images on proxstor
# this might be more useful if we allow different images in the future
# cos at the moment will only print 1 image 
if (cmd == 'info'):

  # get list of images
  for image in prox.nodes(proxnode).storage(proxstor).content.get():

    # if image matches our generated image name
    if image.get('volid') == (kopsrox_img):

      # created time
      created = str(datetime.fromtimestamp(int(image.get('ctime'))))

      # size in G
      size = str(int(image.get('size') / 1073741824)) + 'G'

      # print image info
      print(kopsrox_img + ' ('+ kopsrox_config.storage_type + ')' + ' created: ' + created + ' size: ' + size)

# destroy image
if (cmd == 'destroy'):
  print('kopsrox:image::destroy:', kopsrox_img)
  proxmox.destroy(proximgid)
