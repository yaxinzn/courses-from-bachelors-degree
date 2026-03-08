import subprocess, re
from pathlib import Path

OUT = Path("_data/restudy_updates.yml")
MAX_COMMITS = 80  # scan last N commits touching restudy/playbooks

def sh(cmd):
    return subprocess.check_output(cmd, text=True)

# git log with name-only so we can infer course codes from paths
log = sh([
    "git","log",
    f"-n{MAX_COMMITS}",
    "--date=short",
    "--pretty=format:@@@%ad|%s",
    "--name-only",
    "--","restudy","playbooks"
])

items = []
date = None
subject = None
files = []

def flush():
    global date, subject, files, items
    if not date or not subject:
        return
    codes = sorted(set(
        m.group(2)
        for f in files
        for m in [re.match(r"^(restudy|playbooks)/([A-Z]{4}\d{4})/", f)]
        if m
    ))
    courses = ", ".join(codes) if codes else "—"
    # keywords summary: commit subject (you control by how you write commit message)
    items.append((date, courses, subject))

for line in log.splitlines():
    line = line.strip()
    if line.startswith("@@@"):
        flush()
        files = []
        date, subject = line[3:].split("|", 1)
        date = date.strip()
        subject = subject.strip()
    elif line:
        files.append(line)

flush()

def q(s: str) -> str:
    return '"' + s.replace("\\","\\\\").replace('"','\\"') + '"'

OUT.parent.mkdir(parents=True, exist_ok=True)
out = ["# Auto-generated. Edits will be overwritten.\n"]
for d, c, s in items[:50]:
    out.append(f"- date: {q(d)}\n")
    out.append(f"  courses: {q(c)}\n")
    out.append(f"  summary: {q(s)}\n")
OUT.write_text("".join(out), encoding="utf-8")
print(f"Wrote {OUT} with {min(len(items),50)} updates.")
