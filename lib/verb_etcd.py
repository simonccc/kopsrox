#!/usr/bin/env python3
import kopsrox_config as kopsrox_config
import common_config as common, sys, re, os

# verb config
verb = 'etcd'
verbs = common.verbs_etcd

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
  print('ERROR: \''+ passed_verb + '\'- unknown command')
  print('kopsrox', verb, '', end='')
  common.verbs_help(verbs)


import kopsrox_proxmox as proxmox
import kopsrox_k3s as k3s

# should check for an existing token?
# writes a etcd snapshot token from the current running clusters token
def write_token():
    # get the snapshot tokenfile
    token = common.get_token()

    # add a line break to the token
    token = token + '\n'

    # write the token
    with open('kopsrox.etcd.snapshot.token', 'w') as snapshot_token:
      snapshot_token.write(token)
    print("etcd::write-token: wrote kopsrox.etcd.snapshot.token")

# check for number of nodes
config = common.read_kopsrox_ini()

# count of master nodes ( 1 or 3 ) 
masters = int(config['cluster']['masters'])

# cluster name
cname = config['cluster']['name']

# s3 details
endpoint = config['s3']['endpoint']
access_key = config['s3']['access-key']
access_secret = config['s3']['access-secret']
bucket = config['s3']['bucket']

# region optional
region_string = ''
region = config['s3']['region']
if region:
  region_string = '--etcd-s3-region ' + region

# generated string to use in s3 commands
s3_string = \
' --etcd-s3 ' + region_string + \
' --etcd-s3-endpoint ' + endpoint + \
' --etcd-s3-access-key ' + access_key + \
' --etcd-s3-secret-key ' + access_secret + \
' --etcd-s3-bucket ' + bucket + \
' --etcd-s3-skip-ssl-verify '

# get masterid
masterid = common.get_master_id()

# check master is running / exists
try:
  # fails if node can't be found
  proxmox.get_node(masterid)
except:
  proxmox.get_node(masterid)
  print('etcd::check: ERROR: cluster not found')
  exit(0)

# run k3s s3 command passed
def s3_run(cmd):

  # run the command ( 2>&1 required )
  k3s_run = 'k3s etcd-snapshot ' + cmd + s3_string + '2>&1'
  cmd_out = proxmox.qaexec(masterid, k3s_run)

  # look for fatal error in output
  if re.search('level=fatal', cmd_out):
    print('etcd::s3_run: problem with s3 config')
    print(cmd_out)
    exit(0)

  # the response from qaexec for eg timeout
  if ( cmd_out == 'no output'):
    print('etcd::s3_run: problem with s3 ( no output ) ')
    exit(0)

  # return command outpit
  return(cmd_out)

# test connection to s3 by running ls 
s3_run('ls')

# list images in s3 storage
def list_images():

  # run s3 ls and create a list per line
  ls = s3_run('ls').split('\n')

  # images string
  images = ''

  # for each image in the sorted list
  for line in sorted(ls):

    # if image name matches the line append to the images string
    if re.search((cname + '-' + cname), line):
      images += line + '\n'

  # return images string
  return(images)

# s3 prune
# fixme uses hard coded name
if passed_verb == 'prune':
  print(s3_run('prune --name kopsrox'))
  exit(0)

# snapshot 
if passed_verb == 'snapshot':
  print('etcd::snapshot: running')

  # define snapshot command
  snap_cmd = 'k3s etcd-snapshot save ' + s3_string + ' --name kopsrox'
  #print(snap_cmd)
  snapout = proxmox.qaexec(masterid,snap_cmd)

  # fixme check contents of snapout?

  # filter output
  snapout = snapout.split('\n')
  for line in snapout:
    if re.search('S3', line):
     print(line)
  print('etcd::snapshot: done')

  # check for existing token file
  if not os.path.isfile('kopsrox.etcd.snapshot.token'):
    write_token()

# print returned images
if ( passed_verb == 'list' ):
  print('etcd::list:',endpoint, bucket)
  print(list_images())

# minio etcd snapshot restore
if passed_verb == 'restore':

  # get list of images 
  images = list_images()

  # look for passed snapshot
  try:
    if (sys.argv[3]):
      snapshot = str(sys.argv[3])
  except:
    print('etcd::restore: error pass a snapshot name eg:')
    print(images)
    exit(0)

  # check passed snapshot name exists
  if not (re.search(str(snapshot),str(images))):
    print('etcd::restore: no snapshot found:', snapshot)
    print(images)
    exit(0)

  print('etcd::restore: downsizing cluster for restore')
  k3s.k3s_rm_cluster(restore = True)

  print('etcd::restore: restoring', snapshot)
  write_token = proxmox.writefile(masterid, 'kopsrox.etcd.snapshot.token', '/var/tmp/kopsrox.etcd.snapshot.token')

  # define restore command
  restore_cmd = 'systemctl stop k3s && rm -rf /var/lib/rancher/k3s/server/db/ && k3s server --cluster-reset --cluster-reset-restore-path=' + snapshot +' --token-file=/var/tmp/kopsrox.etcd.snapshot.token ' + s3_string

  print('etcd::restore: restoring please wait')
  restore = proxmox.qaexec(masterid, restore_cmd)

  # needs to be filtered like snapshot
  print(restore)
  print('etcd::restore: starting k3s')
  start = proxmox.qaexec(masterid, 'systemctl start k3s')
  print('etcd::restore: started')

  # delete extra nodes in the restored cluster
  nodes = common.kubectl(masterid, 'get nodes').split()
  for node in nodes:
    if ( re.search((cname + '-i'), node) and (node != ( cname + '-m1'))):
      print('etcd::restore:: removing stale node', node)
      common.kubectl(masterid,'delete node ' + node)

  # run k3s update?
  k3s.k3s_update_cluster()
