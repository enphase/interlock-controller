## External Contactor Box

To control devices without an interlock loop port, this box includes a mains-rated (240VAC) contactor powered from +24v.

This has an M12 pin connector pinned as:
- 1 (brown): +24v (switched) contactor control
- 3 (blue): 0v
- 2 (white): equipment-off interlock loop (readback) source (in)
- 4 (black): equipment-off interlock loop (readback) return (out)

For high current, this box has input and output NEMA L14-20 pigtails, plug on the input side and receptacle on the output side, connected via cable glands.
Suggested default: ~250mm pigtails.

For lower current (~10A), the box can have C13/C14 pigtails or panel-mountable connectors.

Parts selection:
- Contactor: 22.64.0.024.4717 (3NO + 1NC with mirror contact) or 3RT2026-1BB40 (3NO + NO and NC auxiliary contacts with mirror contact)
  - NO contacts used to switch line(s)
  - NC contact used for feedback
- Box: NBB-10260
  - Drill hit for AC in/out cable glands, as needed
  - Drill hit for 3d printed connector plate, ~20mm diameter round, with M3 mounting holes in 32x32mm pattern
    - 3d printed plate allows for anti-rotation feature and future interface changes
- DIN rail
- Terminal blocks to join grounds: PTFIX 2X4 GN, 1028364
- Terminal blocks to join neutrals (if present): PTFIX 2X4 WH, 1028366
