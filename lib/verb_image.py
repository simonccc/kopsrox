import common_config as common, sys, os, wget
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
    delete = kprox.prox.nodes(proxnode).qemu(proximgid).delete()
    common.basic_blocking_task_status(kprox.prox, delete, proxnode)
    print(delete, 'deleted old vm')
  except:
    next

  print('creating')
  create = kprox.prox.nodes(proxnode).qemu.post(
          vmid = proximgid,
          scsihw = 'virtio-scsi-pci',
          memory = '2048',
          net0 = 'model=virtio,bridge=vmbr0',
          )
  common.basic_blocking_task_status(kprox.prox, str(create), proxnode)

  # import disk
  disc = kprox.prox.nodes(proxnode).qemu(proximgid).config.post(
        vmid = proximgid,
        scsi0 = (proxstor + ':0,import-from=lenny_sata_nfs:iso/kopsrox-img.iso',)
        )
  common.basic_blocking_task_status(kprox.prox, str(disc), proxnode)

# list images on proxstor
if (passed_verb == 'list'):
  images = kprox.prox.nodes(proxnode).storage(proxstor).content.get()
  for i in images:
    print(i.get('volid'))
