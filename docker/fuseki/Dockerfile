FROM stain/jena-fuseki:3.4.0

# RUN mkdir -p /fuseki/index && mkdir -p /fuseki/tdb
COPY config.ttl /jena-fuseki/config.ttl

CMD ["/jena-fuseki/fuseki-server", "--update", "--config", "config.ttl"]
