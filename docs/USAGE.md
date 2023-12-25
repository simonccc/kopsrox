# usage 

## image
### create
- downloads the image file defined in `koprox.ini` as `up_image_url` under the `[proxmox]` section
- installs packages qagent + nfs client into the image
- imports the disk into proxmox using `sudo qm`

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
