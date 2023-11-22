#!/bin/bash

# script to prepare system.
#



# Variables
user_name="pi"

# Install aptitude
apt-get update
apt-get install -y aptitude

# Setup passwordless sudo
echo "%sudo ALL=(ALL) NOPASSWD: ALL" | (EDITOR="tee -a" visudo)

# Create docker group
groupadd docker

# add user to docker group
sudo usermod -aG docker $user_name


# Change bash prompt for user
echo 'PS1=" 🐤 \[\e[1;32m\]\u@\h\[\e[0m\]:\[\e[1;34m\]\w\[\e[0m\]\$ "' >> /home/$user_name/.bashrc

# Disable password authentication for root
sed -i 's/^#?PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
systemctl reload sshd

# Update apt and install required system packages
apt-get install -y curl vim git ufw mc apt-transport-https ca-certificates software-properties-common python3-pip virtualenv python3-setuptools speedtest-cli

# install docker if not present
if ! command -v docker &> /dev/null; then
    # Install docker
    echo "Installing docker"
    curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
fi

# Set python3 as default
update-alternatives --install /usr/bin/python python /usr/bin/python3 10
