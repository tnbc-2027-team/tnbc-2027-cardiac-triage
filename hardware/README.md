# Hardware (Electrical)

One folder per board, for example `hardware/triage-main/`.

## Start a new board

1. Make a folder `hardware/<board-name>/`.
2. Copy the two files from `hardware/_new-board-template/` into it. They connect the board to our team library in `lib/`.
3. In KiCad 10: **File → New Project** and save it in that folder as `<board-name>.kicad_pro`.

## Before asking for a review

GitHub checks your schematic (ERC) and PCB (DRC) automatically on every pull request. If the check fails, open the "Details" link on the pull request to see why.

Also look over these yourself:

- [ ] Every chip has its power pins connected and its decoupling capacitors
- [ ] New symbols checked pin by pin against the datasheet
- [ ] LEDs, diodes, electrolytic caps and connectors face the right way
- [ ] Anything touching the patient (SpO₂ sensor, electrodes) is isolated or current-limited
- [ ] Board size, mounting holes and connector positions agreed with Mechanical
- [ ] Track widths fit the current, especially the pump and valve drivers
- [ ] Board name and revision on the silkscreen

## Before ordering

- Check the fab's current capabilities (JLCPCB or PCBWay) and set them in **File → Board Setup**.
- Order from files on `main` that passed the checks, and have a second person check the order before paying.
- Add the order to the Live Bill of Materials in Notion.
