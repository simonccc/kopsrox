#!/usr/bin/env python3
import common_config as common, sys, os, wget, re, time, urllib.parse

import kopsrox_proxmox as proxmox
prox = proxmox.prox_init()

verb = 'image'
verbs = common.verbs_image

# check for arguments
try:
  if (sys.argv[2]):
    passed_verb = str(sys.argv[2])
except:
  print('ERROR: pass a command')
  print(verb, '', end='')
  common.verbs_help(verbs)
  exit(0)

# unsupported verb
if not passed_verb in verbs:
  print('ERROR:\''+ passed_verb + '\'- command not found')
  print('kopsrox', verb, '', end='')
  common.verbs_help(verbs)

# import config
config = common.read_kopsrox_ini()
proxnode = (config['proxmox']['proxnode'])
proxstor = (config['proxmox']['proxstor'])
proximgid = (config['proxmox']['proximgid'])
up_image_url = (config['proxmox']['up_image_url'])
proxbridge = (config['proxmox']['proxbridge'])
vm_disk = (config['kopsrox']['vm_disk'])
cloudinituser = (config['kopsrox']['cloudinituser'])
cloudinitsshkey = (config['kopsrox']['cloudinitsshkey'])
network = (config['kopsrox']['network'])
networkgw = (config['kopsrox']['networkgw'])
netmask = (config['kopsrox']['netmask'])

# generate image name
kopsrox_img = common.kopsrox_img(proxstor,proximgid)

# create image
if (passed_verb == 'create'):

  # get image name
  up_image = (up_image_url.split('/')[-1])

  # download image with wget if not present
  if not os.path.isfile(up_image):
    print('image::create: downloading:', up_image_url)
    wget.download(up_image_url)
    print('')

    # patch image with qemu-agent
    try:
      print('image::create: patching: ' + up_image)
      imgpatch = os.system('sudo virt-customize -a ' + up_image + ' --install qemu-guest-agent,nfs-common' ' >' + os.getcwd() + '/kopsrox_imgpatch.log 2>&1')
    except:
      print('error patching image')
      exit(0)

  # destroy template if it exists
  try:
    proxmox.destroy(proximgid)
  except:
    next

  # create new server
  create = prox.nodes(proxnode).qemu.post(
          vmid = proximgid,
          scsihw = 'virtio-scsi-pci',
          memory = '2048',
          net0 = ('model=virtio,bridge=' + proxbridge),
          boot = 'c',
          bootdisk = 'virtio0',
          name = 'kopsrox-image',
          ostype = 'l26',
          ide2 = (proxstor + ':cloudinit'),
          tags = 'kopsrox',
          serial0 = 'socket',
          agent = ('enabled=true'),
          hotplug = 0,
          )
  proxmox.task_status(prox, str(create), proxnode)

  # shell to import disk
  import_disk_string = ('sudo qm set ' + proximgid + ' --virtio0 ' + proxstor + ':0,import-from=' + os.getcwd() + '/' + up_image+ ' >' + os.getcwd() + '/kopsrox_disk_import.log 2>&1') 

  #print(import_disk_string)

  # run shell command to import
  try:
    print('image::create: importing: ' + up_image)
    qmimport = os.system(import_disk_string)
  except:
    print('image::create: ERROR importing disk to VM')
    print(qmimport)
    exit(0)

  # resize disk to suitable size
  disc = prox.nodes(proxnode).qemu(proximgid).resize.put(
        disk = 'virtio0',
        size = vm_disk,
        )

  # cloud init
  # url encode ssh key
  ssh_encode = urllib.parse.quote(cloudinitsshkey, safe='')
  cloudinit = prox.nodes(proxnode).qemu(proximgid).config.post(
          ciuser = cloudinituser, 
          cipassword = 'admin', 
          ipconfig0 = ( 'gw=' + networkgw + ',ip=' + network + '/' + netmask ), 
          sshkeys = ssh_encode )
  proxmox.task_status(prox, str(cloudinit), proxnode)

  # power on and off the vm to resize disk
  #print('resizing disk to', vm_disk)
  poweron = prox.nodes(proxnode).qemu(proximgid).status.start.post()
  proxmox.task_status(prox, str(poweron), proxnode)

  # power off
  time.sleep(10)
  poweroff = prox.nodes(proxnode).qemu(proximgid).status.stop.post()
  proxmox.task_status(prox, str(poweroff), proxnode)

  # convert to template via create base disk
  #print('setting base disk')
  set_basedisk = prox.nodes(proxnode).qemu(proximgid).template.post()
  proxmox.task_status(prox, str(set_basedisk), proxnode)

  # set also in vmconfig
  set_template = prox.nodes(proxnode).qemu(proximgid).config.post(
          template = 1)
  proxmox.task_status(prox, str(set_template), proxnode)

# list images on proxstor
if (passed_verb == 'info'):
  images = prox.nodes(proxnode).storage(proxstor).content.get()
  for i in images:
    if i.get('volid') == (kopsrox_img):
      print(i.get('volid'), i.get('ctime'))

# destroy image
if (passed_verb == 'destroy'):
    print('destroying kopsrox image')
    proxmox.destroy(proximgid)
