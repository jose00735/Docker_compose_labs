docker_images_id=$(docker image ls | awk '{ print $3 }' | grep -v IMAGE)

for id in $docker_images_id
do
    docker image rm -f $id
done
