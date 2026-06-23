import re
import json
from pathlib import Path

def fix_json_file(filepath):
    print(f"Обработка: {filepath.name}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if content.startswith('\ufeff'):
        content = content[1:]
    content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
    content = re.sub(r',\s*([}\]])', r'\1', content)
    def escape_quotes_in_string(match):
        inner = match.group(1)
        inner = inner.replace('"', '\\"')
        return f'"{inner}"'
    content = re.sub(r'"(.*?)"', escape_quotes_in_string, content, flags=re.DOTALL)
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"  ОШИБКА после исправлений: {e}")
        return False
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  УСПЕШНО исправлен")
    return True

if __name__ == "__main__":
    json_root = Path("/home/mathew/Политех/4-й курс/ВКР/ Project/AI DiaCar/AI-DiaCar/AIModel/DataPDF")
    if not json_root.exists():
        print(f"Папка не найдена: {json_root}")
        exit(1)
    for json_file in json_root.glob("**/*.json"):
        fix_json_file(json_file)
    print("Готово.")