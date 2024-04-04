# usage 

- [image](#image)
- [cluster](#cluster)
- [etcd](#etcd)
- [node](#node)

## image <a name=image>
### create 
- downloads the image file defined in `koprox.ini`
- installs `qemu-guest-agent` into the image via `virt-customise`
- imports the disk into the `storeage` proxmox storage using `sudo qm`
- creates cloudinit drive with user and networking setup
- converts the vm into a template
  
### destroy 
- :warning: deletes the existing image template

### info <a name=image-info> 
- prints info about image/template vm eg storage, id, creation time and source cloud image file

## cluster <a name=cluster>
### create 
- creates and updates a cluster - use this to setup a fresh cluster
- clones the image to `kopsrox-m1` master server and configures it via cloudinit
- exports kubeconfig and node token
- if an existing working master is found just runs the same steps as `kopsrox cluster update`

### update 
- checks the state of the cluster vs what is configured in `kopsrox.ini`
- adds or deletes workers/masters per `kopsrox.ini`

### info 
- shows a list of ids, hostnames and ips the host they are running on
- shows `kubectl get nodes`

### kubectl 
- provides a quick and basic way to run some kubectl commands for example:

`./kopsrox.py cluster kubectl get events -A`

### kubeconfig 
- export the cluster kubeconfig to a `$cname.kubeconfig` file - ie the name of the cluster set in `kopsrox.ini`
- file is patched to have correct master IP vs 127.0.0.1

### destroy 
- :warning: destroys the cluster ( NO WARNING! ) 
- deletes workers then masters in safe order

### k3stoken 
- exports the clusters k3s token ( used to add nodes to cluster ) 

## etcd <a name=etcd>
### snapshot 

`./kopsrox.py etcd snapshot`

Takes a backup of etcd

`./kopsrox.py etcd list`

Should show the new backup

### list 

`./kopsrox.py etcd list`

- lists snapshots taken in s3 storage based on cluster name

### restore 

restores a cluster from a snapshot

usage:

`./kopsrox.py etcd restore $imagename`

- :white_check_mark: check you're using the correct `kopsrox.etcd.snapshot.token` file for the snapshot!

- downsizes the cluster to 1 node then resizes back to the scale set in `kopsrox.ini`

### restore-latest
- restores the cluster from the latest backup in s3

### prune 
- deletes old snapshots per the retention policy set on the bucket

## node
### destroy
- pass hostname destroys that host
### utility
- creates the utility node -u1
### terminal
- connects you to the passed vms serial console


