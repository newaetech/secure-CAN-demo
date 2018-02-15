# Secure Can Demo

This demo was created to showcase Correlation Power Analysis (CPA) attacks on CAN buses using AES for encryption and authentication.

## Getting Started

### Required Hardware
* 2 CW308 Boards
* 2 CW308 Target Boards with CAN headers (STM32F3 only, for now)
* 2 CANoodlers
* Something to perform CPA attacks with (CW Lite, CW Pro, etc)
* Something that outputs an analog voltage level (must output no higher than 3.3V. The adjustable regulator on the CW308 boards will work fine for this)
* Something to view a PWM output (the LEDs on the CW308 boards will work)

### Optional Extras
If you want to view the packets being sent over the CAN bus, this project includes two ways to do that:
* To a computer using a USB/CAN adapter
* To a Raspberry PI using a SPI/CAN adapter and another CANoodler
In addition to the above adapters, you'll also need a splitter to split the CAN bus

### Hardware Setup
[Detailed instructions including pictures](www.google.ca)
* Attach target boards to CW308s
* Attach target boards to CANoodlers
* Attach CANoodlers to each other
* Turn termination to on on both CANoodlers
  * Note that there should be exactly two terminations on the CAN bus. If you have another device on the bus, make sure it's not terminated
* Connect your analog voltage source (3.3V max) to PB14/MISO pin on one CW308. This will be your throttle device
  * If you're using the adjustable regulator on the CW308, switch VADJ SRC to 3.3V
  * The VADJ output is on the pin right next to the VADJ potentiometer.
* Connect your PWM viewing device to PA11/GPIO3 on the other CW308. This will be your master device
  * If you want to use the CW308 LEDS for this, connect PA11/GPIO3 to LED 1, 2, or 3

### Firmware Setup
* Depending on the voltage range of your voltage input, you may need to modify the firmware
  * The firmware supplied with this project works with the CW308 adjustable regulator (A-B mV) 
  * Change VTHROT_MAX and VTHROT_MIN (both in millivolts) at the top of firmware/secure-can-demo/secure-can.c to values for your input
  
  This project uses the same build system as [Chipwhisperer](www.google.ca). By default, this project builds for the master device and STM32F3 hardware. New firmware can be built in firmware/secure-can-demo using the following command:
  ``` make ISMASTER=NO ```
  
* Upload the throttle firmware (firmware/secure-can-demo/throttle.hex) to your throttle device
  * Uploading firmware can be done through a debugger or through a CWLite
  * Uploading instructions for the STM32F3 are described [here](www.google.ca)
  
* Upload the master firmware (firmware/secure-can-demo/master.hex) to your master device

### CPA Attack Details
* The algorithm to encrypt and authenticate are shown [here](www.google.ca)
* To aid in CPA attacks, the trigger pin is set high while running through AES. If you want to remove this, remove trigger_high() and trigger_low() from seccan.c encrypt and decrypt functions
* The STM32F3s look for an external clock before falling back on the internal one. If you want to supply an external clock (say from a CWLite), this clock must be 8MHz.

## Setting Up Packet Viewing
If you have the optional hardware described earlier, you can use your computer to view what's happening on the CAN bus.

### Hardware Setup
* Use splitter to split the CAN bus off from the two CANoodlers
* Attach the free end of the splitter to your USB/CAN adapter or your extra CANoodler
* If you're using the USB/CAN adapter, connect it to your computer
* If you're using the Raspberry PI with SPI/CAN adapter connect it to your CANoodler 

### Software
This repo comes with a simple GUI that will decrypt/authenticate the info being sent over the CAN bus. It also separates the data being sent by the throttle from other data on the bus.
To run, navigate to packet_viewer/ and run:
```python testside.py```
The top row displays what's being sent from throttle to master. The rest of the rows cycle through other packets sent on the bus. The connect button will connect to the CAN bus, while the disconnect button will disconnect.
The current status of the connection is shown in the top of the window.