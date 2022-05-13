<h1>Explanation</h1>

<h2>To do</h2>

<h2>Prerequisites</h2>

* MySQL server
* RabbitMQ server

<h2>Set up</h2>

<h3>Pi-Server</h3>

The queue_listener script is run as a systemd service to ensure that it is always running. Validate that you have systemd on your device by running:
```
systemd --version
```
Create a new queue_listener.service file
```
sudo nano /etc/systemd/system/queue_listener.service 
```
Enter the following in the new file.
```
[Unit]
Description= queue_listener
Requires=rabbitmq-server.service
After=rabbitmq-server.service

[Service]
Type=simple
Restart=always
WorkingDirectory=/home/<user>/../Pi-Project
User=<user>
ExecStart=python3 /home/<user>/../Pi-Project/Pi-Server/queue_listener.py

[Install]
WantedBy=multi-user.target
```
Run below commands to enable, start it and check its status. The service will restart every time the device is rebooted.
```
sudo systemctl daemon-reload
sudo systemctl enable queue_listener.service 
sudo systemctl start queue_listener.service 
sudo systemctl status queue_listener.service 
```


<h3>Pi-Node</h3>

Crontab is used to run read_and_send.py once every 5 min. Edit the crontab by running:
```
crontab -e
```
Validate that the path to read_and_send.py is correct for your device.
```
*/5 * * * * <your path>/read_and_send.py
```
Save and exit the crontab
