[Unit]
Description=Info bot
After=multi-user.target
[Service]
Type=idle
ExecStart=./info_bot/start.sh
[Install]
WantedBy=multi-user.target