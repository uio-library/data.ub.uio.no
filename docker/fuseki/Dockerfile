# FROM stain/jena-fuseki:3.7.0
FROM ghcr.io/danmichaelo/jena-fuseki:4.3.2

# RUN mkdir -p /fuseki/index && mkdir -p /fuseki/tdb
COPY start.sh shiro.ini config.ttl /jena-fuseki/

CMD ["/jena-fuseki/start.sh"]
