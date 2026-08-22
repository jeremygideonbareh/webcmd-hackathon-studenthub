# parse_resume.py
import re
import json

with open(r"C:\Users\Sapna\Downloads\cv.tex", "r", encoding="utf-8") as f:
    content = f.read()


def extract_section(pattern, text):
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1) if match else ""


# --- Skills: \section{Key Skills} ... \begin{itemize} \item X \item Y ... \end{itemize}
skills_block = extract_section(
    r"\\section\{Key Skills\}(.*?)\\end\{itemize\}", content
)
skills = re.findall(r"\\item\s+(.*?)\n", skills_block)
skills = [s.strip() for s in skills]

# --- Projects: \section{Projects} ... \begin{twenty} ... \end{twenty}
projects_block = extract_section(
    r"\\section\{Projects\}.*?\\begin\{twenty\}(.*?)\\end\{twenty\}", content
)

# Split the block into one chunk per \twentyitem, then grab
# just the first 3 {...} groups from each chunk (dates, dates, title) —
# we deliberately stop before the description, which has nested braces
# from \begin{itemize} that would confuse a longer regex.
chunks = projects_block.split("\\twentyitem")[1:]  # [1:] skips text before the first item

projects = []
for chunk in chunks:
    match = re.match(r"\s*\{(.*?)\}\s*\{(.*?)\}\s*\{(.*?)\}", chunk, re.DOTALL)
    if match:
        title = match.group(3).strip()
        projects.append(title)

# --- Education: \education{ ... } — split on \\ for each line
education_block = extract_section(r"\\education\{(.*?)\n\}", content)
education_lines = [
    line.strip() for line in education_block.split("\\\\") if line.strip()
]

resume_data = {
    "skills": skills,
    "projects": projects,
    "education_lines": education_lines,
}

with open("resume_parsed.json", "w", encoding="utf-8") as f:
    json.dump(resume_data, f, indent=2)

print(json.dumps(resume_data, indent=2))
print("\nSaved to resume_parsed.json")