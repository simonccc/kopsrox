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

  # open kopsrox manifest
  kopsrox_yaml = f'./lib/manifests/kopsrox-{cluster_name}.yaml'
  kopsrox_manifest = open(kopsrox_yaml, 'w')

  # generate kubevip manifest
  kv_manifest = open('./lib/manifests/kubevip.yaml', 'r').read().replace('KOPSROX_IP', network_ip).strip()
  kopsrox_manifest.write(kv_manifest)

  # generate traefik helm config
  traefik_conf = f'''
---
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  valuesContent: |-
    service:
      spec:
        loadBalancerIP: "{network_ip}"'''
  kopsrox_manifest.write(traefik_conf)

  # define common secret section for sergelogvinov's helm charts
  controller_common = f'''
    config:
      clusters:
        - url: https://{proxmox_endpoint}:{proxmox_api_port}/api2/json
          insecure: true
          token_id: {proxmox_user}!{proxmox_token_name}
          token_secret: {proxmox_token_value}
          region: {cluster_name}'''

  # generate cloud controller yaml
  ccm_manifest = f'''
---
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: proxmox-cloud-controller-manager
  namespace: kube-system
spec:
  bootstrap: true
  chart: oci://ghcr.io/sergelogvinov/charts/proxmox-cloud-controller-manager
  valuesContent: |-{controller_common}
    useDaemonSet: true
    nodeSelector:
      node-role.kubernetes.io/control-plane: "true"
'''
  kopsrox_manifest.write(ccm_manifest)

  # generate csi yaml
  csi_manifest = f'''
---
apiVersion: v1
kind: Namespace
metadata:
  labels:
    kubernetes.io/metadata.name: csi-proxmox
    pod-security.kubernetes.io/enforce: privileged
  name: csi-proxmox
---
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: proxmox-csi-plugin
  namespace: csi-proxmox
spec:
  chart: oci://ghcr.io/sergelogvinov/charts/proxmox-csi-plugin
  valuesContent: |-{controller_common}
    storageClass:
      - name: proxmox-csi
        storage: {proxmox_storage}
        annotations:
          storageclass.kubernetes.io/is-default-class: 'true'
'''
  kopsrox_manifest.write(csi_manifest)
  kopsrox_manifest.close()

  token_fname = f'{cluster_name}.k3stoken'
  token_cmd = ''
  if os.path.isfile(token_fname):
    token = open(token_fname, "r").read()
    token_cmd = f' --token {token}'

  k3s_install_options = f'--kubelet-arg --cloud-provider=external --kubelet-arg --provider-id=proxmox://{cluster_name}/{vmid} {token_cmd}'
  k3s_install_version = f'cat /k3s.sh | INSTALL_K3S_VERSION={k3s_version}'
  k3s_install_master = f'{k3s_install_version} sh -s - server --cluster-init --disable=servicelb,local-storage --node-label="topology.kubernetes.io/zone={proxmox_node}" --tls-san={network_ip} {k3s_install_options}'
  k3s_install_slave = f'{k3s_install_version} sh -s - server --server https://{network_ip}:6443 {k3s_install_options}'
  k3s_install_worker = f'rm -rf /etc/rancher/k3s/* && {k3s_install_version} sh -s - agent --server="https://{network_ip}:6443" {k3s_install_options}'

  # script to run in kopsrox image
  virtc_script = f'''\
curl -v https://get.k3s.io > /k3s.sh
mkdir -p /var/lib/rancher/k3s/server/manifests/
mkdir -p /etc/rancher/k3s/config.yaml.d/
echo -n '
#!/usr/bin/env bash
if [[ ! \"$1\" ]] then
echo err
exit
fi

if [[ \"$1\" == "master" ]] then
{k3s_install_master}
exit
fi

if [[ \"$1\" == "slave" ]] then
{k3s_install_slave}
exit
fi

if [[ \"$1\" == "worker" ]] then
{k3s_install_worker}
exit
fi
' > /kopsrox.sh 
chmod +x /kopsrox.sh

echo -n '
etcd-s3: true
etcd-snapshot-retention: 7
etcd-s3-region: {region_string}
etcd-s3-endpoint: {s3_endpoint}
etcd-s3-access-key: {access_key}
etcd-s3-secret-key: {access_secret}
etcd-s3-bucket: {bucket}
etcd-s3-skip-ssl-verify: true
etcd-snapshot-compress: true'  > /etc/rancher/k3s/config.yaml.d/etcd-backup.yaml'''

  # shouldn't really need root/sudo but run into permissions problems
  kmsg(f'{kname}virt-customize', f'installing {image_packages}')
  virtc_cmd = f'''
sudo virt-customize -a {cloud_image} \
--install {image_packages} \
--run-command "{virtc_script}" \
--copy-in {kopsrox_yaml}:/var/lib/rancher/k3s/server/manifests/ \
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
