#!/usr/bin/env bash
set -e -u -v -x
LAB=${1:-"uklab16_20"}
# Go to rpc_deployment directory
pushd ../rpc_deployment

# Delete all containers
ansible-playbook -i inventory/${LAB}.yml \
                 -e dinv=inventory/host_vars/${LAB}.yml \
                 -e @inventory/overrides/${LAB}.yml \
                 -e group=all \
                 setup/destroy-containers.yml

popd
