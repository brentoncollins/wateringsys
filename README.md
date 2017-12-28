
### Install Information

Clone into the PI home DIR then move into the wateringsys directory and run the following commands to create two services which run the status every hour along with the pump timer.

## Clone into home dir
```
sudo git clone https://github.com/brentoncollins/wateringsys.git
```
## Move into dir and install
```
sudo python3 setup.py install
sudo apt-get install python3-pil.imagetk
```
## Run these commands to get the pump timer running as a service
```
sudo cp pumptimer.service /lib/systemd/system/
sudo cp status.service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/pumptimer.service
sudo chmod 644 /lib/systemd/system/status.service

sudo systemctl daemon-reload
sudo systemctl enable pumptimer.service
sudo systemctl enable status.service
sudo systemctl start pumptimer.service
sudo systemctl start status.service

```
### Usage Information

## Edit use data

You will have to sign up to a gmail account to send email notifications and also edit the data in email_data.txt

```
### Email Login ###
user_name@gmail.com
### Password ###
yourpassword
### To Email ###
to_email@email.com
```

## status.py
This will run the weather observation, speedtest-api plot and the water-level check every hour.
If you have run the commands to set this up as a service it will start when the RPI starts and run as a service
you will not have to run it when you start the RPI
## pumptimer.py
Once you have opened tk.py and set a timer for the pump, this will just output how long until the pump is going to run.
Once it runs it will set a new timer and wait for the next run.
Also if you have setup the service correctly this will run in the background as a service and you will not have to start it.
## tk.py
This is the HMI for the system, once it is all setup this is all you should need to run the pump and set new timers for the system.


### Preview of the system
Images.
https://imgur.com/a/Bo0ic

Video.
https://youtu.be/q598M7_Ar7A

More into I posted on reddit.
https://www.reddit.com/r/raspberry_pi/comments/7iljv2/rpi_watering_system_using_an_rpi_7_screen_water/


DISCLAIMER this is my first decent python project so im sure the code probably is not as pretty as it should be but it works :)
if you have any inprovment ideas or creative critisism please email me brentoncollins86@gmail.com

