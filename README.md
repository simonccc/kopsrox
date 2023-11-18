# kopsrox

- cli to automate creating a k3s cluster on proxmox VE using cloud images
- add more master/worker nodes using simple config file
- backup and restore your cluster easily via S3 snapshots
- quick demo: https://asciinema.org/a/597074

Docs:
[CONFIG.md](CONFIG.md)
[FAQ.md](FAG.md)


## setup prerequisites

- password less sudo access on a proxmox VE host 

- `sudo apt install libguestfs-tools python3-termcolor -y`

_to patch the cloudimage and colors_

- `pip3 install --break-system-packages --user -r requirements.txt`

_installs the required pip packages vs using os packages_

## Proxmox API key

Generate an API key and set the permissions:

`sudo pvesh create /access/users/root@pam/token/kopsrox`

`sudo pveum acl modify / --roles Administrator --user root@pam  --token 'root@pam!kopsrox'`

Take a note of the token as we'll need this below

## kopsrox.ini

run `./kopsrox.py` and an example _kopsrox.ini_ will be generated - you will need to edit this for your setup

Kopsrox uses a simple static id/ip assignments based on `proximgid` and `network` settings eg 

```
[proxmox]
...
proximgid = 620
...
[kopsrox]
...
network = 192.168.0.170
...
```

|-|vmid|ip|type|
|--|--|--|--|
|0|620|-|image|
|1|621|192.168.0.171|master 1|
|2|622|192.168.0.172|master 2|
|3|623|192.168.0.173|master 3|
|4|624|-|spare|
|5|625|192.168.0.175|worker 1|
|6|626|192.168.0.176|worker 2|
|7|627|192.168.0.177|worker 3|
|8|628|192.168.0.178|worker 4|
|9|629|192.168.0.179|worker 5|

see [CONFIG.md](CONFIG.md)

## get started
### create an image

`./kopsrox.py create image`

### create a cluster

`./kopsrox.py cluster create`

### add a worker

Edit `kopsrox.ini` and set `workers = 1` in the `[cluster]` section

`./kopsrox.py cluster update`

### check the cluster info

`./kopsrox.py cluster info`

# usage 

## image
__create__
- downloads the image file defined in `koprox.ini` as `up_image_url` under the `[proxmox]` section
- patches it ( installs packages qagent + nfs client) 
- imports the disk using `sudo qm`
- installs k3s 

__destroy__
- deletes the existing image template
- delete the .img file manually if you want a fresh download of the upstream image

__info__
- prints info about image file

## cluster

### create
- creates and updates a cluster - use this to setup a fresh cluster
- exports kubeconfig and node token
- if a working master is found just runs `update`

### update
- checks the state of the cluster vs what is configured in `kopsrox.ini`
- adds or deletes workers/masters per `kopsrox.ini`

### info
- shows a list of ids, hostnames and ips the host they are running on
- shows kubectl get nodes

### kubectl
- provides a quick and basic way to run kubectl commands for example:

`./kopsrox.py cluster kubectl get events -A`

### kubeconfig
- export the kubeconfig to a `kopsrox.kubeconfig` file which is patched to have the masters IP

### destroy
- destroys the cluster ( NO WARNING! ) 

## etcd

kopsrox uses the k3s built in commands to backup to s3 api compatible storage.

tested providers include minio, cloudflare, backblaze etc

### snapshot

The first time a snapshot is taken the cluster token is written to `kopsrox.etcd.snapshot.token`

This is not overwriten when further snapshots are taken - even on a new cluster

`./kopsrox.py etcd snapshot`

Takes a backup of etcd

`./kopsrox.py etcd list`

Should show the new backup

### restore

Restores a cluster from an etcd snapshot

`./kopsrox.py etcd list`

show available snapshots

`./kopsrox.py etcd restore $imagename`

- check you're using the correct `kopsrox.etcd.snapshot.token` file for the snapshot!

- downsizes the cluster to 1 node 

### list

- lists snapshots taken in s3 storage based on cluster name

### prune

- deletes old snapshots by 7 days? ( tbc ) 
