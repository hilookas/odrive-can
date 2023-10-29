#!/bin/bash

# create a virtual vcan0 interface on each system boot

SERVICE_NAME="create_vcan0"
BASH_SCRIPT="/etc/systemd/system/$SERVICE_NAME.sh"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

# Check if the service already exists
if systemctl list-units --full -all | grep -Fq $SERVICE_NAME.service; then
    echo "Service already exists!"
else
    # Create the Bash script to set up vcan0
    echo "#!/bin/bash
modprobe vcan
ip link add dev vcan0 type vcan || true
ip link set up vcan0" | sudo tee $BASH_SCRIPT

    # Make the Bash script executable
    sudo chmod +x $BASH_SCRIPT

    # Create the systemd service file
    echo "[Unit]
Description=Create Virtual CAN Network
After=network.target

[Service]
ExecStart=$BASH_SCRIPT
Type=oneshot

[Install]
WantedBy=multi-user.target" | sudo tee $SERVICE_FILE

    # Reload systemd, enable and start the service
    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME.service
    sudo systemctl start $SERVICE_NAME.service

    echo "Service has been created and started!"
fi
