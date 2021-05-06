#/bin/sh
FILE=$1
FILE_DATE=$(date -r ${FILE} "+%Y-%m-%d")
sed -r "s/(^\s*"date"\s*\:\s*\")\<generation date\>(\"\s*,?\s*$)/\1${FILE_DATE}\2/"

