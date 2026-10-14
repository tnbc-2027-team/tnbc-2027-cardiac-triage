# Portable Cardiac Triage System

TMU BioDesign's entry to the True North Biomedical Competition 2026-27.

**The challenge:** a portable device that measures **SpO₂, blood pressure and heart rate**, works without outside power or internet, fits different patient sizes, and shows a **High / Medium / Low** triage priority.

Deadlines, tasks, documents and meeting notes live in **Notion** and Google Drive. This repo only stores technical files (KiCad, CAD, code).

## Where files go

| Folder | What goes in it | Subteam |
|---|---|---|
| `hardware/` | KiCad schematics and PCBs, one folder per board | Electrical |
| `lib/` | Our own KiCad symbols, footprints and 3D models | Electrical |
| `firmware/` | Code that runs on the microcontroller | Electrical / Software |
| `software/` | Code that runs on a computer (data logging, analysis, display) | Software |
| `mech/` | Enclosure, cuff and clip CAD | Mechanical |

## New here?

Read **[docs/github-guide.md](docs/github-guide.md)**. It takes about 10 minutes, and you don't need any Git experience.

## The only 5 rules

1. **Put your files in your subteam's folder** (see the table above).
2. **Always get the latest files before you start** (Fetch, then Pull in GitHub Desktop), and push when you're done.
3. **Write a clear commit message**, like "Add SpO2 sensor to schematic", not "update".
4. **Tell your subteam before you edit a shared KiCad board or CAD file.** Two people editing the same file at once will overwrite each other.
5. **Stuck or something looks broken? Ask your subteam lead.** Nothing in Git is lost for good, so don't panic.

Electrical: everyone uses **KiCad 10**. Files saved in a newer version can't be opened in an older one.
