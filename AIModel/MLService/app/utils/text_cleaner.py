import re

def fix_merged_words(text: str) -> str:

    if not text:
        return text

    text = re.sub(r'([а-яё])([А-ЯЁ][а-яё])', r'\1 \2', text)

    text = re.sub(r'([А-ЯЁ]{2,})([А-ЯЁ][а-яё])', r'\1 \2', text)

    text = re.sub(r'(\b[ивксо])([а-яё])', r'\1 \2', text)

    text = re.sub(r'(\s+\d+)([.!?])', r'\2', text)

    text = re.sub(r'([а-яё]+)([ие])([а-яё]+)', lambda m: m.group(1) + ' ' + m.group(2) + m.group(3)
                  if m.group(2) in 'ие' and len(m.group(1)) > 3 else m.group(0), text)

    return text

def fix_broken_words(text: str) -> str:

    if not text:
        return text

    text = re.sub(r'([а-яА-Яa-zA-Z]+)-\s*\n\s*([а-яА-Яa-zA-Z]+)', r'\1\2', text)

    text = re.sub(r'([А-ЯЁ])\s+([А-ЯЁ])', r'\1\2', text)

    return text

def fix_spaces_inside_words(text: str) -> str:

    if not text:
        return text

    text = re.sub(r'\b([а-яёa-z])\s+([а-яёa-z]+)\b', r'\1\2', text, flags=re.IGNORECASE)

    text = re.sub(r'\b([а-яёa-z])\s+([а-яёa-z])\b', r'\1\2', text, flags=re.IGNORECASE)

    text = re.sub(r'\(\s*с\s+м', '(см', text)
    text = re.sub(r'с\s+м\.', 'см.', text)

    return text

def remove_pdf_artifacts(text: str) -> str:
    if not text:
        return text

    text = re.sub(r'=== СТРАНИЦА \d+ ===', '', text)
    text = re.sub(r'=== ОСНОВНОЙ МАНУАЛ.*?===', '', text, flags=re.DOTALL)
    text = re.sub(r'=== ОБЩИЙ МАНУАЛ.*?===', '', text, flags=re.DOTALL)

    text = re.sub(r'^\s*\d{1,3}\s+(?=[А-Яа-я])', '', text, flags=re.MULTILINE)

    text = re.sub(r'in fo', '', text, flags=re.IGNORECASE)
    text = re.sub(r'www\.[^\s]+', '', text)
    text = re.sub(r'Рис\.\s*\d+', '', text)
    text = re.sub(r'см\.\s*с\.\s*\d+', '', text)

    text = re.sub(r'\b[а-яёa-z]\b(?![\s]*$)', '', text, flags=re.IGNORECASE)

    return text

def normalize_whitespace(text: str) -> str:
    if not text:
        return text

    text = re.sub(r'\n{3,}', '\n\n', text)

    text = re.sub(r'\s{2,}', ' ', text)

    text = re.sub(r'\s+([.!?,:;])', r'\1', text)

    text = re.sub(r'\(\s+', '(', text)

    return text.strip()

def is_valid_sentence(sentence: str, min_length: int = 30) -> bool:

    if not sentence or len(sentence) < min_length:
        return False

    if re.search(r'[А-ЯЁ]{5,}', sentence):
        return False

    if '(см' in sentence and not sentence.strip().endswith('.'):
        return False
        
    if re.match(r'^\s*\d+\s*[-–]\s*\w+', sentence):
        return False

    return True

def clean_text(text: str) -> str:

    if not text:
        return text
    text = fix_broken_words(text)
    text = remove_pdf_artifacts(text)
    text = fix_merged_words(text)
    text = fix_spaces_inside_words(text)
    text = normalize_whitespace(text)
    text = fix_spaces_inside_words(text)
    text = normalize_whitespace(text)
    return text

def split_into_sentences(text: str) -> list:
    if not text:
        return []
    sentences = re.split(r'[.!?;]+', text)
    result = []
    for s in sentences:
        s = s.strip()
        if len(s) > 20 and not s.startswith('==='):
            result.append(s)
    return result