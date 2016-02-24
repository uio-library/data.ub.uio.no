FROM stain/jena-fuseki

COPY config.ttl /jena-fuseki/config.ttl

CMD ["/jena-fuseki/fuseki-server", "--update", "--config", "config.ttl"]
