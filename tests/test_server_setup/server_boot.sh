# Whatever this is it installs git, initiates a git repository, and creates users who are authenticated to push to the remote.
# Install git.
apk update && apk add git
# Initiate git repository.
git config --global user.email "babygitr@nomail.com"
git config --global user.name "babygitr"
git config --global init.defaultBranch main
mkdir git_repo
cd git_repo
git init
# Create users and auth methods.
adduser -D babygitr
# Username and password
echo 'babygitr:stupidpassword' | chpasswd
echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config
# Create some keys
cd /etc/ssh
ssh-keygen -A
cd
# Start the SSH server
/usr/sbin/sshd -D -e
