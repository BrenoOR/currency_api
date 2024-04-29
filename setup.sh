# Setup global environment

sudo dnf install -y docker
sudo service docker start
sudo chkconfig docker on

sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

sudo chmod +x ./docker-setup.sh

touch .env

echo Configure the entrypoint inserting the machine private ip in the indicated place.

echo Now configure the .env file, then run docker-setup.sh
echo See dot-env-example.md for more details:
cat dot-env-example.md
