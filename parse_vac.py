from bs4 import BeautifulSoup
import requests


def extract_vacancy_to_markdown(url):
    """
    Извлекает данные о вакансии по URL и возвращает в формате Markdown

    Args:
        url (str): URL вакансии на hh.ru

    Returns:
        str: Данные вакансии в формате Markdown
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
    except requests.RequestException as e:
        return f"Ошибка при загрузке страницы: {e}"

    soup = BeautifulSoup(html_content, 'html.parser')

    # Извлекаем основные данные
    title = soup.find('h1', {'data-qa': 'vacancy-title'})
    title_text = title.text.strip() if title else "Не указано"

    salary = soup.find('span', class_='magritte-text_typography-label-1-regular___pi3R-_4-1-1')
    salary_text = salary.text.strip() if salary else "Не указана"

    experience = soup.find('span', {'data-qa': 'vacancy-experience'})
    experience_text = experience.text.strip() if experience else "Не указан"

    company = soup.find('a', {'data-qa': 'vacancy-company-name'})
    company_text = company.text.strip() if company else "Не указана"
    company_link = f"https://hh.ru{company['href']}" if company and company.get('href') else "#"

    # Извлекаем описание вакансии
    description = soup.find('div', {'data-qa': 'vacancy-description'})
    description_text = ""
    if description:
        # Очищаем HTML теги, но сохраняем структуру
        for tag in description.find_all(['p', 'ul', 'li', 'strong']):
            if tag.name == 'p':
                text = tag.get_text().strip()
                if text:
                    description_text += text + "\n\n"
            elif tag.name == 'ul':
                for li in tag.find_all('li'):
                    li_text = li.get_text().strip()
                    if li_text:
                        description_text += f"- {li_text}\n"
                description_text += "\n"
            elif tag.name == 'strong':
                strong_text = tag.get_text().strip()
                if strong_text:
                    description_text += f"**{strong_text}** "

    # Извлекаем ключевые навыки
    skills = []
    skills_elements = soup.find_all('li', {'data-qa': 'skills-element'})
    for skill in skills_elements:
        skill_text = skill.get_text().strip()
        if skill_text:
            skills.append(skill_text)

    # Форматируем в Markdown
    markdown_output = f"""# {title_text}

**Компания:** [{company_text}]({company_link})  
**Уровень дохода:** {salary_text}  
**Опыт работы:** {experience_text}

## Описание вакансии

{description_text if description_text else 'Описание не найдено'}

## Ключевые навыки

{', '.join([f'`{skill}`' for skill in skills]) if skills else 'Не указаны'}

---

*Вакансия размещена на [hh.ru]({url})*"""

    return markdown_output


# Тестовый URL
test_url = "https://hh.ru/vacancy/124384733?query=%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%87%D0%B8%D0%BA+%D1%87%D0%B0%D1%82-%D0%B1%D0%BE%D1%82%D0%BE%D0%B2&hhtmFrom=vacancy_search_list"

# Пример использования
if __name__ == "__main__":
    print("Извлечение данных вакансии...")
    markdown_result = extract_vacancy_to_markdown(test_url)
    print(markdown_result)

    # Дополнительно: сохранение в файл
    with open('vacancy.md', 'w', encoding='utf-8') as md_file:
        md_file.write(markdown_result)
    print("\nРезультат также сохранен в файл 'vacancy.md'")