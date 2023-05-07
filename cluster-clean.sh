set -x
set -e
echo "kopsrox destroy"
./kopsrox.py cluster destroy
echo "kopsrox cluster create"
./kopsrox.py cluster create
./kopsrox.py cluster info
