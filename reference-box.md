## General notes
- Jumper wires 16cm long
- Long jumper wires 24cm long
  - Only used for the barrel jack to the distribution blocks
- Coil and terminate unused wires (M12 5th pins)
- The Phoenix relays we use have polarized coil pins. A1 is +V, A2 is GND. **This differs from the wiring diagram.**

## Top row: rails

Top row:
- Grey terminal block (1-wide) x as many as needed: these bridge the interlock prev (M12 black) to interlock next (M12 white)

Bottom row:
- White terminal block (3-wide): GND
  - All button GNDs (M12 blue) wired here 
- Blue terminal block (3-wide): +24
- Purple terminal block (3-wide): +24 RDY
  - The start button LED line (M12 brown) is connected here
- Orange terminal block (3-wide): +24 IC
  - The e-stop LED lines (M12 brown) are connected here

## Center rows: relays

- Relay K2: start latch
- Relay K4: tower light control
- Relay K5: open inverter
- Relay K6: interlock compare
- output relays
  - These should be mirror contact relays since the tower light uses the readback state

Relay GNDs are daisy chained for wiring simplicity

## Bottom row: barrel jack breakout

- Grey terminal block (1-wide) x 2: bridge the short barrel jack lead to a longer wire to the main distribution block on the top row
