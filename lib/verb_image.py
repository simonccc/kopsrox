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
  except:
    next

  print('creating')
  create = kprox.prox.nodes(proxnode).qemu.post(vmid = proximgid)
  disc = kprox.prox.nodes(proxnode).qemu(proximgid).config.post()



# list images on proxstor
if (passed_verb == 'list'):
  images = kprox.prox.nodes(proxnode).storage(proxstor).content.get()
  for i in images:
    print(i.get('volid'))
