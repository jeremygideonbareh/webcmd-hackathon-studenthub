# tfidf_matcher.py
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Terms that would normally get split/mangled by a plain tokenizer
# (default tokenizers split on punctuation, so "C++" becomes "c" and "Node.js" becomes "node" + "js")
# Add to this list as you find more tech terms in real postings.
TECH_TERMS_TO_PRESERVE = [
    "c++", "c#", "node.js", "next.js", "vue.js", "scikit-learn",
    "tensorflow", "pytorch", "tf-idf", "front-end", "back-end",
    "full-stack", ".net", "asp.net",
]


def custom_tokenizer(text):
    """
    Lowercases text, protects known tech terms from being split,
    then extracts word-like tokens including things like C++ or Node.js.
    """
    text = text.lower()

    # Temporarily replace known tech terms with a placeholder token
    # (using underscores so they survive the regex split as ONE token)
    placeholders = {}
    for i, term in enumerate(TECH_TERMS_TO_PRESERVE):
        if term in text:
            placeholder = f"__TECHTERM{i}__"
            placeholders[placeholder] = term
            text = text.replace(term, placeholder)

    # Now split into words: letters/numbers, allowing . + # - inside a token
    # so things like "3.14" or "full-stack" stay as one token
    tokens = re.findall(r"[a-z0-9]+(?:[.\-+#][a-z0-9]+)*", text)

    # Swap placeholders back to their real form
    final_tokens = []
    for tok in tokens:
        matched_placeholder = None
        for placeholder, real_term in placeholders.items():
            if placeholder.lower() in tok:
                matched_placeholder = real_term
                break
        final_tokens.append(matched_placeholder if matched_placeholder else tok)

    return final_tokens


def match_resume_to_postings(resume_data, postings, top_n=5):
    """
    resume_data: dict with 'skills' (list) and 'projects' (list), e.g. from resume_parsed.json
    postings: list of dicts, each with at least 'title' and 'description' keys
    Returns: postings sorted by relevance, each with an added 'match_score' field
    """
    # Build the resume "document" — combine skills and projects into one string.
    # Skills are repeated twice to weight them higher than general project text.
    resume_skills_text = " ".join(resume_data.get("skills", []))
    resume_projects_text = " ".join(resume_data.get("projects", []))
    resume_text = f"{resume_skills_text} {resume_skills_text} {resume_projects_text}"

    # Build one "document" per job posting
    posting_texts = [
        f"{p.get('title', '')} {p.get('description', '')} {' '.join(p.get('skills', []))}"
        for p in postings
    ]

    # All documents = resume + every posting, vectorized together so they share the same vocabulary
    all_documents = [resume_text] + posting_texts

    vectorizer = TfidfVectorizer(
        tokenizer=custom_tokenizer,
        ngram_range=(1, 3),   # unigrams, bigrams, AND trigrams
        token_pattern=None,   # required when using a custom tokenizer
        lowercase=False,      # our tokenizer already lowercases
    )
    tfidf_matrix = vectorizer.fit_transform(all_documents)

    resume_vector = tfidf_matrix[0]         # first row = resume
    posting_vectors = tfidf_matrix[1:]      # rest = postings

    scores = cosine_similarity(resume_vector, posting_vectors)[0]

    # Attach scores back to postings and sort by best match first
    for posting, score in zip(postings, scores):
        posting["match_score"] = round(float(score), 4)

    ranked = sorted(postings, key=lambda p: p["match_score"], reverse=True)
    return ranked[:top_n]


if __name__ == "__main__":
    # Quick manual test with fake data, so this file works standalone
    fake_resume = {
        "skills": ["Python", "Qiskit", "Machine Learning", "C++"],
        "projects": ["Quantum Monte Carlo Option Pricing", "Lunar Drone Simulator"],
    }

    fake_postings = [
        {"title": "ML Intern", "description": "Looking for Python and machine learning experience", "skills": ["Python", "TensorFlow"]},
        {"title": "Frontend Intern", "description": "React and Node.js required", "skills": ["React", "Node.js"]},
        {"title": "Quantum Computing Research Intern", "description": "Qiskit and quantum algorithms, Python required", "skills": ["Qiskit", "Python"]},
    ]

    results = match_resume_to_postings(fake_resume, fake_postings, top_n=3)
    for r in results:
        print(f"{r['match_score']:.4f}  {r['title']}")