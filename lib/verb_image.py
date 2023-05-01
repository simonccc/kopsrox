import common_config as common, sys, os, wget, re, time, urllib.parse
verb = 'image'
verbs = common.verbs_image

# check for arguments
try:
  if (sys.argv[2]):
    passed_verb = str(sys.argv[2])
except:
  print(verb)
  common.verbs_help(verbs)
  exit(0)

# unsupported verb
if not passed_verb in verbs:
  print(verb)
  print('ERROR:\''+ passed_verb + '\'- command not found')
  common.verbs_help(verbs)

# import config
from configparser import ConfigParser
kopsrox_config = ConfigParser()
import proxmox_config as kprox

# read values from config
kopsrox_config.read(common.kopsrox_conf)
proxnode = kopsrox_config.get('proxmox', 'proxnode')
proxstor = kopsrox_config.get('proxmox', 'proxstor')
proximgid = kopsrox_config.get('proxmox', 'proximgid')
up_image_url = kopsrox_config.get('proxmox', 'up_image_url')
proxbridge = kopsrox_config.get('proxmox', 'proxbridge')

# kopsrox lvl
vm_disk_size = kopsrox_config.get('kopsrox', 'vm_disk_size')
cloudinituser = kopsrox_config.get('kopsrox', 'cloudinituser')
cloudinitsshkey = kopsrox_config.get('kopsrox', 'cloudinitsshkey')
network = kopsrox_config.get('kopsrox', 'network')
networkgw = kopsrox_config.get('kopsrox', 'networkgw')

# generate image name
kopsrox_img = common.kopsrox_img(proxstor,proximgid)

# create image
if (passed_verb == 'create'):

  # get image name
  up_image = (up_image_url.split('/')[-1])

  # check to see if already present
  if not os.path.isfile(up_image):
    print('Downloading:', up_image_url)
    wget.download(up_image_url)

  # destroy old image server if it exists
  try:
    poweroff = kprox.prox.nodes(proxnode).qemu(proximgid).status.stop.post()
    common.task_status(kprox.prox, poweroff, proxnode)
    delete = kprox.prox.nodes(proxnode).qemu(proximgid).delete()
    common.task_status(kprox.prox, delete, proxnode)
  except:
    next

  # create new server
  print('create vm')
  create = kprox.prox.nodes(proxnode).qemu.post(
          vmid = proximgid,
          scsihw = 'virtio-scsi-pci',
          memory = '2048',
          net0 = ('model=virtio,bridge=' + proxbridge),
          boot = 'c',
          bootdisk = 'scsi0',
          name = 'kopsrox-image',
          ostype = 'l26',
          ide2 = (proxstor + ':cloudinit')
          )
  common.task_status(kprox.prox, str(create), proxnode)

  import_disk_string = ('sudo qm set ' + proximgid + ' --scsi0 ' + proxstor + ':0,import-from=' + os.getcwd() + '/' + up_image+ ' >' + os.getcwd() + '/kopsrox_disk_import.log 2>&1') 

  #print(import_disk_string)

  # run shell command to import
  try:
    print('importimg disk')
    qmimport = os.system(import_disk_string)
  except:
    print('error importing disk to VM')
    exit(0)

  # resize disk to suitable size
  print('resizing disk')
  disc = kprox.prox.nodes(proxnode).qemu(proximgid).resize.put(
        disk = 'scsi0',
        size = vm_disk_size,
        )

  # cloud init
  print('cloud init')

  # url encode ssh key
  ssh_encode = urllib.parse.quote(cloudinitsshkey, safe='')
  cloudinit = kprox.prox.nodes(proxnode).qemu(proximgid).config.post(
          ciuser = cloudinituser, 
          cipassword = 'admin', 
          ipconfig0 = ( 'gw=' + networkgw + ',ip=' + network + '/32' ), 
          sshkeys = ssh_encode )
  common.task_status(kprox.prox, str(cloudinit), proxnode)

  # power on and off the vm to resize disk
  print('powering on')
  poweron = kprox.prox.nodes(proxnode).qemu(proximgid).status.start.post()
  common.task_status(kprox.prox, str(poweron), proxnode)

  print('sleeping 10 for disk resize')
  time.sleep(10)

  print('poweroff')
  poweroff = kprox.prox.nodes(proxnode).qemu(proximgid).status.stop.post()
  common.task_status(kprox.prox, str(poweroff), proxnode)

  print('powering on')
  poweron = kprox.prox.nodes(proxnode).qemu(proximgid).status.start.post()
  common.task_status(kprox.prox, str(poweron), proxnode)


  exit(0)

# list images on proxstor
if (passed_verb == 'list'):
  images = kprox.prox.nodes(proxnode).storage(proxstor).content.get()
  for i in images:
    print(i.get('volid'))
