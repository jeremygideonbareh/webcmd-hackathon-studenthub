# step5_clean_projects.py
import re

with open(r"C:\Users\Sapna\Downloads\cv.tex", "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(
    r"\\cvsubsection\{Other Activities and Projects\}(.*?)(?=\\cvsection\{|\\cvsubsection\{|\\end\{document\})",
    content,
    re.DOTALL
)
projects_block = match.group(1) if match else ""

project_names = re.findall(r"\\cvlistitem\{(.*?)\}", projects_block)

print(project_names)