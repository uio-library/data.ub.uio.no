
# https://groups.google.com/forum/#!topic/docker-user/2dP09wrq5Qk
#
# Make sure we're not confused by old, incompletely-shutdown httpd
# context after restarting the container.  httpd won't start correctly
# if it thinks it is already running.
LOCKFILE=/run/apache2/apache2.pid
rm -rf $LOCKFILE

/usr/sbin/apache2ctl -DFOREGROUND
