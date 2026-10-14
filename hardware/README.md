# Hardware (Electrical)

One folder per board, for example `hardware/triage-main/`.

## Start a new board

1. Make a folder `hardware/<board-name>/`.
2. Copy the two files from `hardware/_new-board-template/` into it. They connect the board to our team library in `lib/`.
3. In KiCad 10: **File → New Project** and save it in that folder as `<board-name>.kicad_pro`.

## Before you push

GitHub checks your schematic (ERC) and PCB (DRC) automatically every time you push. If you get an email that the check failed, open the **Actions** tab on GitHub to see why.

Also look over these yourself:

- [ ] Every chip has its power pins connected and its decoupling capacitors
- [ ] New symbols checked pin by pin against the datasheet
- [ ] LEDs, diodes, electrolytic caps and connectors face the right way
- [ ] Anything touching the patient (SpO₂ sensor, electrodes) is isolated or current-limited
- [ ] Board size, mounting holes and connector positions agreed with Mechanical
- [ ] Track widths fit the current, especially the pump and valve drivers
- [ ] Board name and revision on the silkscreen
