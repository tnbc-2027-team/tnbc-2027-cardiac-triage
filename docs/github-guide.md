# GitHub in 10 minutes

You don't need the command line. Use **GitHub Desktop**, a free app that does everything with buttons.

## One-time setup

1. Make a GitHub account and send your username to your subteam lead so they can add you.
2. Accept the invite email from GitHub.
3. Install **GitHub Desktop** (desktop.github.com) and sign in.
4. In GitHub Desktop: **File → Clone repository**, pick `tnbc-2027-cardiac-triage`, and choose a folder on your computer.

You now have the team's files on your computer.

## Every time you work

1. **Get the latest files.** Click **Fetch origin**, then **Pull origin** if it appears.
2. **Make your own branch.** Click **Current branch → New branch** and give it a short name, like `spo2-schematic` or `enclosure-v2`.
3. **Do your work** in KiCad, your CAD tool or your code editor, and save as usual.
4. **Commit.** GitHub Desktop lists the files you changed. Write a short summary of what you did and click **Commit**.
5. **Push.** Click **Push origin** (or **Publish branch** the first time). Do this at least once a day so your work isn't only on your laptop.
6. **Ask for a review.** Click **Create Pull Request**. A browser page opens. Add a sentence on what you changed and pick one teammate as reviewer.
7. **After it's approved,** click **Merge** on that page. Then in GitHub Desktop, switch back to `main` and pull.

## Good to know

- **Big CAD files** (STEP, SolidWorks, Fusion) are handled automatically. Just commit them like anything else.
- **Two people editing the same KiCad board or CAD file at once** doesn't work, because Git can't combine them. Tell your subteam before you start on a shared file.
- **Made a mistake?** Every commit is saved. Ask your lead and it can be undone.
