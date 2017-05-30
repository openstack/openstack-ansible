Vagrant.configure(2) do |config|

  config.vm.define "ubuntu1604" do |xenial|
    xenial.vm.box = "ubuntu/xenial64"
    # Expand the disk to 60GB. You'll need
    # the plugin disksize. Please run:
    # vagrant plugin install vagrant-disksize
    xenial.disksize.size = '60GB'
    xenial.vm.provider "virtualbox" do |v|

      v.memory = 8192
      v.cpus = 4

      # Now we can execute the build
      config.vm.provision "shell", inline: <<-SHELL
        sudo su -
        cd /vagrant
        ./scripts/gate-check-commit.sh
      SHELL

    end
  end

  config.vm.define "centos7" do |centos7|
    centos7.vm.box = "centos/7"
    centos7.disksize.size = '60GB'
    centos7.vm.provider "virtualbox" do |v|

      v.memory = 8192
      v.cpus = 4

      # Now we can execute the build
      config.vm.provision "shell", inline: <<-SHELL
        sudo su -
        cd /vagrant
        PART_START=$(parted /dev/sda --script unit MB print | awk '/^ 3 / {print $3}')
        parted /dev/sda --script unit MB mkpart primary ${PART_START} 100%
        parted /dev/sda --script set 4 lvm on
        pvcreate /dev/sda4
        vgextend VolGroup00 /dev/sda4
        lvextend -l +100%FREE /dev/mapper/VolGroup00-LogVol00
        xfs_growfs /dev/mapper/VolGroup00-LogVol00
        ./scripts/gate-check-commit.sh
      SHELL

    end
  end

end
