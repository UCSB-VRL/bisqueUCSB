#!/bin/sh

if [ $# -lt  1 ]; then 
  echo "usage: isam2innodb.sh DBNAME <mysql args> i.e. -u -p "
  exit 
fi


DB=$1; shift

echo "converting tables to engine=InnoDB"
mysql $*  --database=$DB -e "show tables;" | tail --lines=+2 | xargs -i echo "ALTER TABLE \`{}\` ENGINE=INNODB;" > /tmp/alter_table.sql
mysql $* --database=$DB  < /tmp/alter_table.sql

echo "adding foreign key contraints"
mysql $* $DB < contrib/mysql/add-contraints.sql
