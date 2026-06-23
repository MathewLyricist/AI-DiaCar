import os
import sys
import pdfplumber
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """Извлекает текст из PDF с помощью pdfplumber."""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Ошибка при обработке PDF {pdf_path}: {e}")
        return None

def main(input_folder, output_folder):
    input_folder = os.path.abspath(input_folder)
    output_folder = os.path.abspath(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    # Счётчики
    processed = 0
    skipped = 0
    failed = 0

    # Рекурсивно обходим все PDF
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                # Имя для выходного txt (берём только имя файла, без пути)
                txt_name = os.path.splitext(file)[0] + '.txt'
                txt_path = os.path.join(output_folder, txt_name)

                # Если такой txt уже есть — пропускаем (чтобы не делать повторно)
                if os.path.exists(txt_path):
                    print(f"Пропущен (уже есть): {txt_name}")
                    skipped += 1
                    continue

                print(f"Обработка: {pdf_path}")
                text = extract_text_from_pdf(pdf_path)
                if text:
                    try:
                        with open(txt_path, 'w', encoding='utf-8') as f:
                            f.write(text)
                        print(f"  -> сохранён: {txt_path}")
                        processed += 1
                    except Exception as e:
                        print(f"  Ошибка записи: {e}")
                        failed += 1
                else:
                    print(f"  Не удалось извлечь текст")
                    failed += 1

    print(f"\nГотово. Обработано: {processed}, пропущено: {skipped}, ошибок: {failed}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python pdf_to_txt.py <папка_с_pdf> <папка_для_txt>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])