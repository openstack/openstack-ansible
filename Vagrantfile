Vagrant.configure(2) do |config|

  config.vm.define "ubuntu1604" do |xenial|
    xenial.vm.box = "ubuntu/xenial64"
    xenial.vm.provider "virtualbox" do |v|

      v.name = "OpenStack-Ansible_Ubuntu-16.04_#{Time.now.getutc.to_i}"
      v.memory = 8192
      v.cpus = 4

      image_path = "#{ENV["HOME"]}/VirtualBox VMs/#{v.name}"
      image_name = 'ubuntu-xenial-16.04-cloudimg'

      # We clone the image to a resizable format
      v.customize [
        "clonehd", "#{image_path}/#{image_name}.vmdk",
                   "#{image_path}/#{image_name}.vdi",
        "--format", "VDI"
      ]

      # Then resize it to 60 GB
      v.customize [
        "modifymedium", "disk",
        "#{image_path}/#{image_name}.vdi",
        "--resize", 60 * 1024
      ]

      # Then attach it as the primary disk
      v.customize [
        "storageattach", :id,
        "--storagectl", "SCSI Controller",
        "--port", "0",
        "--device", "0",
        "--type", "hdd",
        "--nonrotational", "on",
        "--medium", "#{image_path}/#{image_name}.vdi"
      ]

      # Then remove the original disk
      v.customize [
        "closemedium", "disk",
        "#{image_path}/#{image_name}.vmdk",
        "--delete"
      ]

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
    centos7.vm.provider "virtualbox" do |v|

      v.name = "OpenStack-Ansible_CentOS-7_#{Time.now.getutc.to_i}"
      v.memory = 8192
      v.cpus = 4

      image_path = "#{ENV["HOME"]}/VirtualBox VMs/#{v.name}"
      image_name = 'centos-7-1-1.x86_64'

      # We clone the image to a resizable format
      v.customize [
        "clonehd", "#{image_path}/#{image_name}.vmdk",
                   "#{image_path}/#{image_name}.vdi",
        "--format", "VDI"
      ]

      # Then resize it to 60 GB
      v.customize [
        "modifymedium", "disk",
        "#{image_path}/#{image_name}.vdi",
        "--resize", 60 * 1024
      ]

      # Then attach it as the primary disk
      v.customize [
        "storageattach", :id,
        "--storagectl", "IDE Controller",
        "--port", "0",
        "--device", "0",
        "--type", "hdd",
        "--nonrotational", "on",
        "--medium", "#{image_path}/#{image_name}.vdi"
      ]

      # Then remove the original disk
      v.customize [
        "closemedium", "disk",
        "#{image_path}/#{image_name}.vmdk",
        "--delete"
      ]

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
