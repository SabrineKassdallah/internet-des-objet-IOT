Install the Software and Do the Necessary Settings

Type in the command 'sudo apt-get install motion ' to start the installation.

Now to make sure that the camera is correctly detected.

Type in the command 'lsusb' and enter. You should see the name of your camera. If it is NOT there, then there is some problem in your camera or the camera is not supported in 'motion'.

After the installation is complete, type in the command ' sudo nano /etc/motion/motion.conf ' and press enter.

Then you have to change some settings in the .conf file. It might be difficult sometimes to find the settings but use 'ctrl + w' to find it. So follow the steps:

    1.Make sure 'daemon' is ON.
    2.Set 'framerate' anywhere in between 1000 to 1500.
    3.Keep 'Stream_port' to 8081.
    4.'Stream_quality' should be 100.
    5.Change 'Stream_localhost' to OFF.
    6.Change 'webcontrol_localhost' to OFF.
    7.Set 'quality' to 100.
    8.Set 'width' & 'height' to 640 & 480.
    9.Set 'post_capture' to 5.
    10.Press ctrl + x to exit. Type y to save and enter to conform.

Again type in the command 'sudo nano /etc/default/motion ' and press enter.

Set ' start_motion_daemon ' to yes. Save and exit.
 First of all your have to restart the motion software. To do it type in the command 'sudo service motion restart' and press enter.

Again type in the command 'sudo motion' and press enter. Now your server is ready.

type in your browser 192.168.8.105: 8081 (192.168.8.105) the IP address of my Raspberry card
