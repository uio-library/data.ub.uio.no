FROM stain/jena-fuseki:3.4.0

COPY config.ttl /jena-fuseki/config.ttl

CMD ["/jena-fuseki/fuseki-server", "--update", "--config", "config.ttl"]
