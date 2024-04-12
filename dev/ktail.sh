c=`grep ^cluster_name kopsrox.ini | cut -d ' ' -f3`
kubectl --kubeconfig=${c}.kubeconfig get events --all-namespaces --watch-only -o 'go-template={{.lastTimestamp}}-{{.involvedObject.namespace}} [{{.involvedObject.kind}}] {{.message}} ({{.involvedObject.name}})'
