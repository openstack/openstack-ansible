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

# Verify whether required plugins are installed.
required_plugins = [ "vagrant-disksize" ]
required_plugins.each do |plugin|
  if not Vagrant.has_plugin?(plugin)
    raise "The vagrant plugin #{plugin} is required. Please run `vagrant plugin install #{plugin}`"
  end
end

Vagrant.configure(2) do |config|

  # Configure all VM specs.
  config.vm.provider "virtualbox" do |v|
    v.memory = 12288
    v.cpus = 4
  end

  config.vm.synced_folder ".", "/vagrant", type: "rsync"

  # Configure the disk size.
  disk_size = "60GB"

  config.vm.define "ubuntu1804" do |bionic|
    bionic.vm.box = "ubuntu/bionic64"
    bionic.disksize.size = disk_size
    config.vm.provision "shell",
      privileged: true,
      inline: <<-SHELL
          cd /vagrant
          ./scripts/gate-check-commit.sh
      SHELL
  end

  config.vm.define "centos7" do |centos7|
    centos7.vm.box = "centos/7"
    centos7.disksize.size = disk_size
    # The CentOS build does not have growroot, so we
    # have to do it ourselves.
    config.vm.provision "shell",
      privileged: true,
      inline: <<-SHELL
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

  config.vm.define "opensuse423" do |leap423|
    leap423.disksize.size = disk_size
    leap423.vm.box = "opensuse/openSUSE-42.3-x86_64"
    leap423.vm.provision "shell",
      # NOTE(hwoarang) The parted version in Leap 42.3 can't do an online
      # partition resize so we must create a new one and attach it to the
      # btrfs filesystem.
      privileged: true,
      inline: <<-SHELL
        cd /vagrant
        echo -e 'd\n2\nn\np\n\n\n\nn\nw' | fdisk /dev/sda
        PART_END=$(fdisk -l /dev/sda | grep ^/dev/sda2 | awk '{print $4}')
        resizepart /dev/sda 2 $PART_END
        btrfs fi resize max /
        ./scripts/gate-check-commit.sh
      SHELL
  end

  config.vm.define "opensuse150" do |leap150|
    leap150.disksize.size = disk_size
    leap150.vm.box = "opensuse/openSUSE-15.0-x86_64"
    leap150.vm.provision "shell",
      privileged: true,
      inline: <<-SHELL
        cd /vagrant
        zypper -qn in gdisk
        echo -e 'x\ne\nw\ny\n' | gdisk /dev/sda
        parted -s /dev/sda unit GB resizepart 3 100%
        btrfs fi resize max /
        ./scripts/gate-check-commit.sh
      SHELL
  end

end
