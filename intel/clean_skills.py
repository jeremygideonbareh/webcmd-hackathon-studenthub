# step4_clean_skills.py
import re

with open(r"C:\Users\Sapna\Downloads\cv.tex", "r", encoding="utf-8") as f:
    content = f.read()

# Step 3's logic: grab the Skills block
match = re.search(
    r"\\cvsection\{Skills\}(.*?)(?=\\cvsection\{|\\cvsubsection\{)",
    content,
    re.DOTALL
)
skills_block = match.group(1) if match else ""

# NEW: pull out just the names inside \cvlistitem{NAME}{...}
# \cvlistitem\{(.*?)\}  means: find \cvlistitem{ then capture everything
# up to the next }, and stop there (the (.*?) is "non-greedy" so it
# stops at the FIRST } instead of the last one in the file)
skill_names = re.findall(r"\\cvlistitem\{(.*?)\}", skills_block)

print(skill_names)