#!/usr/bin/env python3

# general imports
import common_config as common, sys, os, wget, re, time

# used to convert timestamps
from datetime import datetime

# used to encode ssh key
import urllib.parse

# import values from kopsrox_config
import kopsrox_config as kopsrox_config

# proxmox connection
import kopsrox_proxmox as proxmox
prox = proxmox.prox_init()

# handle image sub commands
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

# map common config values
proxnode = kopsrox_config.proxnode
proxstor = kopsrox_config.proxstor
proximgid = kopsrox_config.proximgid

# generate image name
kopsrox_img = proxmox.kopsrox_img(proxstor,proximgid)

# create image
if (passed_verb == 'create'):

  # get image name
  up_image = (kopsrox_config.up_image_url.split('/')[-1])

  # download image with wget if not present
  if not os.path.isfile(up_image):
    print('image::create: downloading:', up_image)
    wget.download(kopsrox_config.up_image_url)
    print('')

    # define image patch command
    log = ' >> kopsrox_imgpatch.log 2>&1'

    # define virt-customize command
    virtc_cmd = 'sudo virt-customize -a ' + up_image

    # install qemu-guest-agent
    qa_patch = virtc_cmd + ' --install qemu-guest-agent,nfs-common' + log

    # install k3s 
    k3s_install  = virtc_cmd  + ' --run-command "curl -sfL https://get.k3s.io > /k3s.sh"' + log 
    k3s_patch = virtc_cmd  + ' --run-command "cat /k3s.sh | INSTALL_K3S_SKIP_ENABLE=true INSTALL_K3S_VERSION="' + kopsrox_config.k3s_version + '" sh -"' + log 
    # resize image with vm_disk size from config
    resize_patch = 'sudo qemu-img resize ' + up_image + ' ' + kopsrox_config.vm_disk + log

    # generate the final patch command
    patch_cmd = (qa_patch + ' && ' + k3s_install + ' && ' + k3s_patch + ' && ' + resize_patch)

    #print(patch_cmd)

    # patch image 
    try:
      print('image::create: patching: ' + up_image)
      imgpatch = os.system(patch_cmd)
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
  import_disk_string = ('sudo qm set ' + proximgid + ' --ciupgrade 0 --virtio0 ' + proxstor + ':0,import-from=' + os.getcwd() + '/' + up_image+ ' >' + os.getcwd() + '/kopsrox_disk_import.log 2>&1') 

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
        size = kopsrox_config.vm_disk,
        )

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
if (passed_verb == 'info'):

  # get list of images
  for image in prox.nodes(proxnode).storage(proxstor).content.get():

    # if image matches our generated image name
    if image.get('volid') == (kopsrox_img):

      # created time
      created = str(datetime.fromtimestamp(image.get('ctime')))

      # size in G
      size = str(int(image.get('size') / 1073741824)) + 'G'

      # print image info
      print(kopsrox_img + ' ('+ kopsrox_config.storage_type + ')' + ' created: ' + created + ' size: ' + size)

# destroy image
if (passed_verb == 'destroy'):
  print('image::destroy: destroying image', kopsrox_img)
  proxmox.destroy(proximgid)
