# step6_clean_experience.py
import re

with open(r"C:\Users\Sapna\Downloads\cv.tex", "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(
    r"\\cvsection\{Experience\}(.*?)(?=\\cvsection\{|\\cvsubsection\{)",
    content,
    re.DOTALL
)
experience_block = match.group(1) if match else ""

# \cvexperience{Title}{Place}{Dates}{Location}{Keywords}
# we capture all FIVE {...} groups this time
experience_entries = re.findall(
    r"\\cvexperience\{(.*?)\}\{(.*?)\}\{(.*?)\}\{(.*?)\}\{(.*?)\}",
    experience_block
)

experience_keywords = []
for title, place, dates, location, keywords in experience_entries:
    experience_keywords.append(title)
    # keywords is comma-separated, e.g. "Kangaroo, Echidna, Wallaby"
    experience_keywords.extend([k.strip() for k in keywords.split(",")])

print(experience_keywords)