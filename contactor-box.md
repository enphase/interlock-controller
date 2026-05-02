## External Contactor Box

To control devices without an interlock loop port, this box includes a mains-rated (240VAC) contactor powered from +24v.

This has an M12 pin connector pinned as:
- 1 (brown): +24v contactor control
- 3 (blue): 0v
- 2 (white): equipment-off interlock loop (readback) source (in)
- 4 (black): equipment-off interlock loop (readback) return (out)

This box has input and output NEMA L6-30 pigtails, socket on the input side and receptacle on the output side, connected via PG16 (or as-sized-to-cables) cable glands.
Suggested default: ~250mm pigtails

Parts selection:
- Contactor: 22.64.0.024.4717 (3NO + 1NC with mirror contact)
  - NO contacts used to switch lines
  - NC contact used for feedback
- Box: NBB-10260
  - Drill hit for AC in/out cable glands, as needed
  - Drill hit for 3d printed connector plate, 40mm diameter round, with M3 mounting holes in 32x32mm pattern
    - 3d printed plate allows for anti-rotation feature and future interface changes
- DIN rail
- Terminal blocks to join grounds: PTFIX 2X4 GN, 1028364
