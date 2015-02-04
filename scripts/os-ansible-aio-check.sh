#!/bin/bash

# This is a placeholder until we change the macro for the
# os-ansible-deployment gate check script to use the
# newly split script set.

set -e -u -v -x

source $(dirname ${0})/gate-check-commit.sh
