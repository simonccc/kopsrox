# get started
## create an image

`./kopsrox.py create image`

## create a cluster

`./kopsrox.py cluster create`

## add a worker

Edit `kopsrox.ini` and set `workers = 1` in the `[cluster]` section

`./kopsrox.py cluster update`

## check the cluster info

`./kopsrox.py cluster info`

## create etcd snapshot 

Configure 'kopsrox.ini' with suitable s3 details for your provider

`./kopsrox.py etcd snapshot`
