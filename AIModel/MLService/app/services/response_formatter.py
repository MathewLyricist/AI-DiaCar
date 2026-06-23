from typing import Dict, List


class ResponseFormatter:

    def format_answer(self, query: str, knowledge: Dict, car_info: Dict = None) -> str:

        answer = f"🔧 **{query}**\n\n"

        if knowledge.get('causes'):
            answer += "📋 **Возможные причины:**\n"
            for cause in knowledge['causes'][:3]:
                answer += f"• {cause}\n"
            answer += "\n"

        if knowledge.get('steps'):
            answer += "🔧 **Рекомендуемые действия:**\n"
            for i, step in enumerate(knowledge['steps'], 1):
                formatted_step = self._highlight_parameters(step)
                answer += f"{i}. {formatted_step}\n"
            answer += "\n"

        if knowledge.get('parameters'):
            answer += "📏 **Важные параметры:**\n"
            for param in knowledge['parameters']:
                answer += f"• {param}\n"
            answer += "\n"

        if knowledge.get('manual_pages'):
            pages = knowledge['manual_pages'].split(',')
            answer += f"📄 **Рекомендую посмотреть страницы:** "
            answer += ", ".join([f"стр. {p.strip()}" for p in pages[:3]])
            answer += "\n\n💡 *На этих страницах есть подробные инструкции*"

        answer += "\n\n💡 **Рекомендации:**\n"
        answer += "• Проверьте комплектацию автомобиля\n"
        answer += "• Соблюдайте технику безопасности\n"
        answer += "• При сомнениях обратитесь к специалисту"

        return answer

    def _highlight_parameters(self, text: str) -> str:
        import re
        pattern = r'(\d+[-–]?\d*\s*(?:мм|°С|об/мин|км/ч|Нм|л\.с\.|л|кг))'
        return re.sub(pattern, r'**\1**', text)