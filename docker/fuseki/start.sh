#!/bin/sh

cp /jena-fuseki/shiro.ini /fuseki/shiro.ini
/jena-fuseki/fuseki-server --update --config config.ttl

