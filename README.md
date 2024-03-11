# solax_tesla
A very specific project to use the wifi dongle on a x3 mic pro g2 solax inverter, to obtain solar information that then informs a script on whether to start tesla charging

# Set-up

To use this script the following is needed:
- A twillio account
- A Tesla refresh token https://tesla-info.com/tesla-token.php
- A x3 mic pro g2 solax inverter, using a wifi 3 dongle, and the url/password for this
- A Iphone with the Tesla app installed/your car linked

Enter variables as they fit in the credentials.json file

The Iphone will need to create two shortcuts, one for when it receives a "start" message to start charging, and
another for when it receives a "stop" message to stop charging.

# Credits
@squishykid's solax project's helped me translate the 100 length array returned from the inverter into useable values: https://github.com/squishykid/solax/tree/master
