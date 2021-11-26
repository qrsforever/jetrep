
## Wifi AP

    https://github.com/oblique/create_ap/

    nmcli dev wifi list
    sudo nmcli device wifi connect 国电社区 password 88888888

    sudo nmcli device wifi hotspot ifname wlan0 con-name jethotspot ssid jetap password 12345678

    sudo nmcli connection add type wifi ifname wlan0 con-name jethotspot autoconnect no ssid jetap ip4 192.168.1.1/24
    sudo nmcli connection modify jethotspot 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared
    sudo nmcli connection modify jethotspot wifi-sec.key-mgmt wpa-psk
    sudo nmcli connection modify jethotspot wifi-sec.psk 12345678
    sudo nmcli connection up id jethotspot
    sudo nmcli connection show jethotspot

    https://blog.csdn.net/adocir/article/details/113877200
    https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/158-raspberry-pi-auto-wifi-hotspot-switch-direct-connection

## Journalctl

    https://blog.csdn.net/agg7911/article/details/101137030


## Nvidia

1. [加速: 实战 | 硬编解码技术的AI应用][1]


## Gstreamer

1. [GStreamer Pipeline Samples: GOP][2]

2. [I-Frame / P-Frame / B-Frames][3]

3. [Settings for GOP structure(group of pictures)][4]


## Other

1. [Pyudev][5]

    six >= 1.13; pyudev > 0.22

[5]: https://github.com/pyudev/pyudev
[4]: https://docs.aws.amazon.com/mediaconvert/latest/ug/gop-structure.html
[3]: https://ottverse.com/i-p-b-frames-idr-keyframes-differences-usecases/
[2]: https://docs.rocos.io/prod/docs/gstreamer-pipeline-samples#native-camera-peripherals
[1]: https://www.163.com/dy/article/G4C1C33T0538BXGY.html
