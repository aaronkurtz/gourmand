# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 80, host: 8080

  config.vm.synced_folder "./gourmand", "/srv/gourmand"

  config.vm.provision :ansible do |ansible|
    ansible.playbook = "ansible/vagrant.yml"
    # ansible.verbose = "vvv"
  end
end
