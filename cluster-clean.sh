set -x
set -e
echo "kopsrox destroy"
./kopsrox.py cluster destroy
sleep 2
echo "kopsrox cluster create"
./kopsrox.py cluster create
sleep 2
./kopsrox.py cluster info
