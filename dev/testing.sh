#set -e
#set -x

start_time=$(date +%s) 

# vars
CFG="kopsrox.ini"
K="./kopsrox.py"
KC="$K cluster"
KCI="$KC info"
KCC="$KC create"
KCU="$KC update"
KCD="$KC destroy"
KI="$K image"
KID="$KI destroy"
KIC="$KI create"
KII="$KI info"
KE="$K etcd"
KEL="$K list"
KES="$KE snapshot"
KER="$KE restore"
KERL="${KER}-latest"


# change 
kc() {
  sed -i /"$1 =/c\\$1 = $2" $CFG
}

# minimal cluster
kc masters 1 ; kc workers 0
$KCU
kc masters 1 ; kc workers 1
$KCU
kc masters 1 ; kc workers 0
$KCU

# get pods
get_pods="$KC kubectl get pods -A"

# recreate 1 node
#./kopsrox.py cluster destroy && ./kopsrox.py cluster create
#$KCD ; $KCC


# add a worker and delete it
#kc workers 0 ; $KCU ; kc workers 3 ; $KCU ; kc workers 0 ; $KCU
#kc masters 3 ; $KCU ; kc masters 1  ; $KCU

# destroy image create cluster create restore latest
#$KCD ; $KIC ; $KCC ; $KERL
#


finish_time=$(date +%s) 
echo  $((finish_time - start_time)) secs
