# Portable Cardiac Triage System

TMU BioDesign's entry to the True North Biomedical Competition 2026-27.

**The challenge:** a portable device that measures **SpO₂, blood pressure and heart rate**, works without outside power or internet, fits different patient sizes, and shows a **High / Medium / Low** triage priority.

Deadlines, tasks and requirements live in **Notion**. This repo only stores our files.

## Where files go

| Folder | What goes in it | Subteam |
|---|---|---|
| `hardware/` | KiCad schematics and PCBs, one folder per board | Electrical |
| `lib/` | Our own KiCad symbols, footprints and 3D models | Electrical |
| `firmware/` | Code that runs on the microcontroller | Electrical / Software |
| `software/` | Code that runs on a computer (data logging, analysis, display) | Software |
| `mech/` | Enclosure, cuff and clip CAD | Mechanical |
| `docs/report/` | Design report drafts | Everyone |
| `docs/dfmea/` | Risk analysis (DFMEA) | Everyone |
| `docs/pitch/` | Pitch deck and budget | Everyone |

## New here?

Read **[docs/github-guide.md](docs/github-guide.md)**. It takes about 10 minutes, and you don't need any Git experience.

## The only 5 rules

1. **Work on your own branch, never directly on `main`.**
2. **Open a pull request** when your change is ready, and ask one teammate to look at it.
3. **Write a clear commit message**, like "Add SpO2 sensor to schematic", not "update".
4. **Electrical:** everyone uses **KiCad 10**. Files saved in a newer version can't be opened in an older one.
5. **Stuck or something looks broken? Ask your subteam lead.** Nothing in Git is lost for good, so don't panic.
