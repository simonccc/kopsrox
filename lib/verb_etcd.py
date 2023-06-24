#!/usr/bin/env python3
import common_config as common, sys, re, base64, os
import kopsrox_proxmox as proxmox

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
  print('ERROR:\''+ passed_verb + '\'- command not found')
  print('kopsrox', verb, '', end='')
  common.verbs_help(verbs)

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
masters = config['cluster']['masters']

# get masterid
masterid = common.get_master_id()

# snapshot 
if passed_verb == 'snapshot':

  # need to check status of minio / bucket
  print('etcd::snapshot: running on kopsrox-m1 '+'('+ str(masterid)+')')

  # run the command to take snapshot
  snapout = proxmox.qaexec(masterid, 'k3s etcd-snapshot --etcd-s3 --etcd-s3-endpoint 192.168.0.164:9000 --etcd-s3-access-key minio --etcd-s3-secret-key miniostorage --etcd-s3-bucket kopsrox --etcd-s3-skip-ssl-verify --name kopsrox')

  # now also need to figure out what to do with the token
  print('etcd::snapshot: done')

  # check for existing token file
  if not os.path.isfile('kopsrox.etcd.snapshot.token'):
    write_token()

# list images on storage
def list_images():
  # need to check status of minio / bucket
  # run the command to ls ( 2>1 required ) 
  return(proxmox.qaexec(masterid, 'k3s etcd-snapshot ls --etcd-s3 --etcd-s3-endpoint 192.168.0.164:9000 --etcd-s3-access-key minio --etcd-s3-secret-key miniostorage --etcd-s3-bucket kopsrox --etcd-s3-skip-ssl-verify 2>1 | grep kopsrox-k | sort'))

# print returned images
if passed_verb == 'list':
  print('etcd::list:')
  print(list_images())

# local snapshot
if passed_verb == 'local-snapshot':
  print('etcd::local-snapshot: kopsrox-m1 '+'('+ str(masterid)+')')

  # run the command to take snapshot
  snapout = proxmox.qaexec(masterid, 'k3s etcd-snapshot --etcd-snapshot-compress --name kopsrox')

  # get path of snapshot from output 
  for line in snapout.split():
    # in path in output line
    if (re.search('path', line)):
      # split the line with output by :
      rpath = line.split(':')

  # remove extra chars and add .zip
  path = (rpath[8].replace('}', '').replace('"', '') + '.zip')
  print('etcd::local-snapshot:', path, 'created')

  # qaexec needs commands to have output ( the echo ok ) 
  b64cmd = ('base64 ' + path + ' > ' + ( path + '.b64' ) + ' && echo ok')
  b64 = proxmox.qaexec(masterid, b64cmd)

  # try qagent file get 
  # this will break when the file gets too large
  get_file = proxmox.getfile(masterid, str((path + '.b64')))

  # encode the already b64 file
  contentb64 = get_file.encode()

  # write the snapshot
  with open('kopsrox.etcd.snapshot.zip', 'wb') as snapshot:
    snapshot.write(base64.b64decode(contentb64))
  print("etcd::local-snapshot: wrote kopsrox.etcd.snapshot.zip")

  # write token if doesn't exist
  if not os.path.isfile('kopsrox.etcd.snapshot.token'):
    write_token()

# minio etcd snapshot restore
if passed_verb == 'restore':

  # need to check for minio availability
  print("etcd::restore: starting")
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

  print('etcd::restore: restoring', snapshot)

  # single master restore
  if ( int(masters) == 1 ):
    write_token = proxmox.writefile(masterid, 'kopsrox.etcd.snapshot.token')

    restore_cmd = 'systemctl stop k3s && rm -rf /var/lib/rancher/k3s/server/db/ && k3s server --cluster-reset --cluster-reset-restore-path=' + snapshot +' --token-file=/var/tmp/kopsrox.etcd.snapshot.token --etcd-s3 --etcd-s3-bucket=kopsrox --etcd-s3-access-key=minio  --etcd-s3-secret-key=miniostorage --etcd-s3-endpoint 192.168.0.164:9000 --etcd-s3-skip-ssl-verify && systemctl start k3s'

    #print(restore_cmd)
    print('etcd::restore: restoring please wait')
    restore = proxmox.qaexec(masterid, restore_cmd)
    print(restore)
    print(common.kubectl(masterid, 'get nodes'))

# local etcd snapshot restore
if passed_verb == 'local-restore':

  # check for local snapshot zip
  if not os.path.isfile('kopsrox.etcd.snapshot.zip'):
    print('etcd::local-restore: no kopsrox.etcd.snapshot.zip file found')
    exit(0) 

  # check for number of masters here
  if ( int(masters) == 1 ):
    print('etcd::local-restore: restoring local etcd snapshot to single master')
    write_file = proxmox.writefile(masterid, 'kopsrox.etcd.snapshot.zip')
    write_token = proxmox.writefile(masterid, 'kopsrox.etcd.snapshot.token')

    # command to restore
    restore_cmd = 'systemctl stop k3s && rm -rf /var/lib/rancher/k3s/server/db/ && k3s server --cluster-reset --cluster-reset-restore-path=/var/tmp/kopsrox.etcd.snapshot.zip --token-file=/var/tmp/kopsrox.etcd.snapshot.token && systemctl start k3s'

    print('etcd::local-restore: restoring please wait')
    restore = proxmox.qaexec(masterid, restore_cmd)
    print(restore)
    print(common.kubectl(masterid, 'get nodes'))

  # restore for masters / slave
  if ( int(masters) == 3 ):
    print('etcd::local-restore: restoring etcd snapshot to ha setup')
    write_file = proxmox.writefile(masterid, 'kopsrox.etcd.snapshot.zip')
    write_token = proxmox.writefile(masterid, 'kopsrox.etcd.snapshot.token')

    # stop k3s and restore on m1
    restore_cmd = 'systemctl stop k3s && rm -rf /var/lib/rancher/k3s/server/db/ && k3s server --cluster-reset --cluster-reset-restore-path=/var/tmp/kopsrox.etcd.snapshot.zip --token-file=/var/tmp/kopsrox.etcd.snapshot.token'

    print('etcd::local-restore: restoring please wait')
    restore = proxmox.qaexec(masterid, restore_cmd)
    print(restore)

    # stop k3s on slaves
    print('etcd::local-restore: cleaning slaves')
    stop_m2 = proxmox.qaexec(int(masterid) + 1, 'systemctl stop k3s && rm -rf /var/lib/rancher/k3s/server/db/')
    stop_m3 = proxmox.qaexec(int(masterid) + 2, 'systemctl stop k3s && rm -rf /var/lib/rancher/k3s/server/db/')

    # start k3s on master then slaves
    print('etcd::local-restore: starting k3s on m1')
    start_m1 = proxmox.qaexec(masterid, 'systemctl start k3s')
    print('etcd::local-restore: starting k3s on m2')
    start_m2 = proxmox.qaexec(int(masterid) + 1, 'systemctl start k3s')
    print('etcd::local-restore: starting k3s on m3')
    start_m3 = proxmox.qaexec(int(masterid) + 2, 'systemctl start k3s')

    print(common.kubectl(masterid, 'get nodes'))

