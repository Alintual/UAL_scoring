import requests
from bs4 import BeautifulSoup
import re


def get_html(url: str):
    """Получение HTML по URL"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    return requests.get(url, headers=headers)


def extract_candidate_data(html):
    """Извлечение данных кандидата из HTML"""
    soup = BeautifulSoup(html, 'html.parser')

    # Извлечение основных данных кандидата с обработкой ошибок
    try:
        name = soup.find('h2', {'data-qa': 'bloko-header-1'}).text.strip()
    except AttributeError:
        name = "Не указано"

    try:
        gender_age = soup.find('p').text.strip()
    except AttributeError:
        gender_age = "Не указано"

    try:
        location = soup.find('span', {'data-qa': 'resume-personal-address'}).text.strip()
    except AttributeError:
        location = "Не указано"

    try:
        job_title = soup.find('span', {'data-qa': 'resume-block-title-position'}).text.strip()
    except AttributeError:
        job_title = "Не указано"

    try:
        job_status = soup.find('span', {'data-qa': 'job-search-status'}).text.strip()
    except AttributeError:
        job_status = "Не указано"

    # Извлечение опыта работы
    experiences = []
    try:
        experience_section = soup.find('div', {'data-qa': 'resume-block-experience'})
        if experience_section:
            experience_items = experience_section.find_all('div', class_='resume-block-item-gap')
            for item in experience_items:
                try:
                    # Получаем период работы
                    period_elem = item.find('div', class_='bloko-column_s-2')
                    period = period_elem.text.strip() if period_elem else "Период не указан"

                    # Получаем длительность работы (если есть)
                    duration_elem = item.find('div', class_='bloko-text')
                    duration = duration_elem.text.strip() if duration_elem else ""

                    # Очищаем период от дублирующейся длительности
                    if duration:
                        # Удаляем длительность из периода, если она там есть
                        cleaned_period = re.sub(r'\s*' + re.escape(duration) + r'\s*$', '', period).strip()
                        formatted_period = f"{cleaned_period} ({duration})"
                    else:
                        formatted_period = period

                    company = item.find('div', class_='bloko-text_strong').text.strip() if item.find('div',
                                                                                                     class_='bloko-text_strong') else "Компания не указана"

                    position_elem = item.find('div', {'data-qa': 'resume-block-experience-position'})
                    position = position_elem.text.strip() if position_elem else "Должность не указана"

                    description_elem = item.find('div', {'data-qa': 'resume-block-experience-description'})
                    description = description_elem.text.strip() if description_elem else "Описание отсутствует"

                    experiences.append(f"**{formatted_period}**\n\n*{company}*\n\n**{position}**\n\n{description}\n")
                except Exception as e:
                    continue
    except Exception as e:
        experiences = ["Опыт работы не найден"]

    # Извлечение ключевых навыков
    skills = []
    try:
        skills_section = soup.find('div', {'data-qa': 'skills-table'})
        if skills_section:
            skills = [skill.text.strip() for skill in skills_section.find_all('span', {'data-qa': 'bloko-tag__text'})]
    except Exception as e:
        skills = ["Навыки не найдены"]

    # Формирование строки в формате Markdown
    markdown = f"# {name}\n\n"
    markdown += f"**{gender_age}**\n\n"
    markdown += f"**Местоположение:** {location}\n\n"
    markdown += f"**Должность:** {job_title}\n\n"
    markdown += f"**Статус:** {job_status}\n\n"

    markdown += "## Опыт работы\n\n"
    if experiences:
        for exp in experiences:
            markdown += exp + "\n"
    else:
        markdown += "Опыт работы отсутствует\n\n"

    markdown += "## Ключевые навыки\n\n"
    markdown += ', '.join(skills) + "\n"

    return markdown


# Пример использования функции
if __name__ == "__main__":
    # Тестовый URL
    test_url = "https://hh.ru/resume/d1d527250003e1c8040039ed1f746c79633631"

    try:
        response = get_html(test_url)
        response.raise_for_status()  # Проверка статуса ответа

        markdown = extract_candidate_data(response.text)
        print(markdown)

        # Сохранение в файл для проверки
        with open("candidate_profile.md", "w", encoding="utf-8") as f:
            f.write(markdown)
        print("\nПрофиль сохранен в файл 'candidate_profile.md'")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")