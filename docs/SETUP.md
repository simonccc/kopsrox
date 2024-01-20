## Requirements :hammer_and_wrench:

- password less sudo access on a proxmox VE host  ( tested up to 8.1.3 ) 
- network with internet access configured in proxmox
- a range of 10 free Proxmox 'vmids' eg 600 to 610
- a range of 10 IP's on your network for kopsrox to work with eg 192.168.0.160 to 192.168.0.170

## Install Packages :bricks:

- `sudo apt install libguestfs-tools python3-termcolor -y`
- `pip3 install --break-system-packages --user -r requirements.txt`

_installs the required pip packages vs using os packages_

## Generate Proxmox API key

`sudo pvesh create /access/users/root@pam/token/kopsrox`

`sudo pveum acl modify / --roles Administrator --user root@pam  --token 'root@pam!kopsrox'`

Take a note of the token as you will need this for `kopsrox.ini` or check out [CONFIG.md](CONFIG.md)

## Create kopsrox.ini

run `./kopsrox.py` and an example _kopsrox.ini_ will be generated - you will need to edit this for your setup

check out [CONFIG.md](CONFIG.md)
