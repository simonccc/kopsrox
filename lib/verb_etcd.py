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

# snapshot
if passed_verb == 'snapshot':
  masterid = common.get_master_id()
  print('etcd:snapshot: kopsrox-m1:' + str(masterid))
  snapout = proxmox.qaexec(masterid, 'k3s etcd-snapshot --etcd-snapshot-compress --name kopsrox')

  # get path of snapshot 
  for line in snapout.split():
    # in path in output line
    if (re.search('path', line)):
      # split the line with output by :
      rpath = line.split(':')

  # remove extra chars and add .zip
  path = (rpath[8].replace('}', '').replace('"', '') + '.zip')
  print('etcd:snapshot:', path, 'created')

  # qaexec needs commands to have output ( the echo ok ) 
  b64cmd = ('sudo base64 ' + path + ' > ' + ( path + '.b64' ) + ' && echo ok')
  b64 = proxmox.qaexec(masterid, b64cmd)

  # try qagent file get 
  # this will break when the file gets too large
  get_file = proxmox.getfile(masterid, str((path + '.b64')))

  # encode the already b64 file
  contentb64 = get_file.encode()

  # write the snapshot
  with open('kopsrox.etcd.snapshot.zip', 'wb') as snapshot:
    snapshot.write(base64.b64decode(contentb64))
  print("etcd:snapshot: written kopsrox.etcd.snapshot.zip")

# etcd snapshot restor
if passed_verb == 'restore':
  if not os.path.isfile('kopsrox.etcd.snapshot.zip'):
    print('etcd:restore: no kopsrox.etcd.snapshot.zip file found')
    exit(0) 
  print('etcd:restore: restoring etcd snapshot')

