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

OS_BRANCH=${OS_BRANCH:-"master"}
OSA_BRANCH=${OSA_BRANCH:-"$OS_BRANCH"}
SERVICE_FILE=${SERVICE_FILE:-"playbooks/defaults/repo_packages/openstack_services.yml"}
OPENSTACK_SERVICE_LIST=${OPENSTACK_SERVICE_LIST:-"$(grep 'git_repo\:' ${SERVICE_FILE} | awk -F '/' '{ print $NF }' | egrep -v 'requirements|-' | tr '\n' ' ')"}
PRE_RELEASE=${PRE_RELEASE:-"false"}

IFS=$'\n'

if echo "$@" | grep -e '-h' -e '--help';then
    echo "
Options:
  -b|--openstack-branch (name of OpenStack branch, eg: stable/newton)
  -o|--osa-branch       (name of the OSA branch, eg: stable/newton)
  -s|--service-file     (path to service file to parse)
"
exit 0
fi

# Provide some CLI options
while [[ $# > 1 ]]; do
key="$1"
case $key in
    -b|--openstack-branch)
    OS_BRANCH="$2"
    shift
    ;;
    -o|--osa-branch)
    OSA_BRANCH="$2"
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
  branch_data=$(git ls-remote ${repo_address} | grep "${OS_BRANCH}$")

  # If there is branch data continue
  if [ ! -z "${branch_data}" ];then

    # Set the branch sha for the head of the branch
    branch_sha=$(echo "${branch_data}" | awk '{print $1}')

    # Set the branch entry
    branch_entry="${branch_sha} # HEAD of \"$OS_BRANCH\" as of $(date +%d.%m.%Y)"

    # Write the branch entry into the repo_packages file
    sed -i.bak "s|${repo_name}_git_install_branch:.*|${repo_name}_git_install_branch: $branch_entry|" ${SERVICE_FILE}

    # If the repo is in the specified list, then action the additional updates
    if [[ "${OPENSTACK_SERVICE_LIST}" =~ "${repo_name}" ]]; then
      os_repo_tmp_path="/tmp/os_${repo_name}"
      osa_repo_tmp_path="/tmp/osa_${repo_name}"

      # Ensure that the temp path doesn't exist
      rm -rf ${os_repo_tmp_path} ${osa_repo_tmp_path}

      # Do a shallow clone of the OpenStack repo to work with
      if git clone --quiet --depth=10 --branch ${OS_BRANCH} --no-checkout --single-branch ${repo_address} ${os_repo_tmp_path}; then
        pushd ${os_repo_tmp_path} > /dev/null
          git checkout --quiet ${branch_sha}
        popd > /dev/null

        # Set the OSA address
        osa_repo_address="https://git.openstack.org/openstack/openstack-ansible-os_${repo_name}"

        # Do a shallow clone of the OSA repo to work with
        if git clone --quiet --depth=10 --branch ${OSA_BRANCH} --single-branch ${osa_repo_address} ${osa_repo_tmp_path}; then
          pushd ${osa_repo_tmp_path} > /dev/null
            git checkout --quiet origin/${OSA_BRANCH}
          popd > /dev/null

          # Update the policy files
          find ${os_repo_tmp_path}/etc -name "policy.json" -exec \
            cp {} "${osa_repo_tmp_path}/templates/policy.json.j2" \;

          # Tweak the paste files for any hmac key entries
          find ${os_repo_tmp_path}/etc -name "*[_-]paste.ini" -exec \
            sed -i.bak "s|hmac_keys = SECRET_KEY|hmac_keys = {{ ${repo_name}_profiler_hmac_key }}|" {} \;

          # Tweak the barbican paste file to support keystone auth
          if [ "${repo_name}" = "barbican" ]; then
            find ${os_repo_tmp_path}/etc -name "*[_-]paste.ini" -exec \
              sed -i.bak sed 's|\/v1\: barbican-api-keystone|\/v1\: {{ (barbican_keystone_auth \| bool) \| ternary('barbican-api-keystone', 'barbican_api') }}|'{} \;
          fi

          # Tweak the gnocchi paste file to support keystone auth
          if [ "${repo_name}" = "gnocchi" ]; then
            find ${os_repo_tmp_path}/etc -name "*[_-]paste.ini" -exec \
              sed -i.bak "s|pipeline = gnocchi+noauth|pipeline = {{ (gnocchi_keystone_auth \| bool) \| ternary('gnocchi+auth', 'gnocchi+noauth') }}|" {} \;
          fi

          # Update the paste files
          find ${os_repo_tmp_path}/etc -name "*[_-]paste.ini" -exec \
            bash -c "name=\"{}\"; cp \${name} \"${osa_repo_tmp_path}/templates/\$(basename \${name}).j2\"" \;

          # Tweak the rootwrap conf filters_path (for neutron only)
          if [ "${repo_name}" = "neutron" ]; then
            find ${os_repo_tmp_path}/etc -name "rootwrap.conf" -exec \
              sed -i.bak "s|filters_path=/etc/neutron|filters_path={{ ${repo_name}_conf_dir }}|" {} \;
          fi

          # Tweak the rootwrap conf exec_dirs
          find ${os_repo_tmp_path}/etc -name "rootwrap.conf" -exec \
            sed -i.bak "s|exec_dirs=|exec_dirs={{ ${repo_name}_bin }},|" {} \;

          # Update the rootwrap conf files
          find ${os_repo_tmp_path}/etc -name "rootwrap.conf" -exec \
            cp {} "${osa_repo_tmp_path}/templates/rootwrap.conf.j2" \;

          # Update the rootwrap filters
          find ${os_repo_tmp_path}/etc -name "*.filters" -exec \
            bash -c "name=\"{}\"; cp \${name} \"${osa_repo_tmp_path}/files/rootwrap.d/\$(basename \${name})\"" \;

          # Update the yaml files for Ceilometer
          if [ "${repo_name}" = "ceilometer" ]; then
            find ${os_repo_tmp_path}/etc -name "*.yaml" -exec \
              bash -c "name=\"{}\"; cp \${name} \"${osa_repo_tmp_path}/templates/\$(basename \${name}).j2\"" \;
          fi

          # Update the yaml files for Heat
          if [ "${repo_name}" = "heat" ]; then
            find ${os_repo_tmp_path}/etc -name "*.yaml" -exec \
              bash -c "name=\"{}\"; cp \${name} \"${osa_repo_tmp_path}/templates/\$(echo \${name} | rev | cut -sd / -f -2 | rev).j2\"" \;
          fi

          # Switch into the OSA git directory to work with it
          pushd ${osa_repo_tmp_path} > /dev/null

            # Check for changed files
            git_changed=$(git status --porcelain | wc -l)
            # Check for untracked files
            git_untracked=$(git ls-files --other --exclude-standard --directory | wc -l)
            if [ ${git_untracked} -gt 0 ]; then
              # If there are untracked files, ensure that the commit message includes
              # a WIP prefix so that the patch is revised in more detail.
              git_msg_prefix="[New files - needs update] "
            else
              git_msg_prefix=""
            fi

            # If any files have changed, submit a patch including the changes
            if [ ${git_changed} -gt 0 ]; then
              git checkout -b sha-update
              git review -s > /dev/null
              git add --all
              git commit -a -m "${git_msg_prefix}Update paste, policy and rootwrap configurations $(date +%Y-%m-%d)" --quiet
              git review > /dev/null
            fi
          popd > /dev/null
        fi
      fi

      # Clean up the temporary files
      rm -rf ${os_repo_tmp_path} ${osa_repo_tmp_path}
    fi
  fi

  echo -e "Processed $repo_name @ $branch_entry\n"

done

unset IFS

# Update the PIP_INSTALL_OPTIONS with the current versions of pip, wheel and setuptools
PIP_CURRENT_OPTIONS=$(./scripts/get-pypi-pkg-version.py -p pip setuptools wheel -l horizontal)
sed -i.bak "s|^PIP_INSTALL_OPTIONS=.*|PIP_INSTALL_OPTIONS=\$\{PIP_INSTALL_OPTIONS:-'${PIP_CURRENT_OPTIONS}'\}|" scripts/scripts-library.sh

for pin in ${PIP_CURRENT_OPTIONS}; do
  sed -i.bak "s|^$(echo ${pin} | cut -f1 -d=).*|${pin}|" global-requirement-pins.txt
  sed -i.bak "s|^  - $(echo ${pin} | cut -f1 -d=).*|  - ${pin}|" playbooks/inventory/group_vars/all.yml
done

echo "Updated pip install options/pins"

# Update the ansible-role-requirements.yml file
# We don't want to be doing this for the master branch
if [ "${OSA_BRANCH}" != "master" ] || [ "${PRE_RELEASE}" == "true" ]; then
  echo "Updating ansible-role-requirements.yml"

  if [ "${PRE_RELEASE}" == "true" ]; then
    ROLE_GIT_SOURCES=$(awk '/src: .*/ {print $2}' ansible-role-requirements.yml)
  else
    ROLE_GIT_SOURCES=$(awk '/src: .*\/openstack\// {print $2}' ansible-role-requirements.yml)
  fi

  # Loop through each of the role git sources, only looking for openstack roles
  for role_src in ${ROLE_GIT_SOURCES}; do

    # Determine the role's name
    role_name=$(sed 's/^[ \t-]*//' ansible-role-requirements.yml | awk '/src: / || /name: / {print $2}' | grep -B1 "${role_src}" | head -n 1)
    echo "... updating ${role_name}"

    # If the role_src is NOT from git.openstack.org, try to get a tag first
    if [[ ${role_src} != *"git.openstack.org"* ]]; then
      role_version=$(git ls-remote --tags ${role_src} | awk '{print $2}' | grep -v '{}' | cut -d/ -f 3 | sort -n | tail -n 1)
    fi

    # Grab the latest SHA that matches the specified branch
    if [[ -z "${role_version}" ]]; then
      role_version=$(git ls-remote ${role_src} | grep "${OSA_BRANCH}$" | awk '{print $1}')
    fi

    # For OSA roles, get the release notes
    if [[ ${role_src} == *"git.openstack.org"* ]]; then
      # Setup a var for tmp space
      osa_repo_tmp_path="/tmp/osa_${role_name}"

      # Ensure that the temp path doesn't exist
      rm -rf ${osa_repo_tmp_path}

      # Do a shallow clone of the repo to work with
      git clone --quiet --depth=10 --branch ${OSA_BRANCH} --single-branch ${role_src} ${osa_repo_tmp_path}
      pushd ${osa_repo_tmp_path} > /dev/null
        git checkout --quiet origin/${OSA_BRANCH}
      popd > /dev/null

      # If there are releasenotes to copy, then copy them
      if $(ls -1 ${osa_repo_tmp_path}/releasenotes/notes/*.yaml > /dev/null 2>&1); then
        rsync -aq ${osa_repo_tmp_path}/releasenotes/notes/*.yaml releasenotes/notes/
      fi

      # Clean up the temporary files
      rm -rf ${osa_repo_tmp_path}
    fi

    # Now use the information we have to update the ansible-role-requirements file
    "$(dirname "${0}")/ansible-role-requirements-editor.py" -f ansible-role-requirements.yml -n "${role_name}" -v "${role_version}"

    unset role_version
  done
  echo "Completed updating ansible-role-requirements.yml"
else
  echo "Skipping the ansible-role-requirements.yml update as we're working on the master branch"
fi

# Update the release version in playbooks/inventory/group_vars/all.yml
# We don't want to be doing this for the master branch and we only want
# to do it once, so we key off of a specific repo source file name.
if [[ "${OSA_BRANCH}" != "master" ]] && [[ "${SERVICE_FILE}" == "playbooks/defaults/repo_packages/openstack_services.yml" ]]; then

  echo "Updating the release version..."
  currentversion=$(awk '/openstack_release:/ {print $2}' playbooks/inventory/group_vars/all.yml)

  # Extract the required version info
  major_version=$( echo ${currentversion} | cut -d. -f1 )
  minor_version=$( echo ${currentversion} | cut -d. -f2 )
  patch_version=$( echo ${currentversion} | cut -d. -f3 )

  # increment the patch version
  patch_version=$(( patch_version + 1 ))

  sed -i .bak "s/${currentversion}/${major_version}.${minor_version}.${patch_version}/" playbooks/inventory/group_vars/all.yml
else
  echo "Skipping the release version update as we're working on the master branch"
fi
