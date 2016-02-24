
Inspect volume:

    sudo docker run --volumes-from docker_fusekidata_1 --rm -it ubuntu bash

Clear all data:
	sudo docker-compose rm fusekidata
	sudo docker-compose up fusekidata

