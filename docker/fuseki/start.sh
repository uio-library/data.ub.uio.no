#!/bin/sh

cp /jena-fuseki/shiro.ini /fuseki/shiro.ini
exec /jena-fuseki/fuseki-server --update --config config.ttl

