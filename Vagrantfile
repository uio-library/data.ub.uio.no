# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.require_version ">= 1.6.0"

Vagrant.configure(2) do |config|

  config.vm.box = "centos/7"
  config.ssh.insert_key = false
  config.ssh.forward_agent = true

  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--memory", 4096]
  end

  config.vm.hostname = "vm-uxl"
  config.vm.network :private_network, ip: "192.168.20.100"

  # Main provision script
  config.vm.provision :shell, path: "provision.sh"

  # We need to launch httpd after vagrant has mounted the synced folders,
  # and we need to set SELinux into permissive mode since we can't add contexts
  # to a Vagrant synced folder.
  config.vm.provision :shell, :inline => "setenforce permissive && service httpd start", run: "always"


  config.vm.synced_folder ".", "/vagrant", disabled: true

  config.vm.synced_folder "apache", "/opt/data.ub/apache"

  config.vm.synced_folder "docker", "/opt/data.ub/docker"

  config.vm.synced_folder "www", "/opt/data.ub/www",
    owner: "vagrant",
    group: "apache",
    mount_options: ["dmode=755", "fmode=664"]

end
