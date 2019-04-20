#!/usr/bin/env bash
# Copyright 2015, Rackspace US, Inc.
# Copyright 2017, SUSE LINUX GmbH.
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

###### HOOKS ########
# The following hooks can be defined in the user scripts. All hooks accept the
# following parameters:
#
# 1: repository name
# 2: OpenStack service branch
# 3: OSA branch
# 4: repository address
#
#osa_pre_sync_hook: Actions to be performed before copying updated files to OSA OpenStack services repositories
osa_pre_sync_hook() { true; }
#osa_post_sync_hook: Actions to be performed after copying updated files to OSA OpenStack services repositories
osa_post_sync_hook() { true; }

###### HELPER FUNCTIONS ######
osa_helper_cleanup_files() {
  [[ $# > 0 ]] && rm -rf "${@}"
}

osa_helper_clone_os_package() {
  local repo_name="${1}"
  local os_branch="${2}"
  local os_branch_sha"${3}"
  local repo_address="${4}"
  local os_repo_tmp_path="/tmp/os_${repo_name}"

  osa_helper_cleanup_files ${os_repo_tmp_path}
  # Do a shallow clone of the OpenStack repo to work with
  if git clone --quiet --depth=10 --branch ${os_branch} --no-checkout --single-branch ${repo_address} ${os_repo_tmp_path}; then
    pushd ${os_repo_tmp_path} > /dev/null
    git checkout --quiet ${os_branch_sha}
    popd > /dev/null
    return 0
  fi
  return 1
}

osa_helper_clone_osa_role() {
    local repo_name="${1}"
    local osa_branch="${2}"
    local osa_repo_address="${3:-https://opendev.org/openstack/openstack-ansible-os_${repo_name}}"
    local osa_repo_tmp_path="/tmp/osa_${repo_name}"

    osa_helper_cleanup_files ${osa_repo_tmp_path}
    # Do a shallow clone of the OSA repo to work with
    if git clone --quiet --depth=10 --branch ${osa_branch} --single-branch ${osa_repo_address} ${osa_repo_tmp_path}; then
      pushd ${osa_repo_tmp_path} > /dev/null
      git checkout --quiet origin/${osa_branch}
      popd > /dev/null
      return 0
    fi
    return 1
}

####### MAIN FUNCTIONS #######

#
# Updates SHAs for OSA roles and OpenStack repo packages.
#
sync_roles_and_packages() {
  local repo_name repo_address branch_data branch_sha branch_entry osa_repo_tmp_path os_repo_tmp_path
  local os_branch="${1}"; shift
  local osa_branch="${1}"; shift
  local service_file="${1}"; shift
  local openstack_service_list="$@"
  local osa_repo_address="https://opendev.org/openstack/openstack-ansible-os_${repo_name}"

  IFS=$'\n'

  # Iterate through the service file
  for repo in $(grep 'git_repo\:' ${service_file}); do
    # Set the repo name
    repo_name=$(echo "${repo}" | sed 's/_git_repo\:.*//g')
    local osa_repo_tmp_path="/tmp/osa_${repo_name}"
    local os_repo_tmp_path="/tmp/os_${repo_name}"

    echo -e "\nInspecting ${repo}..."

    # Set the repo address
    repo_address=$(echo ${repo} | awk '{print $2}')

    # Get the branch data
    branch_data=$(git ls-remote ${repo_address} | grep "${os_branch}$")

    # If there is no branch data, move to the next role
    [ -z "${branch_data}" ] && continue

    # Set the branch sha for the head of the branch
    branch_sha=$(echo "${branch_data}" | awk '{print $1}')

    # Set the branch entry
    branch_entry="${branch_sha} # HEAD of \"$os_branch\" as of $(date +%d.%m.%Y)"

    # Write the branch entry into the repo_packages file
    sed -i.bak "s|${repo_name}_git_install_branch:.*|${repo_name}_git_install_branch: $branch_entry|" ${service_file}

    # If the repo is not in the specified list, then move to the next role
    ! [[ "${openstack_service_list}" =~ "${repo_name}" ]] && continue

    if osa_helper_clone_os_package ${repo_name} ${os_branch} ${branch_sha} ${repo_address}; then
      if osa_helper_clone_osa_role ${repo_name} ${osa_branch}; then

        # pre-sync user hook
        osa_pre_sync_hook ${repo_name} ${os_branch} ${osa_branch} ${repo_address}

        # We have implemented tooling to dynamically fetch the
        # api-paste and other static/template files from these
        # repositories, so skip trying to update their templates
        # and static files.
        local static_file_repo_skip_list=( ceilometer gnocchi keystone )

        # Check if this repo is in the static file skip list
        local skip_this_repo="no"
        for skip_list_item in "${static_file_repo_skip_list[@]}"; do
          if [[ "${repo_name}" == "${skip_list_item}" ]]; then
            skip_this_repo="yes"
          fi
        done

        if [[ "${skip_this_repo}" != "yes" ]] && [[ -e "${os_repo_tmp_path}/etc" ]]; then
          # Update the policy files
          find ${os_repo_tmp_path}/etc -name "policy.json" -exec \
            cp {} "${osa_repo_tmp_path}/templates/policy.json.j2" \;

          # Tweak the paste files for any hmac key entries
          find ${os_repo_tmp_path}/etc -name "*[_-]paste.ini" -exec \
            sed -i.bak "s|hmac_keys = SECRET_KEY|hmac_keys = {{ ${repo_name}_profiler_hmac_key }}|" {} \;

          # Tweak the barbican paste file to support keystone auth
          if [[ "${repo_name}" == "barbican" ]]; then
            find ${os_repo_tmp_path}/etc -name "*[_-]paste.ini" -exec \
              sed -i.bak "s|\/v1\: barbican-api-keystone|\/v1\: {{ (barbican_keystone_auth \| bool) \| ternary('barbican-api-keystone', 'barbican_api') }}|" {} \;
          fi

          # Tweak the gnocchi paste file to support keystone auth
          if [[ "${repo_name}" == "gnocchi" ]]; then
            find ${os_repo_tmp_path}/etc -name "*[_-]paste.ini" -exec \
              sed -i.bak "s|pipeline = gnocchi+noauth|pipeline = {{ (gnocchi_keystone_auth \| bool) \| ternary('gnocchi+auth', 'gnocchi+noauth') }}|" {} \;
          fi

          # Update the paste files
          find ${os_repo_tmp_path}/etc -name "*[_-]paste.ini" -exec \
            bash -c "name=\"{}\"; cp \${name} \"${osa_repo_tmp_path}/templates/\$(basename \${name}).j2\"" \;

          # Update the yaml files for Heat
          if [[ "${repo_name}" == "heat" ]]; then
            find ${os_repo_tmp_path}/etc -name "*.yaml" -exec \
              bash -c "name=\"{}\"; cp \${name} \"${osa_repo_tmp_path}/templates/\$(echo \${name} | rev | cut -sd / -f -2 | rev).j2\"" \;
          fi
        fi

        # We have to check for rootwrap files in *all* service repositories
        # as we have no dynamic way of fetching them at this stage.
        if [[ -e "${os_repo_tmp_path}/etc" ]]; then

          # Tweak the rootwrap conf filters_path (for neutron only)
          if [[ "${repo_name}" == "neutron" ]]; then
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
          mkdir -p ${osa_repo_tmp_path}/files/rootwrap.d
          find ${os_repo_tmp_path}/etc -name "*.filters" -exec \
            bash -c "name=\"{}\"; cp \${name} \"${osa_repo_tmp_path}/files/rootwrap.d/\$(basename \${name})\"" \;

        fi

        # post-sync user hook
        osa_post_sync_hook ${repo_name} ${os_branch} ${osa_branch} ${repo_address}

        osa_helper_cleanup_files ${osa_repo_tmp_path} ${os_repo_tmp_path}
      fi
    fi

    echo -e "Processed $repo_name @ $branch_entry\n"

  done

  unset IFS
}

#
# Updates global requirement pins for pip, setuptools and wheel
#
update_pip_options() {
  PIP_CURRENT_OPTIONS=$(./scripts/get-pypi-pkg-version.py -p pip setuptools wheel -l horizontal)

  for pin in ${PIP_CURRENT_OPTIONS}; do
    sed -i.bak "s|^$(echo ${pin} | cut -f1 -d=).*|${pin}|" global-requirement-pins.txt
  done

  echo "Updated global requirement pins"
}

#
# Updates ansible-role-requirements file SHAs
#
update_ansible_role_requirements() {
  local role_name role_version osa_repo_tmp_path role_git_sources current_source_dir
  local osa_branch=${1}
  local pre_release=${2}
  local force_master=${3}
  current_source_dir="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"

  # Update the ansible-role-requirements.yml file
  if [ "${osa_branch}" != "master" ] || \
      [ "${pre_release}" == "true" ] || \
      [ "${force_master}" == "true" ]; then
    echo "Updating ansible-role-requirements.yml"

    if [ "${pre_release}" == "true" ]; then
      role_git_sources=$(awk '/src: .*/ {print $2}' ansible-role-requirements.yml)
    else
      role_git_sources=$(awk '/src: .*\/openstack\// {print $2}' ansible-role-requirements.yml)
    fi

    # Loop through each of the role git sources, only looking for openstack roles
    for role_src in ${role_git_sources}; do

      # Determine the role's name
      role_name=$(sed 's/^[ \t-]*//' ansible-role-requirements.yml | awk '/src: / || /name: / {print $2}' | grep -B1 "${role_src}" | head -n 1)
      echo "... updating ${role_name}"

      # If the role_src is NOT from opendev.org, try to get a tag first unless we are working on master
      if [[ ${role_src} != *"opendev.org"* ]] && [[ "${force_master}" != "true" ]]; then
        role_version=$(git ls-remote --tags ${role_src} | awk '{print $2}' | grep -v '{}' | cut -d/ -f 3 | sort --version-sort | tail -n 1)
      fi

      # Grab the latest SHA that matches the specified branch
      if [[ -z "${role_version}" ]]; then
        role_version=$(git ls-remote ${role_src} | grep "${osa_branch}$" | awk '{print $1}')
      fi

      # If we are forcing master and we still don't have a role_version defined, then we need
      # to fallback to master branch
      if [[ -z "${role_version}" ]] && [[ "${force_master}" == "true" ]]; then
        role_version=$(git ls-remote ${role_src} | grep /master$ | awk '{print $1}')
      fi

      # For OSA roles, get the release notes
      if [[ ${role_src} == *"opendev.org"* ]]; then
        local osa_repo_tmp_path="/tmp/osa_${role_name}"

        osa_helper_clone_osa_role $role_name $osa_branch $role_src

        # If there are releasenotes to copy, then copy them
        if $(ls -1 ${osa_repo_tmp_path}/releasenotes/notes/*.yaml > /dev/null 2>&1); then
          rsync -aq ${osa_repo_tmp_path}/releasenotes/notes/*.yaml releasenotes/notes/
        fi

        osa_helper_cleanup_files $osa_repo_tmp_path
      fi

      # Now use the information we have to update the ansible-role-requirements file
      "$current_source_dir/ansible-role-requirements-editor.py" -f ansible-role-requirements.yml -n "${role_name}" -v "${role_version}"

      unset role_version
    done
    echo "Completed updating ansible-role-requirements.yml"
  else
    echo "Skipping the ansible-role-requirements.yml update as we're working on the master branch"
  fi
}

update_release_version() {
    local osa_branch=${1}
    local service_file=${2}

    # Update the release version in group_vars/all/all.yml
    # We don't want to be doing this for the master branch and we only want
    # to do it once, so we key off of a specific repo source file name.
    if [[ "${osa_branch}" != "master" ]] && [[ "${service_file}" == "playbooks/defaults/repo_packages/openstack_services.yml" ]]; then

      echo "Updating the release version..."
      currentversion=$(awk '/openstack_release:/ {print $2}' group_vars/all/all.yml)

      # Extract the required version info
      major_version=$( echo ${currentversion} | cut -d. -f1 )
      minor_version=$( echo ${currentversion} | cut -d. -f2 )
      patch_version=$( echo ${currentversion} | cut -d. -f3 )

      # increment the patch version
      patch_version=$(( patch_version + 1 ))

      sed -i .bak "s/${currentversion}/${major_version}.${minor_version}.${patch_version}/" group_vars/all/all.yml
    else
      echo "Skipping the release version update as we're working on the master branch"
    fi
}
