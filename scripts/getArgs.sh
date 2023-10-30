#!/bin/bash

display_container_info() {
    CONTAINER_NAME=$1
    CONTAINER_ID=$(docker ps -qf "name=${CONTAINER_NAME}")
    if [ ! -z "$CONTAINER_ID" ]; then
        NETWORK_NAME=$(docker inspect $CONTAINER_ID | jq -r '.[0].NetworkSettings.Networks | keys[0]')
        echo -n "$(docker inspect $CONTAINER_ID | jq -r ".[0].NetworkSettings.Networks.${NETWORK_NAME}.IPAddress") "
        echo -n "$(docker inspect $CONTAINER_ID | jq -r ".[0].NetworkSettings.Networks.${NETWORK_NAME}.MacAddress") "
    else
        echo "Container ${CONTAINER_NAME} not found!"
    fi
}

display_container_info demo-ftp_client-1
display_container_info demo-vsftpd_server-1
