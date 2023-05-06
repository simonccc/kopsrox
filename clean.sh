set -x
set -e
echo "removing vms"
sudo qm destroy 600
sudo qm stop 601
sudo qm destroy 601
echo "kopsrox img create"
./kopsrox.py image create
./kopsrox.py image info
echo "kopsrox cluster create"
./kopsrox.py cluster create
./kopsrox.py cluster info
