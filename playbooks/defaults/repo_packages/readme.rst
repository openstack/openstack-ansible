Packages built by python from git
#################################
:date: 2014-09-01 09:57
:tags: python, pip, wheel, lxc, openstack, cloud, ansible
:category: \*nix

Packages Downloads and Installable
==================================

Any and all packages that need to be installed for this repository to work should be specified here in the, ``repo_packages`` directory. The files in this directory are given to the python wheel builder for construction. 

Inside these files all download-able objects such as tar-balls and random files should also be specified. While the packaging roles may not be used to process these links the stated purpose of this directory is to have anything that is "installable" in a single location with the goal to allow for easily manipulation of requirements as they change.

NOTICE on items in this file:
  * If you use anything in the "*._git_install_branch" field that is not a TAG 
    make sure to leave an in-line comment as to "why".

For the sake of anyone else editing this file: 
  * If you add clients to this file please do so in alphabetical order.
  * Every entry should be name spaced with the name of the client followed by an "_"

The basic structure of all of these files:
  * git_repo: ``string`` URI to the git repository to clone from.
  * git_fallback_repo: ``string`` URI to an alternative git repository to clone from when **git_repo** fails.
  * git_dest: ``string`` full path to place a cloned git repository. This will normally incorporate the **repo_path** variable for consistency purposes.
  * git_install_branch: ``string`` branch, tag or SHA of a git repository to clone into.
  * git_repo_plugins: ``list`` of ``hashes`` with keys: path, package | This is used to install additional packages which may be installable from the same base repository.
