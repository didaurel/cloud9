#!/bin/sh
set -e
LIB=$(dirname "$(readlink -f "$0")")
CLOUD=$LIB/..;
CONFD=$CLOUD/conf.d
CONF=$CONFD/cloud9.conf
source $CONF
source $CONFD/$1.conf
cd $DIR;[ -d $REPO ]||mkdir $REPO;cd $REPO;set +e;rm *;mkdir RESOURCES;mv resources/patches RESOURCES/;
mv resources/site.make RESOURCES/
mv resources/composer.json RESOURCES/
rm -r docs/ resources/ src/ tests/;
set -e
composer create-project ec-europa/subsite temp dev-master --no-interaction
set +e
mv temp/* .
rmdir temp/
if [ ! -d lib/modules/custom ];then 
	mkdir lib/custom/;mv lib/modules/* lib/custom;mv lib/custom/features lib/features;
	mv lib/custom lib/modules;mv lib/features lib/modules;
fi;
mv RESOURCES/* resources/
rmdir RESOURCES
set -e
#read -p "FILE (default Developer configuration file: build.develop.props) = " FILE
FILE=${FILE:-build.develop.props}
echo FILE=$FILE>>$CONF
#echo "project.url.base = https://$ENVIRONMENT_ID.vfs.cloud9.$REGION_ID.amazonaws.com/$REPO/$SITE">>$FILE
echo "project.url.production = $URL">>$FILE
echo "project.id = $SITE">>$FILE
echo "project.name = Subsite $SITE">>$FILE
echo "platform.package.version = $VERSION">>$FILE
echo "db.host = 127.0.0.1">>$FILE
echo "share.path = /tmp/cache">>$FILE
echo "phpcs.reports = full">>$FILE
echo "behat.formatter.name = pretty">>$FILE
echo "db.dl.password = $ASDA">>$FILE
echo 'db.dl.username = ${project.id}'>>$FILE
echo 'db.name = ${project.id}'>>$FILE
#echo 'behat.base_url = ${project.url.base}'>>$FILE
rm resources/composer.lock;
cd $DIR/$REPO;
phing build-platform;
phing build-subsite-dev;phing install-$2
#sed -i "/ec2-user/s/\/home\/ec2-user\/environment\/$REPO\/build\///" build/sites/default/settings.php
