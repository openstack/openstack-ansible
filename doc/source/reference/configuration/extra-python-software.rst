Adding extra python software
============================

The system will allow you to install and build any package that is a python
installable. The repository infrastructure will look for and create any
git based or PyPi installable package. When the package is built the repo-build
role will create the sources as Python wheels to extend the base system and
requirements.

While the pre-built packages in the repository-infrastructure are
comprehensive, it may be needed to change the source locations and versions of
packages to suit different deployment needs. Adding additional repositories as
overrides is as simple as listing entries within the variable file of your
choice. Any ``user_.*.yml`` file within the "/etc/openstack_deployment"
directory will work to facilitate the addition of a new packages.


.. code-block:: yaml

    swift_git_repo: https://private-git.example.org/example-org/swift
    swift_git_install_branch: master


Additional lists of python packages can also be overridden using a
``user_.*.yml`` variable file.

.. code-block:: yaml

    swift_requires_pip_packages:
      - virtualenv
      - python-keystoneclient
      - NEW-SPECIAL-PACKAGE


Once the variables are set call the play ``repo-build.yml`` to build all of the
wheels within the repository infrastructure. When ready run the target plays to
deploy your overridden source code.
