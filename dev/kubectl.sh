c=`grep ^cluster_name kopsrox.ini | cut -d ' ' -f3`
kubectl --kubeconfig=${c}.kubeconfig ${@}
