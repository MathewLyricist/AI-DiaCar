import re
from typing import List, Dict
from pdfplumber import open as pdf_open
from app.utils.text_cleaner import clean_text
from app.utils.russian_dictionary import INSTRUCTION_VERBS


class PDFParserService:

    def extract_clean_text(self, pdf_path: str) -> str:
        full_text = []

        with pdf_open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    cleaned = self._clean_page_text(page_text)
                    full_text.append(cleaned)

        return '\n\n'.join(full_text)

    def _clean_page_text(self, text: str) -> str:

        text = re.sub(r'([а-яА-Яa-zA-Z]+)-\s*\n\s*([а-яА-Яa-zA-Z]+)', r'\1\2', text)

        text = re.sub(r'([А-Я])\s+([А-Я])', r'\1\2', text)

        text = re.sub(r'in fo', '', text, flags=re.IGNORECASE)
        text = re.sub(r'www\.[^\s]+', '', text)
        text = re.sub(r'Рис\.\s*\d+', '', text)

        text = ' '.join(text.split())

        lines = text.split('\n')
        lines = [l for l in lines if len(l.strip()) > 20]

        return '\n'.join(lines)

    def extract_instructions(self, text: str, topic_keywords: List[str]) -> List[Dict]:
        instructions = []

        sentences = re.split(r'[.!?]+', text)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 30:
                continue

            if any(kw.lower() in sentence.lower() for kw in topic_keywords):
                if self._has_instruction_verb(sentence):
                    instructions.append({
                        'text': sentence,
                        'length': len(sentence)
                    })

        return sorted(instructions, key=lambda x: x['length'], reverse=True)[:10]

    def _has_instruction_verb(self, sentence: str) -> bool:
        verbs = [
            'измерьте', 'проверьте', 'отрегулируйте', 'ослабьте', 'затяните',
            'снимите', 'установите', 'замените', 'нажмите', 'поверните'
        ]
        sentence_lower = sentence.lower()
        return any(verb in sentence_lower for verb in verbs)

    def find_relevant_blocks(self, text: str, keywords: List[str], min_block_len=150, max_block_len=3000) -> List[str]:
        if not text or not keywords:
            return []
        cleaned = clean_text(text)
        if len(cleaned) < min_block_len:
            return []
        paragraphs = re.split(r'\n\s*\n', cleaned)
        lines = cleaned.split('\n')
        blocks = paragraphs.copy()
        block_size = 8
        for i in range(0, len(lines), block_size):
            block = '\n'.join(lines[i:i + block_size])
            if len(block) > min_block_len:
                blocks.append(block)
        unique_blocks = list(set(blocks))
        scored = []
        for block in unique_blocks:
            if len(block) < min_block_len:
                continue
            block_lower = block.lower()
            if not any(kw in block_lower for kw in keywords if len(kw) > 3):
                continue
            if any(x in block_lower for x in
                   ['оглавление', 'предисловие', 'руководство по эксплуатации', 'приложение', 'скачано с сайта',
                    'издательство', 'ISBN', 'твердый переплет', 'цветные электросхемы']):
                continue
            kw_matches = sum(1 for kw in keywords if kw in block_lower)
            verb_matches = sum(1 for v in INSTRUCTION_VERBS if v in block_lower)
            step_bonus = 10 if re.search(r'\d+\.\s*[А-Я]', block_lower) else 0
            relevance = kw_matches * 3 + verb_matches * 5 + step_bonus
            if re.search(r'\d+\s*Н·м', block_lower):
                relevance += 10
            if relevance > 0:
                if len(block) > max_block_len:
                    block = block[:max_block_len] + "..."
                scored.append((relevance, block))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [block for _, block in scored[:2]]

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        return self.extract_clean_text(pdf_path)

