# Team KiCad library

Parts we drew ourselves or changed. For common parts (resistors, capacitors, standard connectors), use KiCad's built-in libraries.

| Folder | Contents |
|---|---|
| `symbols/team.kicad_sym` | Our symbols |
| `footprints/team.pretty/` | Our footprints |
| `3d/` | 3D models, named the same as their footprint |
| `symbols/Espressif.kicad_sym`, `footprints/Espressif.pretty/` | Espressif's official ESP32 library (see below) |

When you add a part:

- Fill in **Datasheet** (a link), **MPN** (manufacturer part number) and **LCSC** (if ordering from JLCPCB).
- Ask someone else to check the pins against the datasheet before it's used on a board.

Parts and costs are tracked in the **Live Bill of Materials** in Notion.

## Parts in the team library

| Symbol | Footprint | Part |
|---|---|---|
| `team:AD8232` | `team:AD8232` | SparkFun AD8232 heart rate monitor module (SEN-12650) |
| `team:MAX30102` | `team:MAX30102` | MAX30102 SpO₂ / heart-rate breakout module |
| `team:XIAO_ESP32C3` | `team:XIAO-ESP32-C3-DIP` (or `-DIP-SMD`) | Seeed Studio XIAO ESP32C3. The battery pins (B+, B-) have no pads on these footprints |

## Espressif library (ESP32)

`Espressif` is a copy of Espressif's official KiCad library, version 3.1.0, from https://github.com/espressif/kicad-libraries. It is licensed under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), so changes to these files must stay under the same license and keep this credit. It covers ESP32, -S2, -S3, -C3, -C5, -C6, -H2 and -P4 modules and DevKits.

The 3D models are not included (about 250 MB). To see them in the 3D viewer, install **Espressif Library** from KiCad's **Plugin and Content Manager**.
