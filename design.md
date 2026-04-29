## External Connections

### Sensors

- 2x emergency stop switch w/ red light
  - This light indicates when the interlock is closed (output live)
- 1x magnetic door switch
- 1x start button w/ green light
  - This light indicates when the interlock is ready (output not live, but can be started by pushing this button)
  - Both e-stop lights AND start lights are on when the interlock is closed (output live).

### Output

- 1x dry contact output, connected to the test equipment interlock port
- 1x tower light
  - red = interlock closed (output live)
  - green = interlock open
  - no lights on or both lights on = invalid state
- Lights on e-stop and pushbuttons


## Interface definition

Inputs and outputs use M12 connectors, 4 or 5 pin versions, A-code.
For maximum compatibility, where not otherwise constrained, we use M12 4-position pins and M12 5-position sockets.

Outputs (eg, dry contact) are M12 sockets, while inputs (eg, sensors) are M12 pins.

The general pinning is, as consistent with IEC 60947‑5‑2:
- 1 (brown): +24v
- 3 (blue): 0v
- 2 (white): signal 1 (interlock loop source)
- 4 (black): signal 2 (interlock loop return)
- 5: disconnected where not used

Specific pinnings:
- For the e-stop: pin 1 (+24) is the interlock-closed +24v signal, which powers the e-stop light. 0v is always present.
- For the start button: pin 1 (+24) is the interlock-ready +24v signal, which powers the start button light. 0v is always present.
- For the tower light, if using M12 connectors: signal 1 is red, signal 2 is green (polarity dependent on the tower light configuration). 24v and 0v are always present.

Part selections:
- M12 5-position socket 0.2m pigtail: T4171310005-001
- M12 4-position pin 0.2m pigtail: T4171210004-001
- M12 5-position pin 0.2m pigtail (if needed): T4171210005-001
- Cables: M12A05ML-12AFL-Sx00x


## Power Entry

Power entry consists of one fused C13 power entry connector.

Part selections:
- C13 with fuse: 719W-00/02
- Fuse: 5x20mm fuse:
  - 250mA slow: 0034.3111
  - 500mA fast: 0034.1513


## Electrical architecture

Internal wiring color conventions for terminal blocks and non-connector-pigtail wires ([source](https://industrialmonitordirect.com/blogs/knowledgebase/24v-dc-control-wiring-wire-color-codes-ul-en-standards)):
- Blue: +24v
- White: 0v
- Purple: interlock-ready +24v
- Orange: interlock-closed +24v
- Grey: general signal


- 24v architecture, as is common for industrial automation.
- Interlock loop starts at 24v and goes through (through and back) all the sensor ports, ending in the interlock-ready +24v rail.
  - This feeds the start button LEDs.
- The interlock loop then goes through the parallel combination of the start button and a relay that is powered by the interlock-closed +24v signal, ending in the interlock-closed +24v signal.
  - This provides latching-trip, push-to-reset functionality.
  - This feeds the e-stop switch LEDs.
- The interlock-closed +24v powers the force-guided relays (FGRs) that provide independent dry contact outputs per output.
- The force-guided channel from the output relay controls the tower lights.
  - The tower light RED is connected to ALL of the FGR NOs.
  - The tower light GREEN is connected to ALL of the FGR NCs.
  - The FGR common is connected to 0v (for a common-anode tower light).
  - Structurally, the tower light indicates output state, it should be consistent with the e-stop light in the absence of faults.
  - A single relay failure can lead to an inconsistent state with both red and green LEDs active, which is an invalid state requiring repairs.

Part selections:
- 120->24 converter: HDR-30-24
- Standard relay: Phoenix 2903342
- Force-guided relay: Phoenix 2908215
- Terminal blocks: PTFIX series
  - 6-position blue: 3002761 PTFIX 6X1,5 BU
  - 6-position white: 3002778 PTFIX 6X1,5 WH
    - 12-position white: 3002779 PTFIX 12X1,5 WH
  - 6-position purple: 3002784 PTFIX 6X1,5 VT
  - 6-position orange: 3002792 PTFIX 6X1,5 OG
  - 6-position grey: 3002757 PTFIX 6X1,5 GY
    - 2-position grey (eg, to join two pigtail wires): 1045923 PTFIX 2X1,5 GY
  - DIN rail adapter: 1049497 PTFIX 1,5-NS35 


## External devices

- Box, 1-position (e-stop only): FB1W-111Y
  - 3d printed adapter to adapt to T-slot framing
- Box, 2-position (e-stop and start button): FB2W-211Z
- E-stop switch: PBES22L114R
  - Emergency stop label ring: HWAV-27-Y
- Start button: A22NL-BGM-TGA-G100-GC
- Door magnetic sensor: https://www.amazon.com/dp/B0BCYHBKVF
  - 3d printed adapter to adapt to T-slot framing 
- M12 adapter: https://www.amazon.com/dp/B0C2N777YG
  - 3d printed threaded endcap to retain the flange on the sensor cable 
- Tower light: https://www.amazon.com/dp/B09X14DK9M (common anode +12/+24v; yellow, blue, and buzzer channels unused and reserved for future expansion)
