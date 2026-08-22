# find_skills.py
import re

with open(r"C:\Users\Sapna\Downloads\cv.tex", "r", encoding="utf-8") as f:
    content = f.read()

# Find text starting at \cvsection{Skills} up to the NEXT \cvsection or \cvsubsection
match = re.search(
    r"\\cvsection\{Skills\}(.*?)(?=\\cvsection\{|\\cvsubsection\{)",
    content,
    re.DOTALL  # lets . match across multiple lines
)

if match:
    skills_block = match.group(1)
    print(skills_block)
else:
    print("Skills section not found")