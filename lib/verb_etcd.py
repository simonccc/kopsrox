#!/usr/bin/env python3

# kopsrox
from kopsrox_config import *
from kopsrox_proxmox import *
from kopsrox_k3s import *

# passed command
cmd = sys.argv[2]
kname = f'etcd_{cmd}'

# token filename
token_fname = cluster_name + '.k3stoken'

# check master is running / exists
try:
  node = vms[masterid]
except:
  kmsg(f'{kname}-check', 'cluster does not exist', 'err')
  exit(0)

# run k3s s3 command passed
def s3_run(s3cmd):

  # run the command ( 2>&1 required )
  k3s_run = f'k3s etcd-snapshot {s3cmd} 2>&1'
  cmd_out = qaexec(masterid, k3s_run)

  # look for fatal error in output
  if re.search('level=fatal', cmd_out):
    kmsg(f'{kname}-s3run', f'\n {cmd_out}', 'err')
    exit(0)

  # return command outpit
  return(cmd_out)

# list images in s3 storage
def list_snapshots():

  # run s3 ls and create a list per line
  ls = s3_run('ls').split('\n')

  # images string
  images = ''

  # for each image in the sorted list
  for line in sorted(ls):

    # if cluster name matches the s3 line append to the images string
    if re.search(f'kopsrox-{cluster_name}', line) and re.search('s3', line):
      images += line+'\n'

  # return images string
  return(images.strip())

# test connection to s3 by getting list of snapshots
snapshots = list_snapshots()

try:
  node = vms[masterid]
except:
  kmsg(f'{kname}-check', 'cluster does not exist', 'err')
  exit(0)

# s3 prune
if cmd == 'prune':
  kmsg(f'{kname}-prune', (f'{s3_endpoint}/{bucket}\n' + s3_run('prune --name kopsrox')), 'sys')
  exit(0)

# snapshot 
if cmd == 'snapshot':

  # check for existing token file
  if not os.path.isfile(token_fname):
    export_k3s_token()

  # define snapshot command
  snap_cmd = f'k3s etcd-snapshot save --name kopsrox --etcd s3 2>&1'
  snapout = qaexec(masterid,snap_cmd)

  # filter output
  snapout = snapout.split('\n')
  for line in snapout:
    if re.search('Snapshot', line):
      kmsg(kname, line)

# print s3List
def s3_list():
  kmsg(kname, f'{s3_endpoint}/{bucket}\n{snapshots}')

# restore / list snapshots
if cmd == 'restore' or cmd == 'restore-latest' or cmd == 'list':

  # snapshots must exist
  # fixme - better
  if not snapshots:
    snapshots = 'not found'
    s3_list()
    exit(0)

  # list
  if cmd == 'list':
    s3_list()
    exit(0)

  # restore-latest 
  if cmd == 'restore-latest':
    # generate latest snapshot name
    snapshot = snapshots.split('\n')[-1].split()[0]
  else:
    # assign passed snapshot argument
    snapshot = sys.argv[3]

  # check passed snapshot name exists
  if not re.search(snapshot,snapshots):
    kmsg(kname, f'{snapshot} not found', 'err')
    s3_list()
    exit(0)

  # check token file exists
  if not os.path.isfile(token_fname):
    kmsg(kname, f'{token_fname} not found exiting.', 'err')
    exit(0)

  # get token value
  token = open(token_fname, "r").read()

  # info
  kmsg(kname,f'restoring {snapshot}', 'sys')

  # remove all nodes apart from image and master
  if (workers >= 1 or masters == 3 ):
    k3s_rm_cluster(restore = True)

  # define restore command
  restore_cmd = f'\
systemctl stop k3s &&  \
k3s server --cluster-reset --cluster-reset-restore-path={snapshot} --token={token} 2>&1 ; \
systemctl start k3s'

  # display some filtered restore contents
  restore = qaexec(masterid, restore_cmd)
  for line in restore.split('\n'):

    # if output contains fatal error
    if re.search('level=fatal', line):
      print(line)
      kmsg(kname, 'fatal error', 'err')
      exit(0)

    # filter these lines
    if re.search('level=', line) and not re.search('info', line) \
    and not re.search('json: no such file or directory', line) \
    and not re.search('Cluster CA certificate is trusted by the host CA bundle', line) \
    and not re.search('Bootstrap key already exists', line):
    # else print line as sys
      kmsg(kname, line, 'sys')

  # delete extra nodes in the restored cluster
  nodes = kubectl('get nodes').split()

  # for each of returned nodes from kubectl
  for node in nodes:

    # if matches cluster name and not master node
    if re.search(f'{cluster_name}-', node) and (node != f'{cluster_name}-m1'):
      kmsg(kname, f'removing stale node {node}', 'sys')

      # need to check this..
      kubectl(f'delete node {node}')

  # get restored clusters kubeconfig and token
  kubeconfig()
  export_k3s_token()

  # run k3s update
  k3s_update_cluster()
