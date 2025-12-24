#!/usr/bin/env python3

# functions
from kopsrox_config import * 

# proxmox functions
from kopsrox_proxmox import prox_task, prox_destroy

# define command
cmd = sys.argv[2]
kname = 'image_'

# create image
if cmd == 'create':

  # get image name from url 
  cloud_image = cloud_image_url.split('/')[-1]
  kmsg(f'{kname}create', f'{cloud_image} > {cluster_name}-i0', 'sys')

  # check if image already exists
  if os.path.isfile(cloud_image):
    kmsg(f'{kname}check', f'{cloud_image} already exists - removing','sys')
    try:
      os.remove(cloud_image)
      if os.path.isfile(cloud_image):
        exit(0)
    except:
      kmsg(f'{kname}check', f'{cloud_image} cannot delete', 'err')
      exit(0)

  # check img can be downloaded
  try:
    kmsg(f'{kname}wget', f'{cloud_image_url}')
    wget.download(cloud_image_url)
    print()
  except:
    kmsg(f'{kname}check', f'unable to download {cloud_image_url}', 'err')
    exit(0)

  # kubevip
  # open the generic kubevip deployment and patch it with our network_ip in memory
  kv_manifest = open('./lib/kubevip/kubevip.yaml', 'r').read().replace('KOPSROX_IP', network_ip).strip()

  # define the name/location of the patched kubevip 
  kv_yaml = f'./lib/kubevip/{cluster_name}-kubevip.yaml'

  # write the patched in memory version to file
  kv_write_out = open(kv_yaml, 'w') 
  kv_write_out.write(kv_manifest)
  kv_write_out.close()

  # proxmox cloud controller manager
  pccm_conf = open('./lib/pccm/template.yaml').read()
  pccm_conf = pccm_conf.replace('KOPSROX_IP', proxmox_endpoint)
  pccm_conf = pccm_conf.replace('KOPSROX_PORT', proxmox_api_port)
  pccm_conf = pccm_conf.replace('KOPSROX_TOKEN', f'{proxmox_user}!{proxmox_token_name}')
  pccm_conf = pccm_conf.replace('KOPSROX_SECRET', f'{proxmox_token_value}')
  pccm_conf = pccm_conf.replace('KOPSROX_CLUSTER', f'{cluster_name}')
  pccm_write_out = open(f'./lib/pccm/{cluster_name}-pccm-raw.yaml','w')
  pccm_write_out.write(pccm_conf)
  pccm_write_out.close()

  pccm_encode = pccm_conf.encode()
  pccm_b64 = base64.b64encode(pccm_encode)
  pccm_secret = f'''
---
apiVersion: v1
data:
  config.yaml: {pccm_b64.decode()}
kind: Secret
metadata:
  name: proxmox-cloud-controller-manager
  namespace: kube-system
type: Opaque'''

  pccm_yaml = f'./lib/pccm/{cluster_name}-pccm-secret.yaml'
  pccm_depl = open('./lib/pccm/cloud-controller-manager.yml','r').read()
  pccm_write_out = open(pccm_yaml, 'w')
  pccm_write_out.write(pccm_depl)
  pccm_write_out.write(pccm_secret)
  pccm_write_out.close()

  # script to run in kopsrox image
  virtc_script = f'''\
curl -v https://get.k3s.io > /k3s.sh 
mkdir -p /var/lib/rancher/k3s/server/manifests/
echo '
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  valuesContent: |-
    service:
      spec:
        loadBalancerIP: "{network_ip}"' > /var/lib/rancher/k3s/server/manifests/traefik-config.yaml

mkdir -p /etc/rancher/k3s/config.yaml.d/
echo -n '
etcd-s3: true
etcd-snapshot-retention: 7
etcd-s3-region: {region_string}
etcd-s3-endpoint: {s3_endpoint}
etcd-s3-access-key: {access_key}
etcd-s3-secret-key: {access_secret}
etcd-s3-bucket: {bucket}
etcd-s3-skip-ssl-verify: true
etcd-snapshot-compress: true'  > /etc/rancher/k3s/config.yaml.d/etcd-backup.yaml

echo -n '
tls-san: {network_ip}' > /etc/rancher/k3s/config.yaml
'''
  # shouldn't really need root/sudo but run into permissions problems
  kmsg(f'{kname}virt-customize', f'installing {image_packages}')
  virtc_cmd = f'''
sudo virt-customize -a {cloud_image} \
--install {image_packages} \
--run-command "{virtc_script}" \
--copy-in {kv_yaml}:/var/lib/rancher/k3s/server/manifests/ \
--copy-in {pccm_yaml}:/var/lib/rancher/k3s/server/manifests/ \
> virt-customize.log 2>&1'''
  local_os_process(virtc_cmd)

  # destroy template if it exists
  try:
    prox_destroy(cluster_id)
  except:
    pass

  # define image desc
  img_ts = str(datetime.now())
  image_desc = f'''
cluster_name: {cluster_name}
cloud_img: {cloud_image}
k3s_version: {k3s_version}
created: {img_ts}'''

  # create new server
  prox_task(prox.nodes(proxmox_node).qemu.post(
    vmid = cluster_id,
    cores = 1,
    memory = 1024,
    bios = 'ovmf',
    efidisk0 = f'{proxmox_storage}:0',
    machine = 'q35',
    cpu = ('cputype=x86-64-v3'),
    scsihw = 'virtio-scsi-single',
    name = f'{cluster_name}-i0',
    ostype = 'l26',
    scsi2 = (f'{proxmox_storage}:cloudinit'),
    tags = cluster_name,
    serial0 = 'socket',
    agent = ('enabled=true'),
    hotplug = 0,
    ciupgrade = 0,
    description = image_desc,
    ciuser = cloudinituser, 
    cipassword = cloudinitpass,
    sshkeys = cloudinitsshkey,
  ))

  # shell to import disk
  # import-from requires the full path os.getcwd required here
  import_cmd = f'''
sudo qm set {cluster_id} --scsi0 {proxmox_storage}:0,import-from={os.getcwd()}/{cloud_image},iothread=true,aio=native
mv {cloud_image} {cloud_image}.patched'''

  # run shell command to import
  kmsg(f'{kname}qm-import', f'importing disk')
  local_os_process(import_cmd)

  # convert to template via create base disk also vm config
  prox_task(prox.nodes(proxmox_node).qemu(cluster_id).template.post())
  prox_task(prox.nodes(proxmox_node).qemu(cluster_id).config.post(template = 1))

# image info
if cmd == 'info':
  image_info()

# destroy image
if cmd == 'destroy':
   kmsg(f'{kname}destroy', f'{kopsrox_img()}/{cloud_image_desc}', 'sys')
   prox_destroy(cluster_id)
