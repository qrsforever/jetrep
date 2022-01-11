```sh
sudo systemctl stop gdm3
sudo systemctl disable gdm3
sudo systemctl set-default multi-user.target
sudo apt remove --purge -y chromium-browser
sudo apt remove --purge -y ubuntu-desktop gdm3
sudo apt remove --purge -y unity-scopes*
sudo apt remove --purge -y gnome-*
sudo apt remove --purge -y lightdm*
sudo apt autoremove -y
sudo reboot
```
