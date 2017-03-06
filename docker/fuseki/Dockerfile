FROM stain/jena-fuseki:2.5.0

COPY config.ttl /jena-fuseki/config.ttl

CMD ["/jena-fuseki/fuseki-server", "--update", "--config", "config.ttl"]
