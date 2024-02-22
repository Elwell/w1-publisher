# w1-publisher
Dallas 1-Wire to MQTT temperature publisher

## Why another 1-wire parser?
Most of the existing ones I've found require owfs or only read the temperature
sensors serially. I explicitly wanted something that could make use of the bulk read feature in the kernel w1_therm module. 

More details at https://docs.kernel.org/w1/slaves/w1_therm.html

## Configuration
Update the MQTT server IP address and any requrements for auth.

This publisher includes a sample MQTT discovery configuration for a home assistant temperature sensor. Please adapt as required.
