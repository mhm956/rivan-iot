#!/usr/bin/env bash

sudo apt update
sudo apt install mysql-server python3-dev

# Use if you need to connect to the database from a remote machine
# sudo ufw allow mysql

# Enable the service to start on reboot
sudo systemctl start mysql
sudo systemctl enable mysql

echo "You will need to set the password manually from here"
sudo /usr/bin/mysql -u root -p

# INSERT INTO mysql.user (User,Host,authentication_string,ssl_cipher,x509_issuer,x509_subject)
#    VALUES('demouser','localhost',PASSWORD('demopassword'),'','','');
# GRANT ALL PRIVILEGES ON *.* to <your-user>@localhost;
# FLUSH PRIVILEGES;

echo "Exiting setup script for mysql"

# If we go with the mysqlclient-python lib
sudo apt-get install python3-dev default-libmysqlclient-dev
pip3 install mysqlclient

In [2]: engine = sa.create_engine('mysql+mysqldb://demouser:demopassword@127.0.0.1:3306')
