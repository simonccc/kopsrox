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

# check for number of nodes
config = common.read_kopsrox_ini()
masters = config['cluster']['masters']
k3s_version = (config['cluster']['k3s_version'])

# get masterid
masterid = common.get_master_id()

# snapshot
if passed_verb == 'snapshot':
  print('etcd:snapshot: kopsrox-m1:' + str(masterid))

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
  print('etcd:snapshot:', path, 'created')

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
  print("etcd:snapshot: wrote kopsrox.etcd.snapshot.zip")

  # write the snapshot tokenfile
  token = common.get_token()
  token = token + '\n'
  with open('kopsrox.etcd.snapshot.token', 'w') as snapshot_token:
    snapshot_token.write(token)
  print("etcd:snapshot: wrote kopsrox.etcd.snapshot.token")

# etcd snapshot restore
if passed_verb == 'restore':

  # check for local snapshot zip
  if not os.path.isfile('kopsrox.etcd.snapshot.zip'):
    print('etcd:restore: no kopsrox.etcd.snapshot.zip file found')
    exit(0) 

  # check for number of masters here
  if ( int(masters) == 1 ):
    print('etcd:restore: restoring etcd snapshot to single master')
    write_file = proxmox.writefile(masterid, 'kopsrox.etcd.snapshot.zip')
    print('etcd:restore: written snapshot')
    write_token = proxmox.writefile(masterid, 'kopsrox.etcd.snapshot.token')
    print('etcd:restore: written snapshot token')

    # stop k3s
    restore_cmd = 'systemctl stop k3s && rm -rf /var/lib/rancher/k3s/server/db/ && k3s server --cluster-reset --cluster-reset-restore-path=/var/tmp/kopsrox.etcd.snapshot.zip --token-file=/var/tmp/kopsrox.etcd.snapshot.token && systemctl start k3s'

    print('etcd:restore: restoring please wait')
    restore = proxmox.qaexec(masterid, restore_cmd)
    print(restore_cmd)
    print(restore)
    print(common.kubectl(masterid, 'get nodes'))

