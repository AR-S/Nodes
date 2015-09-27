### Setting up the Rpi


##### Enable X autostart

Edit `/etc/rc.local`

```
# Print the IP address
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  printf "My IP address is %s\n" "$_IP"
fi

# prevent screen from blanking after timeout
setterm -blank 0

# start X on LCD screen
su -l pi -c "env FRAMEBUFFER=/dev/fb1 startx &"

exit 0
```

##### Prenventing scren blanking

```$ sudo nano /etc/kbd/config```
Find the setting `BLANK_TIME=30` and change value to `0`, same with `POWERDOWN_TIME` setting.

##### Autostart script after X
Edit `/etc/xdg/lxsession/LXDE-pi/autostart`.


##### Installing Kivy

```
$ apt-get build-dep python-pygame
$ sudo pip install hg+http://bitbucket.org/pygame/pygame
```

See more here:
http://stackoverflow.com/questions/23204591/touchscreen-kivy-app-for-raspberry-pi

And official docu here:
http://kivy.org/docs/installation/installation-rpi.html
