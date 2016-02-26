

## Local development with Vagrant

	vagrant up
	vagrant plugin install vagrant-vbguest
	vagrant vbguest --do install


* Note: We can't set selinux security context for shared folders (see https://github.com/mitchellh/vagrant/issues/6970), so we need to the set permissive mode: `setenforce permissive`. On the production server
we will have enforcing mode.

* Note: `sendfile()` is not reliable with Vagrant shared folders. Therefore, set `EnableSendfile off` in apache conf. Ref: https://coderwall.com/p/ztskha/vagrant-apache-nginx-serving-outdated-static-files-turn-off-sendfile

	cd /opt/data.ub/docker
	docker-compose up -d

	cd /opt/data.ub

	git clone git@github.com:realfagstermer/mrtermer.git \
		&& cd mrtermer \
		&& sudo pip install -r requirements.txt \
		&& cd ..

	git clone git@github.com:realfagstermer/realfagstermer.git \
		&& cd realfagstermer \
		&& sudo pip install -r requirements.txt \
		&& cd ..

## Production

Centos 7 with selinux

    git clone ... /opt/data.ub
    chcon -Rv --type=httpd_sys_content_t /opt/data.ub/www
