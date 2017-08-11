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
  echo "   > reload [name] - Remove, build and serve"
  # echo "   > stop - Stop the container"
  # echo "   > start - Start the container"
  echo "   > status [name] - Show status"
  # echo "   > remove - Remove containers"
  echo "   > help - Display this help"
  echo "   > varnishlog - Attach to varnishlog"
  echo "   > attach [name] - Attach to any container"
  echo "   > shell [name] - Start bash shell in running container"
  echo "   > cleanup - Cleanup dangling images"
  echo -e -n "$NORMAL"
  echo "-----------------------------------------------------------------------"

}

build() {
  log "build $EXTRAS"
  docker-compose build $EXTRAS

  [ $? != 0 ] && error "Docker image build failed !" && exit 100
}

up() {
  log "Starting all services"
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

  log "Force removing old version"
  docker-compose rm --force "$service"  # removes volumes as well

  log "Upping new version"
  docker-compose up -d "$service"

  containerid=$(docker-compose ps -q "$service" | cut -c 1-12)
  imageid=$(docker inspect -f {{.Image}} "$containerid" | cut -c 1-19)
  state=$(docker inspect -f {{.State.Running}} "$containerid")

  docker-compose logs --tail=10 "$service"

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
    EXTRAS=$(docker-compose config --services)
  fi
  for service in $EXTRAS; do
    containerid=$(docker-compose ps -q "$service" | cut -c 1-12)
    imageid=$(docker inspect -f {{.Image}} "$containerid" | cut -c 1-19)
    state=$(docker inspect -f {{.State.Running}} "$containerid")
    log "[$service]  Container: $containerid  Image: $imageid  Running: $state"
  done
  # docker ps -f "name=$IMAGE_NAME"
}

remove() {
  log "Removing previous containers"
  # docker rm -f $CONTAINER_NAME &> /dev/null || true
}

attach() {
  service="$EXTRAS"
  containerid1=$(docker-compose ps -q "$service" | cut -c 1-12)
  if [[ -z "$containerid1" ]]; then
    error "No active container found"
    exit 1
  fi
  log "Attaching to container ${containerid1}"
  docker exec -ti ${containerid1} bash

}

varnishlog() {
  service=fuseki_cache
  containerid1=$(docker-compose ps -q "$service" | cut -c 1-12)
  if [[ -z "$containerid1" ]]; then
    error "No active container found"
    exit 1
  fi
  log "Attaching to container ${containerid1}"
  docker exec -ti ${containerid1} varnishlog
}

shell() {
  if [[ -z "$EXTRAS" ]]; then
    error "Please specify a service"
    exit 1
  fi
  containerid1=$(docker-compose ps -q "$EXTRAS" | cut -c 1-12)
  if [[ -z "$containerid1" ]]; then
    error "No active container found"
    exit 1
  fi
  log "Starting bash shell in container ${containerid1}"
  docker exec -ti ${containerid1} env TERM=xterm bash -l
}

cleanup() {
  log "Removing dangling images..."
  docker images --no-trunc -q -f dangling=true | xargs -r docker rmi
}

if [[ "$#" -eq "0" ]]; then
  help
else
  $*
fi
