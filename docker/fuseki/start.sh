#!/bin/sh

cp $FUSEKI_HOME/shiro.ini $FUSEKI_BASE/shiro.ini
# $ADMIN_PASSWORD can always override
if [ -n "$ADMIN_PASSWORD" ] ; then
  echo "Setting admin password"
  sed -i "s/^admin=.*/admin=$ADMIN_PASSWORD/" "$FUSEKI_BASE/shiro.ini"
fi
exec $FUSEKI_HOME/fuseki-server --update --config config.ttl

