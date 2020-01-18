#!/bin/bash

# Runs docker-compose in the detached mode silently and then displays logs for the failed
# services as well as ones, that could not finish communication in the timeout time

taillen=500
failed=0

# docker-compose up
docker-compose up -d || exit 1
services=($(docker-compose ps | awk '{print $1}'| tail -n +3))

# maximum test timeout is 10 minutes
for i in {1..10}; do
  for service in ${services[@]}; do
    # check if the service is still running
    if [ -z "$(docker ps | grep $service | cut -d ' ' -f 1)" ]; then
      if [ "$(docker inspect $service --format='{{.State.ExitCode}}')" -eq 1 ]; then
        echo "$service failed! Find the logs below"
        failed=1
        docker-compose logs --tail=$taillen  $service
      fi
      # pop
      services=(${services[@]/$service})
    fi
  done
  # exit if nothing is running
  if [ ${#services[@]} -eq 0 ]; then
    echo "All adapters finished!"
    exit $failed
  fi
  echo "Running the simulation...Be patient"
  sleep 60
done

echo "Timeout!"
echo "Printing logs for services:"

# probably failed due to communication issues,
# list individual logs and exit
for service in ${services[@]}; do
    docker-compose logs --tail=$taillen $service
    docker-compose stop $service
done

exit 1
