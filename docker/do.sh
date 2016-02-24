#!/usr/bin/env bash

EXTRAS="${*:2}"

# Output colors
NORMAL="\\033[0;39m"
RED="\\033[1;31m"
BLUE="\\033[1;34m"

log() {
  echo -e "$BLUE > $1 $NORMAL"
}

error() {
  echo ""
  echo -e "$RED >>> ERROR - $1$NORMAL"
}

help() {
  echo "-----------------------------------------------------------------------"
  echo "                      Available commands                              -"
  echo "-----------------------------------------------------------------------"
  echo -e -n "$BLUE"
  echo "   > build [name] - To build all the Docker images (or just one)"
  echo "   > up - Up all services"
  echo "   > reload - Remove, build and serve"
  echo "   > stop - Stop the container"
  echo "   > start - Start the container"
  echo "   > status - Show status"
  echo "   > remove - Remove containers"
  echo "   > help - Display this help"
  echo -e -n "$NORMAL"
  echo "-----------------------------------------------------------------------"

}

build() {
  log "build $EXTRAS"
  docker-compose build $EXTRAS

  [ $? != 0 ] && error "Docker image build failed !" && exit 100
}

up() {
  log "Solr serve"
  docker-compose up -d

  [ $? != 0 ] && error "Serve failed !" && exit 105
}

reload_service() {
  service=$1
  log "Reloading $1"
  containerid1=$(docker-compose ps -q "$service" | cut -c 1-12)
  if [[ -z "$containerid1" ]]; then
    error "Image not found"
    exit 1
  fi
  imageid1=$(docker inspect -f {{.Image}} "$containerid1" | cut -c 1-10)
  state1=$(docker inspect -f {{.State.Running}} "$containerid1")
  # log "Container id: $containerid1, image id: $imageid1, running: $state1"

  docker-compose build "$service"
  docker-compose stop "$service"
  docker-compose rm --force "$service"  # removes volumes as well
  docker-compose up -d "$service"

  containerid=$(docker-compose ps -q "$service" | cut -c 1-12)
  imageid=$(docker inspect -f {{.Image}} "$containerid" | cut -c 1-10)
  state=$(docker inspect -f {{.State.Running}} "$containerid")

  log "Service reloaded"
  log "Container id: $containerid1..$containerid"
  log "Image id: $imageid1..$imageid"
  log "Running: $state1..$state"
 #   log "Started at: $(docker inspect -f {{.State.StartedAt}} $CONTAINER_NAME)"
}

reload() {
  if [[ -z "$EXTRAS" ]]; then
    error "Please specify a service"
    exit 1
  fi
  for SERVICE in $EXTRAS; do
    reload_service "$SERVICE"
  done
}

status() {
  if [[ -z "$EXTRAS" ]]; then
    error "Please specify a service"
    exit 1
  fi
  for service in $EXTRAS; do
    containerid=$(docker-compose ps -q "$service" | cut -c 1-12)
    imageid=$(docker inspect -f {{.Image}} "$containerid" | cut -c 1-10)
    state=$(docker inspect -f {{.State.Running}} "$containerid")
    log "Container id: $containerid, image id: $imageid, running: $state"
  done
  # docker ps -f "name=$IMAGE_NAME"
}

remove() {
  log "Removing previous containers"
  # docker rm -f $CONTAINER_NAME &> /dev/null || true
}

if [[ "$#" -eq "0" ]]; then
  help
else
  $*
fi
