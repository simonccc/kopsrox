#  ☣️ get started

## 🇧🇸 setup kopsrox.ini

`./kopsrox.py` - a default kopsrox.ini will be created

you will need to edit this for your setup

follow the guide in [SETUP.md](SETUP.md)

## 🥑   create an image

`./kopsrox.py create image`

## 🥑 create a cluster

`./kopsrox.py cluster create`

## 🚑 add a worker

edit `kopsrox.ini` and set `workers = 1` in the `[cluster]` section

`./kopsrox.py cluster update`

## ➡️ check the cluster info

`./kopsrox.py cluster info`

## 🍎 create etcd snapshot 

Configure 'kopsrox.ini' with suitable s3 details for your provider

`./kopsrox.py etcd snapshot`

## 🛺 restore the latest snapshot

`./kopsrox.py etcd restore-latest`
