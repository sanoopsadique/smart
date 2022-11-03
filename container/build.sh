#!/usr/bin/env bash
if [ $# -eq 0 ]
  then
    echo Enter tag?
    read tag
    if [ $tag == '' ]
        then
            tag='latest'
    fi
  else
    tag=$1
fi

docker build -t sanoopsadique/smart:$tag .
echo Do you want to pull the image to docker hub - y/n:?
read choice
if [ $choice == 'y' ]
    then
        docker push sanoopsadique/smart:$tag
fi
    