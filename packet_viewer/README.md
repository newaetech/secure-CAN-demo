# Secure Can Demo

This demo was created to showcase Correlation Power Analysis (CPA) attacks on CAN buses using AES for encryption and authentication.

## Getting Started

### Required Hardware
* 2 CW308 Boards
* 2 CW308 Target Boards with CAN headers (STM32F3 only, for now)
* 2 CANoodlers
* Something to perform CPA attacks with (CW Lite, CW Pro, etc)
* Something that outputs an analog voltage level (the adjustable regulator on the CW308 boards will work fine for this)
* Something to view a PWM output (the LEDs on the CW308 boards will work)

### Optional Extras
If you want to view the packets being sent over the CAN bus, this project includes two ways to do that:
* To a computer using a USB/CAN adapter
* To a Raspberry PI using a SPI/CAN adapter

### Hardware Setup
[Detailed instructions (including pictures)] (www.google.ca)
* Attach target boards to CW308s
* Attach target boards to CANoodlers
* Attach CANoodlers to each other
* Turn termination to on on both CANoodlers
* Connect your analog voltage source (3.3V max) to PB14/MISO pin on one CW308. This will be your throttle device
  * If you're using the adjustable regulator on the CW308, switch VADJ SRC to 3.3V)
  * The VADJ output is on pin ???
* Connect your PWM viewing device to PA11/GPIO3 on the other CW308. This will be your master device
  * If you want to use the CW308 LEDS for this, connect PA11/GPIO3 to LED 1, 2, or 3

### Firmware Setup
* Upload the throttle firmware (firmware/