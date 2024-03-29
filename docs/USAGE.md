# usage 

- [image](#image)
  - [create](#image-create)
  - [destroy](#image-destroy)
  - [info](#image-info)
- [cluster](#cluster)
  - [create](#cluster-create)
  - [update](#cluster-update)
  - [info](#cluster-info)
  - [kubectl](#kubectl)
  - [kubeconfig](#kubeconfig)
  - [destroy](#cluster-destroy)
- [etcd](#etcd)
  - [snapshot](#snapshot)
  - [list](#list)
  - [restore](#restore)
  - [prune](#prune)

## image <a name=image>
### create <a name=image-create>
- downloads the image file defined in `koprox.ini` as `up_image_url` under the `[proxmox]` section
- installs `qemu-guest-agent` into the image via `virt-customise`
- imports the disk into the `proxstore` proxmox storage using `sudo qm`
- creates cloudinit drive with user and networking setup
- converts the vm into a template
- patched cloudimage is backed up
  
### destroy <a name=image-destroy> 
- :warning: deletes the existing image template
- delete the .img file manually  ( eg `mantic-minimal-cloudimg-amd64.img` if you want a fresh download/repatch of the upstream image

### info <a name=image-info> 
- prints info about image/template vm eg storage, id, creation time and source cloud image file

## cluster <a name=cluster>
### create <a name=cluster-create>
- creates and updates a cluster - use this to setup a fresh cluster
- clones the image to `kopsrox-m1` master server and configures it via cloudinit
- exports kubeconfig and node token
- if an existing working master is found just runs the same steps as `kopsrox cluster update`

### update <a name=cluster-update>
- checks the state of the cluster vs what is configured in `kopsrox.ini`
- adds or deletes workers/masters per `kopsrox.ini`

### info <a name=cluster-info>
- shows a list of ids, hostnames and ips the host they are running on
- shows `kubectl get nodes`

### kubectl <a name=kubectl>
- provides a quick and basic way to run some kubectl commands for example:

`./kopsrox.py cluster kubectl get events -A`

### kubeconfig <a name=kubeconfig>
- export the cluster kubeconfig to a `$cname.kubeconfig` file - ie the name of the cluster set in `kopsrox.ini`
- file is patched to have correct master IP vs 127.0.0.1

### destroy <a name=cluster-destroy>
- :warning: destroys the cluster ( NO WARNING! ) 
- deletes workers then masters in safe order

## etcd <a name=etcd>
### snapshot <a name=snapshot>

The first time a snapshot is taken the cluster token is written to `clustername.etcd.token`

This is not overwriten when further snapshots are taken - even on a new cluster with the same name

`./kopsrox.py etcd snapshot`

Takes a backup of etcd

`./kopsrox.py etcd list`

Should show the new backup

### list <a name=s3-list>

`./kopsrox.py etcd list`

- lists snapshots taken in s3 storage based on cluster name

### restore <a name=restore>

restores a cluster from a snapshot

usage:

`./kopsrox.py etcd restore $imagename`

- :white_check_mark: check you're using the correct `kopsrox.etcd.snapshot.token` file for the snapshot!

- downsizes the cluster to 1 node then resizes back to the scale set in `kopsrox.ini`

### prune <a name=prune>

- deletes old snapshots per the retention policy set on the bucket
