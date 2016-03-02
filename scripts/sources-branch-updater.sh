#!/usr/bin/env bash
# Copyright 2015, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script was created to rapidly interate through a repo_package file
# that contains git sources and set the various repositories inside to
# the head of given branch via the SHA. This makes it possible to update
# all of the services that we support in an "automated" fashion.

ONLINE_BRANCH=${ONLINE_BRANCH:-"stable/kilo"}
SERVICE_FILE=${SERVICE_FILE:-"playbooks/defaults/repo_packages/openstack_services.yml"}
OPENSTACK_SERVICE_LIST=${OPENSTACK_SERVICE_LIST:-"aodh ceilometer cinder glance heat keystone neutron nova"}

IFS=$'\n'

if echo "$@" | grep -e '-h' -e '--help';then
    echo "
Options:
  -b|--branch       (name of branch, eg: stable/liberty)
  -s|--service-file (path to service file to parse)
"
exit 0
fi

# Provide some CLI options
while [[ $# > 1 ]]; do
key="$1"
case $key in
    -b|--branch)
    ONLINE_BRANCH="$2"
    shift
    ;;
    -s|--service-file)
    SERVICE_FILE="$2"
    shift
    ;;
    *)
    ;;
esac
shift
done

# Iterate through the service file
for repo in $(grep 'git_repo\:' ${SERVICE_FILE}); do

  echo -e "\nInspecting ${repo}..."

  # Set the repo name
  repo_name=$(echo "${repo}" | sed 's/_git_repo\:.*//g')

  # Set the repo address
  repo_address=$(echo ${repo} | awk '{print $2}')

  # Get the branch data
  branch_data=$(git ls-remote ${repo_address} | grep "${ONLINE_BRANCH}$")

  # If there is branch data continue
  if [ ! -z "${branch_data}" ];then

    # Set the branch sha for the head of the branch
    branch_sha=$(echo "${branch_data}" | awk '{print $1}')

    # Set the branch entry
    branch_entry="${branch_sha} # HEAD of \"$ONLINE_BRANCH\" as of $(date +%d.%m.%Y)"

    # Write the branch entry into the repo_packages file
    sed -i.bak "s|${repo_name}_git_install_branch:.*|${repo_name}_git_install_branch: $branch_entry|" ${SERVICE_FILE}

    # If the repo is in the specified list, then action the additional updates
    if [[ "${OPENSTACK_SERVICE_LIST}" =~ "${repo_name}" ]]; then
      repo_tmp_path="/tmp/${repo_name}"

      # Ensure that the temp path doesn't exist
      rm -rf ${repo_tmp_path}

      # Do a shallow clone of the repo to work with
      git clone --quiet --depth=10 --branch ${ONLINE_BRANCH} --no-checkout --single-branch ${repo_address} ${repo_tmp_path}
      pushd ${repo_tmp_path} > /dev/null
        git checkout --quiet ${branch_sha}
      popd > /dev/null

      # Update the policy files
      find ${repo_tmp_path}/etc -name "policy.json" -exec \
        cp {} "playbooks/roles/os_${repo_name}/templates/policy.json.j2" \;

      # Tweak the paste files
      find ${repo_tmp_path}/etc -name "*[_-]paste.ini" -exec \
        sed -i.bak "s|hmac_keys = SECRET_KEY|hmac_keys = {{ ${repo_name}_profiler_hmac_key }}|" {} \;

      # Update the paste files
      find ${repo_tmp_path}/etc -name "*[_-]paste.ini" -exec \
        bash -c "name=\"{}\"; cp \${name} \"playbooks/roles/os_${repo_name}/templates/\$(basename \${name}).j2\"" \;

      # Update the rootwrap conf files
      find ${repo_tmp_path}/etc -name "rootwrap.conf" -exec \
        cp {} "playbooks/roles/os_${repo_name}/templates/rootwrap.conf.j2" \;

      # Update the rootwrap filters
      find ${repo_tmp_path}/etc -name "*.filters" -exec \
        bash -c "name=\"{}\"; cp \${name} \"playbooks/roles/os_${repo_name}/files/rootwrap.d/\$(basename \${name})\"" \;

      # Update the yaml files for Ceilometer
      if [ "${repo_name}" = "ceilometer" ]; then
        find ${repo_tmp_path}/etc -name "*.yaml" -exec \
          bash -c "name=\"{}\"; cp \${name} \"playbooks/roles/os_${repo_name}/templates/\$(basename \${name}).j2\"" \;
      fi

      # Update the yaml files for Heat
      if [ "${repo_name}" = "heat" ]; then
        find ${repo_tmp_path}/etc -name "*.yaml" -exec \
          bash -c "name=\"{}\"; cp \${name} \"playbooks/roles/os_${repo_name}/templates/\$(echo \${name} | rev | cut -sd / -f -2 | rev).j2\"" \;
      fi

      # Clean up the temporary files
      rm -rf ${repo_tmp_path}
    fi
  fi

  echo -e "Processed $repo_name @ $branch_entry\n"

done

unset IFS

# Finally, update the PIP_INSTALL_OPTIONS with the current versions of pip, wheel and setuptools
PIP_CURRENT_OPTIONS=$(./scripts/get-pypi-pkg-version.py -p pip setuptools wheel -l horizontal)
sed -i.bak "s|^PIP_INSTALL_OPTIONS=.*|PIP_INSTALL_OPTIONS=\$\{PIP_INSTALL_OPTIONS:-'${PIP_CURRENT_OPTIONS}'\}|" scripts/scripts-library.sh

for pin in ${PIP_CURRENT_OPTIONS}; do
  sed -i.bak "s|^$(echo ${pin} | cut -f1 -d=).*|${pin}|" *requirements.txt
  sed -i.bak "s|^  - $(echo ${pin} | cut -f1 -d=).*|  - ${pin}|" playbooks/inventory/group_vars/hosts.yml
done

echo "Updated pip install options/pins"
