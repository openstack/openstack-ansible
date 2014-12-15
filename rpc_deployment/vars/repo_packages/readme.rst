Ansible Openstack LXC Packages
##############################
:date: 2014-09-01 09:57
:tags: rackspace, lxc, openstack, cloud, ansible
:category: \*nix

Packages Downloads and Installables
===================================

Any and all packages that need to be installed for this repository to work
should be specified here in the, ``repo_packages`` directory. The files in 
this directory are given to plays as additional options.  The options have 
several default actions which are all processed by the following roles:
**package_source_archive**, **package_source_install**, 
**package_system_install**. Inside these files all download-able objects
such as tar-balls and random files should also be specified. While the packaging
roles may not be used to process these links the stated purpose of this 
directory is to have anything that is "installable" in a single location with
the goal to allow for easily manipulation of requirements as they change.

Defaults processed by the **package_source_archive**, 
**package_source_install**, **package_system_install** roles:
  * gpg_keys: ``list`` of ``hashes`` with keys: key_name, keyserver, hash_id.
  * apt_container_keys: ``list`` of ``hashes`` with keys: url, state
  * apt_container_repos: ``list`` of ``hashes`` with keys: repo, state
  * debconf_items: ``list`` of ``hashes`` with keys: question, name, value, vtype
  * run_policy_deny: ``boolean`` true or false: When installing container packages this ``boolean`` will drop a run level policy to ensure that no services are started upon installation.
  * repo_path: ``string`` used to set the "relative path" to an online repository without the domain name. also used as the target directory when downloading a given git repository.
  * git_repo: ``string`` URI to the git repo to clone from.
  * git_fallback_repo: ``string`` URI to an alternative git repo to clone from when **git_repo** fails.
  * git_dest: ``string`` full path to place a cloned git repository. This will normally incorporate the **repo_path** variable for consistency purposes.
  * git_install_branch: ``string`` branch, tag or SHA of a git repo to clone into.
  * git_repo_plugins: ``list`` of ``hashes`` with keys: path, package | This is used to install additional packages which may be installable from the same base repo.
  * pip_wheel_name: ``string`` pip package name to FIRST attempt installation of.
  * service_pip_dependencies: ``list`` of ``strings``.
  * container_packages: ``list`` of ``strings``.
  * apt_common_packages: ``list`` of ``strings``.
  * common_util_packages: ``list`` of ``strings``.
