import common_config as common, sys, os, wget, re, time, urllib.parse
verb = 'cluster'
verbs = common.verbs_cluster

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

import proxmox_config as kprox

# import config
(
proxnode,
proxstor,
proximgid,
up_image_url,
proxbridge,
vm_disk_size,
cloudinituser,
cloudinitsshkey,
network,
networkgw,
        ) = common.read_kopsrox_ini()

print(proxnode,proxstor,network)

exit(0)

# generate image name
kopsrox_img = common.kopsrox_img(proxstor,proximgid)

# 
if passed_verb == 'create':
    print('create')
