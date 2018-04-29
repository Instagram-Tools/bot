#!/bin/bash
# start-bot.sh

docker stop /$1
docker rm /$1

docker-compose run --name $1 -e INSTA_USER=$1 -e INSTA_PW=$2 $3 web
