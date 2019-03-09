#!/bin/bash

service docker start
service docker status

docker pull instagramtools/web

echo "Composition docker stop /selenium"
docker stop /selenium
echo "Composition docker rm /selenium"
docker rm /selenium
echo "Composition start /selenium"
docker run -d --net=bridge --name selenium selenium/standalone-chrome:3.141.59

echo Composition Parameters: $@
INSTA_USER=$1
INSTA_PW=$2

echo "Composition docker stop /bot"
docker stop /bot
echo "Composition docker rm /bot"
docker rm /bot

SETTINGS='["\"{\\\"do_comment_enabled\\\":true,\\\"do_follow_enabled\\\":true,\\\"do_like_enabled\\\":true,\\\"enable_unfollow\\\":true,\\\"enable_follow_user_followers\\\":true,\\\"enable_like_by_feed\\\":false,\\\"enable_like_by_locations\\\":true,\\\"enable_like_by_tags\\\":true,\\\"enable_message\\\":true,\\\"unfollow_users_nonfollowers\\\":false,\\\"speed\\\":100,\\\"discount_code\\\":\\\"TeamDiscount\\\",\\\"like_by_tags\\\":[\\\"fitness\\\",\\\"girlswholift\\\",\\\"girlswillbegirls\\\",\\\"berlin\\\",\\\"munich\\\",\\\"m\\u00fcnchen\\\",\\\"frankfurt\\\",\\\"hamburg\\\",\\\"hannover\\\",\\\"businesswoman\\\",\\\"businessman\\\",\\\"gymlove\\\",\\\"foodspring\\\",\\\"fitnesslife\\\",\\\"motivation\\\",\\\"travel\\\"],\\\"follow_user_followers\\\":[\\\"christinabiluca\\\",\\\"christopherbark\\\",\\\"tobiasrtr\\\",\\\"johannesbartl\\\",\\\"johannes_haller\\\",\\\"johannes_luckas\\\",\\\"philipp_stehler\\\",\\\"raf_camora\\\",\\\"kollegahderboss\\\",\\\"patrickmadany\\\",\\\"danbilzerian\\\",\\\"antoniaelena.official\\\",\\\"tobilikee\\\"],\\\"follow_user_followers_amount\\\":\\\"3\\\",\\\"relationship_bounds_min_followers\\\":\\\"100\\\",\\\"relationship_bounds_max_followers\\\":\\\"5000\\\",\\\"relationship_bounds_min_following\\\":\\\"50\\\",\\\"relationship_bounds_max_following\\\":\\\"1000\\\",\\\"user_interact_amount\\\":\\\"3\\\",\\\"do_like_percentage\\\":\\\"70\\\",\\\"delimit_liking_min\\\":\\\"10\\\",\\\"delimit_liking_max\\\":\\\"500\\\",\\\"do_comment_percentage\\\":\\\"30\\\",\\\"comments\\\":[\\\":)\\\",\\\":))\\\",\\\"top!",":)\\\",\\\"looking","goo!",":)\\\",\\\"looking","good!","\\\",\\\"looks","good!",":)\\\",\\\"top!",":)\\\",\\\"nice","one",":)\\\"],\\\"delimit_commenting_min\\\":\\\"3\\\",\\\"delimit_commenting_max\\\":\\\"70\\\",\\\"do_follow_percentage\\\":15,\\\"unfollow_users_unfollow_after\\\":\\\"2\\\",\\\"location_names\\\":[\\\"Berlin,","Germany\\\",\\\"Hamburg,","Germany\\\",\\\"Frankfurt,","Germany\\\",\\\"Munich,","Germany\\\",\\\"Kiel\\\",\\\"Bremen,","Germany\\\",\\\"Ulm,","Germany\\\",\\\"Stuttgart,","Germany\\\",\\\"N\\u00fcrnberg\\\"],\\\"like_by_locations\\\":[\\\"213131048\\\",\\\"213110159\\\",\\\"72783909\\\",\\\"213359469\\\",\\\"784162920\\\",\\\"214227454\\\",\\\"222859765\\\",\\\"213128338\\\",\\\"4896942\\\"]}\""]'

CMD="docker run -d -v /home/ec2-user/logs:/root/InstaPy/logs -v /home/ec2-user/db:/root/InstaPy/db --net=bridge --link selenium:selenium -e bypass_suspicious_attempt=True -e bypass_with_mobile=True -e SELENIUM=selenium --name bot -e ENV=$SETTINGS -e INSTA_USER=$INSTA_USER -e INSTA_PW=$INSTA_PW instagramtools/web sh ./wait-for-selenium.sh http://selenium:4444/wd/hub -- python docker_quickstart.py"
echo Composition CMD: $CMD

$CMD