# laser-comm
Interstellar communications with a laser and arduino

## Basic Idea

Powerful laser beams can penetrate the Earth's atmosphere and travel far into space, providing an effective means of communication for hobbyists and space agencies alike. This project is a hobbyist's attempt to explore the current state of the technology required to send signals into space over interstellar distances. Specifically, I am interested in technology which is available to hobbyists, does not require licences or permits from government agencies to use and costs no more than a hundred US dollars.

----
It has been established by experiments conducted on International Space Station (ISS) that a 1 Watt blue laser beam sent from the surface of the earth not only reaches space, but is powerful enough to be seen by the naked human eye. See Scott Manley's great video on this:  
[![Can You See A Laser Pointer From The Space Station?](http://img.youtube.com/vi/DCQ2CbfGs6g/0.jpg)](http://www.youtube.com/watch?v=DCQ2CbfGs6g "Can You See A Laser Pointer From The Space Station?")

## Know-how

There are a few things to know about when starting this project. 

### Problem: The danger of lasers

Lasers are extremely dangerous for all kinds of life forms, especially if pointed directly in the eyes. Typically, a laser pointer has a power output of \~1 mW. This power is not enough to send a signal into space (or to blind someone). As mentioned earlier, a laser of power about 1 watt or higher is sufficient although theoretically, we could use a much lower power. A calculation can be made to find the minimum power of the laser such that a certain amount of light escapes into space, given the absorbance characteristics of the earth's atmosphere. Such calculations are straightforward, but are not presented here, since very high power lasers are available online, which means that we are not scratching the bottom of this threshold, even as a hobbyist. However, at such high powers of 1 W or more, the laser is powerful enough to make someone blind instantly if it were pointed directly in their eyes. While it is in use, the laser may get knocked off or pushed by a person, animal or just due to wind or the cable may get yanked off for any number of reasons. All of these could potentialy lead to a fatal accident.


### Solution: Motion detection circuit
To make sure that Murphy does not mess things up, I designed a circuit which consists of a MPU 6050 accelerometer and gyroscope and an arduino.
The arduino (basically, an ATMega 328P chip, with arduino bootloader) constantly monitors the reading of the MPU 6050 and if a sudden motion is detected, the laser is instantly shut off.

### Problem: Communication protocol
Supposing that the laser is safe enough to use, the next step is to think about communication. I am specifically focusing on lasers which are meant to be used in CNCs and laser cutters etc. These lasers accept a TTL signal. The output of the laser is adjusted as per the ampltiude and frequency characteristics of the TTL signal. So, we can easily modulate the intensity of the laser. The second type of communication we should think about is interstellar. How should we encode the information we are sending, so that a civilization which detects it can decode it?\* 

### Solution: Half-duplex UART protocol
Since the lasers we are using are basically cheap, low quality ones, we cannot encode information in other properties of the light beam such as phase or polarization of even fancier: angular momentum. All we can do is modulate the intensity of the beam. The signal may be very weak when it reaches the receiver, so it is preferable to modulate the intensity in a digital binary pattern, rather than some analog form. So, given that we are using a binary transmitter and the receiver would not understand what the heck is being transmitted, we should use a protocol that is as simple as possible to decode. The simplicity and robustness of the UART protocol makes it ideal for use in such communication. The protocol contains a start and stop bit and encodes the byte within these two (we consider the case without any parity bits). Thus, anyone looking at a binary pattern of UART signals would notice the periodicity and that the data between the two start/stop bits varies. Thus, I expect that a completely alien civilization can establish the concept of data packet used in UART protocol. The next detail to consider is the baud rate. CNC/cutting lasers I found on the internet would typically have a maximum modulation frequency of 10KHz 20 20 KHz. The one I am using advertises 20 KHz, but I have no way to verify this. To be safe, I used a baud rate of 9600. This is extremely slow, but I expect that most lasers can keep up with this baud rate. Finally, a minor detail is that this communication will be half-duplex, meaning that we will not be receiving any data from the aliens. If you can establish a full-duplex comm channel with aliens, please let me know.

\*I should mention here that the odds of some civilization intercepting our signal are astronomically small, but that's a minor detail for us optimists.

### Problem: Mechanical stability
Even if a circuit (basically the MPU sensor) is working, we still need to make sure that it faithfully represents the true motion of the laser. For that, the circuit needs to be mechanically rigidly attached to the laser. There are two problems associated with this. First, all good high-power lasers have fans, which are constantly running. This presents a large source of noise for the sensor since the fan is attached directly to the laser. Second, even with the fan attached, the laser gets quite hot. Thus, it is not advisable to attach the motion detection circuit directly to the laser since that would block the airflow from the laser and also potentially damage the motion detection circuit. These are small problems by comparison.

### Solution: 3D printed mount
The solution is to mechanically isolate the (laser+fan) from the circuit enough to attenuate the vibrations from the fan but still be bind the circuit to the laser rigidly. This requires an adapter. So, I designed an adapter which accommodates both the laser and the circuit, but isolates them enough so that vibrations from the fan do not overwhelm the MPU 6050. The residual vibration from the fans can be measured and a threshold can be set in the code, so that fan vibrations are ignored.

## Strategy
If you decide to build this project, some specific details of your may differ from mine, so I am outlining the basic steps I performed to get everything working.

- Buy a powerful laser online (I got mine from Amazon)
- Build a circuit on breadboard to test the performance of MPU 6050.
- Write code for arduino performing safety check.
- Write code to send data from computer to laser.
- Design a PCB to emulate the breadboard design. This makes sure that the circuit is robust and there are no hanging wires as in a breadboard.

I ended up using two ATMega chips: one for minitoring the motion and one for communication with the computer over bluetooth (with a HC-05 bluetooth module). Thus, my PCB design has two chips. This is done so that there is as little lag as possible between the detection of motion and halting of the laser output. This is just a precaution on my part. It is okay to let one chip handle both these tasks if you are confident that no matter what your code will halt the laser within some acceptable latency.

## Circuit
Here is what my PCB looks like.

![Front Side](https://github.com/dataplayer12/laser-comm/blob/master/images/pcb.png)
The PCB design files are in `pcb` directory in Eagle format. The gerber files are in a `zip` file and can be uploaded to your PCB provider's website to be manufactured. I ordered mine from JLCPCB.

## Holder
Here is the 3D design for the holder. The base holds the laser using the M3 size mounting holes while the pillars hold the PCB (also via M3 screws). The center of the base has mounting hole for a quarter-inch tripod screw. So, the whole laser assmebly can be mounted on a tripod, making it easier to aim the beam anywhere.

![Holder](https://github.com/dataplayer12/laser-comm/blob/master/images/holder.png)

The STL file is in the `holder` directory. I printed the holder with PLA using typical parameters for this material at 15% infill on a FlashForge printer.

## Code
- The code for the two arduinos is in `laser_safety` and `laser_transmitter` directories.
- The script `stream_live_video.py` can be used to transmit pictures taken from the webcam on your computer to the laser (using a bluetooth module). Since we are using a baud rate of 9600, we can't transmit the video in real time, but it's kind of cool to stream snapshots of your weekend party into outer space.
- The directory `mindwave` contains some experimental scripts to send EEG data (brain waves) from a NeuroSky Mindwave 2 to the laser. This allows you to attach an EEG reader to your head and transmit your brain waves into outer space! This part of the project is still under development.

## Results
It works!

### Hailing the Chandrayaan-2 lander
Here I am sending a sentence "Hello Vikram! Please respond" to the approximate location where India's Chandrayaan-2 moon mission hard-landed. It did not respond.

![moon](https://github.com/dataplayer12/laser-comm/blob/master/images/moon.jpeg)

### Sending a selfie to betelgeuse
Betelgeuse is an extrenely interesting star. There are probably no planets around betelgeuse and almost certainly no intelligent life, but this maverick star could go supernova in the ≈600 years that it takes light to reach there from Earth. Even if it doesn't, it's kind of cool to have your selfie zip through a massive star. It is possible that the large gravitational effect of the star will cause the laser light to bend around it and go somewhere else. Now that I think about it, it would be interesting to calculate the effect that betelgeuse's gravitational field would have on the timing of the UART signals being sent. I will do that calculation once I learn general relativity.

![betelgeuse](https://github.com/dataplayer12/laser-comm/blob/master/images/betelgeuse.jpeg)