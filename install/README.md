## Odrive configuration


Setup odrive for use with can.

**use host system**, to avoid excessive container restart on device reconnects.

### Preparation

1. `install_rules.sh` on **host system**
2. connect odrive. Power odrive with 5V, connect usb.
3. (optional for vcan) run `setup_vcan_service.sh` to create `vcan0` adapter. It will be started on each startup.


Odrive should become available as usb device:

```
$ lsusb | grep 1209
Bus 001 Device 014: ID 1209:0d32 Generic ODrive Robotics ODrive v3

```


### Configuration

Start devcontainer, odrive tool is installed automatically.

Configure odrive as described in [manual](https://docs.odriverobotics.com/v/0.5.6/can-guide.html)


## SBC with can hat setup

1. run `prepare_system.sh`
2. prepare can hat as explained in [waveshare hat docs](https://www.waveshare.com/wiki/2-CH_CAN_HAT)
    - modify `boot/config.txt`
    - run `install_bcm2835.sh`
    - run `setup_can.sh` , this will start can interfaces on startup.


## Test connection

* `candump can0 -xct z -n 10`
* `python3 -m can.viewer -c "can0" -i "socketcan"`
