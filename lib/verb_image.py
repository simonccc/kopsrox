#!/usr/bin/env python3

# functions
from kopsrox_config import prox, kmsg_info, kmsg_warn, kopsrox_img, kmsg_err
kopsrox_img = kopsrox_img()

# variables
from kopsrox_config import proxnode, proxstor, proximgid, up_image_url, proxbridge, cname, cloudinitsshkey, cloudinituser, cloudinitpass, networkgw, network, netmask, storage_type

# general imports
import wget,sys,os,subprocess

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
if cmd == 'create':

  # get image name from url 
  up_image = (up_image_url.split('/')[-1])

  # download image with wget if not present
  if not os.path.isfile(up_image):

    kmsg_info(kname, ('downloading ' + up_image))
    wget.download(up_image_url)
    print()

    # patch image 
    kmsg_info(kname, 'running virt-customize to install qemu-guest-agent')

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
    patch_cmd = 'sudo virt-customize -a ' + up_image + ' --run-command "' + install_qga + '"'

    try: 
      result = subprocess.run(
        ['bash', "-c", patch_cmd], text=True, capture_output=True
      )
      if (result.returncode == 1):
        exit()
    except:
      kmsg_err((kname + '-error'), result)
      exit()

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
    net0 = ('model=virtio,bridge=' + proxbridge),
    boot = 'c',
    name = (cname + '-i0'),
    ostype = 'l26',
    ide2 = (proxstor + ':cloudinit'),
    tags = cname,
    serial0 = 'socket',
    agent = ('enabled=true,fstrim_cloned_disks=1'),
    hotplug = 0,
    ciupgrade = 0,
    description = up_image,
    ciuser = cloudinituser, 
    cipassword = cloudinitpass,
    sshkeys = ssh_encode,
    ipconfig0 = ( 'gw=' + networkgw + ',ip=' + network + '/' + netmask ), 
  ))

  # shell to import disk
  import_cmd = 'sudo qm set ' + str(proximgid) + \
  ' --virtio0 ' + proxstor + ':0,import-from=' + os.getcwd() + '/' + up_image 

  # run shell command to import
  kmsg_info(kname, ('importing '+ up_image + ' to '+ proxstor))

  try:
    result = subprocess.run(
      ['bash', "-c", import_cmd], capture_output=True, text=True
    )
    if (result.returncode == 1):
      exit()
  except:
    kmsg_err((kname + '-error'), result)
    exit()

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

      # get vm info
      notes = prox.nodes(proxnode).qemu(image['vmid']).config.get()

      # created time
      created = str(datetime.fromtimestamp(int(image.get('ctime'))))

      # size in G
      size = str(int(image.get('size') / 1073741824)) + 'G'

      # print image info
      image_info = ('\n' + notes['description'] + '\n' + kopsrox_img + ' ('+ storage_type + ')' + '\ncreated: ' + created + ' size: ' + size )
      kmsg_info('image-info', image_info)

# destroy image
if (cmd == 'destroy'):
  if (kopsrox_img):
    kmsg_warn('image-destroy', ('deleting '+ kopsrox_img))
    destroy(proximgid)
  else:
    kmsg_warn('image-destroy', ('no image found'))
