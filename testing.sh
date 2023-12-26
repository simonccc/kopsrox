#set -e
#set -x

# vars
CFG="kopsrox.ini"
K="./kopsrox.py"
KC="$K cluster"
KCU="$KC update"

# change 
kc() {
  sed -i /"$1 =/c\\$1 = $2" $CFG
}

# recreate 1 node
# sed to ensure 1 master 1 worker
#./kopsrox.py cluster destroy && ./kopsrox.py cluster create
#

# add a worker and delete it
#kc workers 0 ; $KCU ; kc workers 3 ; $KCU ; kc workers 0 ; $KCU
kc masters 3 ; $KCU ; kc masters 1  ; $KCU
