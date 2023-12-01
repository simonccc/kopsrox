#!/usr/bin/env python3

# functions
from kopsrox_config import prox, kmsg_info, kmsg_warn,kopsrox_img
kopsrox_img = kopsrox_img()

# variables
from kopsrox_config import proxnode, proxstor, proximgid, up_image_url, proxbridge, cname, cloudinitsshkey, cloudinituser, cloudinitpass, networkgw, network, netmask, storage_type

# general imports
import wget,sys, os, subprocess

# used to convert timestamps
from datetime import datetime

# used to encode ssh key
import urllib.parse

# proxmox functions
from kopsrox_proxmox import task_status, destroy

# define command
cmd = sys.argv[2]
kname = 'image-'+cmd

# create image
if (cmd == 'create'):

  # get image name
  up_image = (up_image_url.split('/')[-1])

  # download image with wget if not present
  if not os.path.isfile(up_image):

    kmsg_info(kname, ('downloading ' + up_image))
    wget.download(up_image_url)
    print('')

    # patch image 
    kmsg_info(kname, 'running virt-customize')
    patch_cmd = 'sudo virt-customize -a ' + up_image + \
    ' --install qemu-guest-agent,nfs-common --run-command "curl -sfL https://get.k3s.io > /k3s.sh"'

    try: 
      result = subprocess.run(
        ['bash', "-c", patch_cmd], capture_output=True, text=True
      )
    except:
      kmsg_err(kname, result)
      exit()

  # destroy template if it exists
  try:
    destroy(proximgid)
  except:
    next

  # create new server
  create = prox.nodes(proxnode).qemu.post(
    vmid = proximgid,
    scsihw = 'virtio-scsi-pci',
    memory = '1024',
    net0 = ('model=virtio,bridge=' + proxbridge),
    boot = 'c',
    bootdisk = 'virtio0',
    name = ( cname + '-image'),
    ostype = 'l26',
    ide2 = (proxstor + ':cloudinit'),
    tags = cname,
    serial0 = 'socket',
    agent = ('enabled=true'),
    hotplug = 0,
  )
  task_status(create)

  # shell to import disk
  import_cmd = 'sudo qm set ' + str(proximgid) + \
  ' --ciupgrade 0 --virtio0 ' + proxstor + ':0,import-from=' + os.getcwd() + '/' + up_image 

  # run shell command to import
  kmsg_info(kname, ('importing '+ up_image + ' to '+ proxstor))

  try:
    result = subprocess.run(
      ['bash', "-c", import_cmd], capture_output=True, text=True
    )
  except:
    kmsg_err(kname, result)
    exit()

  # url encode ssh key for cloudinit
  ssh_encode = urllib.parse.quote(cloudinitsshkey, safe='')

  # cloud init user setup
  cloudinit = prox.nodes(proxnode).qemu(proximgid).config.post(
    ciuser = cloudinituser, 
    cipassword = cloudinitpass,
    ipconfig0 = ( 'gw=' + networkgw + ',ip=' + network + '/' + netmask ), 
    sshkeys = ssh_encode 
  )
  task_status(cloudinit)

  # convert to template via create base disk
  set_basedisk = prox.nodes(proxnode).qemu(proximgid).template.post()
  task_status(set_basedisk)

  # set also in vmconfig
  set_template = prox.nodes(proxnode).qemu(proximgid).config.post(template = 1)
  task_status(set_template)

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
      image_info = (kopsrox_img + ' ('+ storage_type + ')' + ' created: ' + created + ' size: ' + size)
      kmsg_info('image-info', image_info)

# destroy image
if (cmd == 'destroy'):
  kmsg_warn('image-destroy', ('deleting '+ kopsrox_img))
  destroy(proximgid)
