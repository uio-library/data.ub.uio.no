FROM stain/jena-fuseki:3.10.0

# RUN mkdir -p /fuseki/index && mkdir -p /fuseki/tdb
COPY start.sh shiro.ini config.ttl /jena-fuseki/

# Husk: signal forwarding: `init=true` i docker-compose.yml, eller `docker run --init`
CMD ["/jena-fuseki/start.sh"]
