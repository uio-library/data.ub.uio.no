
## Init

    git submodule init
    git submodule sync

## Local development with Vagrant

	vagrant up
	vagrant plugin install vagrant-vbguest
	vagrant vbguest --do install


* Note: We can't set selinux security context for shared folders (see https://github.com/mitchellh/vagrant/issues/6970), so we need to the set permissive mode: `setenforce permissive` (or edit `/etc/selinux/config`). On the production server
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

	sudo su
	yum update
   	yum -y install   ntp ntpdate ntp-doc   gcc   gcc-c++   make   openssl-devel   libxml2-devel   libxslt-devel   python-devel   curl   gettext   httpd   vim   git   zip   python-setuptools   bash-completion   ctags

   	tee /etc/yum.repos.d/docker.repo <<-EOF
[dockerrepo]
name=Docker Repository
baseurl=https://yum.dockerproject.org/repo/main/centos/7
enabled=1
gpgcheck=1
gpgkey=https://yum.dockerproject.org/gpg
EOF

	yum update && yum install docker-engine
	service docker start

   	groupadd docker
   	usermod -aG docker ${USER}
   	service docker restart
   	\curl -sSL 'https://setup.ius.io/' | bash
   	\curl -sSL https://github.com/docker/compose/releases/download/1.6.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose
   	yum install -y php56u php56u-pgsql php56u-mbstring php56u-pdo php56u-gd php56u-ldap .    php56u-pecl-imagick php56u-curl php56u-apc
   	\curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer && chmod +x /usr/local/bin/composer
   	\curl -sS https://bootstrap.pypa.io/get-pip.py | python


   	mkdir /op/data.ub
	chown -R dmheggo:ub-wit /opt/data.ub
	git clone git@github.com:scriptotek/data.ub.uio.no.git /opt/data.ub
	chown -R dmheggo:ub-wit /opt/data.ub
   	cd /opt/data.ub
   	git checkout v2

Log out and in again to refresh group membership.

	docker version

SELinux

    chcon -Rv --type=httpd_sys_content_t /opt/data.ub/www
	setsebool -P httpd_can_network_connect 1

Crontab: Load from file:

	crontab crontab
