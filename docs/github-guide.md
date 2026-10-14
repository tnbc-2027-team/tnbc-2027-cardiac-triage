# GitHub in 10 minutes

Think of the repo as a shared Google Drive folder that keeps every old version. You don't need the command line. Use **GitHub Desktop**, a free app that does everything with buttons.

## One-time setup

1. Make a GitHub account and send your username to your subteam lead so they can add you.
2. Accept the invite email from GitHub.
3. Install **GitHub Desktop** (desktop.github.com) and sign in.
4. In GitHub Desktop: **File → Clone repository**, pick `tnbc-2027-cardiac-triage`, and choose a folder on your computer.

You now have the team's files in a normal folder on your computer.

## Every time you work

1. **Get the latest files.** Open GitHub Desktop, click **Fetch origin**, then **Pull origin** if it appears.
2. **Do your work** in your subteam's folder, using KiCad, your CAD tool or your code editor. Save as usual.
3. **Commit.** GitHub Desktop lists the files you changed. Write a short summary of what you did (bottom left) and click **Commit to main**.
4. **Push.** Click **Push origin**. Your teammates can now get your changes.

That's it. Do steps 1 and 4 at least once a day so everyone has the latest files.

## Good to know

- **Push says it was rejected?** Someone pushed before you. Click **Pull origin**, then **Push origin** again.
- **Two people editing the same KiCad board or CAD file at once** doesn't work. Git can't combine them, and one person's work gets overwritten. Tell your subteam before you start on a shared file.
- **Big CAD files** (STEP, SolidWorks, Fusion) are handled automatically. Commit them like anything else.
- **Need an old version back?** Every commit is saved. Ask your lead.
