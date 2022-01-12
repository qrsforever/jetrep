```sh
sudo systemctl stop gdm3
sudo systemctl disable gdm3
sudo systemctl set-default multi-user.target
sudo apt remove --purge -y docker*
sudo apt remove --purge -y chromium-browser thunderbird fonts-noto-cjk containerd snapd
sudo apt remove --purge -y ubuntu-desktop gdm3 lightdm*
sudo apt remove --purge -y unity-scopes*
sudo apt remove --purge -y gnome-shell gnome-calculator gnome-accessibility-themes
sudo apt autoremove -y

sudo rm /etc/apt/sources.list.d/*

sudo reboot
```
