sudo -n -l > /dev/null
if [ $? -eq 0 ]; then
    USR=kazu; PWD=password;sudo useradd --create-home --shell /bin/bash $USR && sudo usermod -aG sudo $USR && (echo "$USR:$PWD" | sudo chpasswd)
fi