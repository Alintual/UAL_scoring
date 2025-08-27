import requests
from bs4 import BeautifulSoup
import re


def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }

    # Добавляем куки для обхода защиты
    cookies = {
        '_hhsid': 'example_hhsid',
        '_ga': 'GA1.1.example',
        'hhtoken': 'example_token'
    }

    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        raise


def extract_vacancy_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    def safe_text(selector, attrs=None):
        try:
            el = soup.find(selector, attrs or {})
            return el.text.strip() if el else "Не указано"
        except:
            return "Не указано"

    title = safe_text('h1', {'data-qa': 'vacancy-title'})
    salary = safe_text('div', {'data-qa': 'vacancy-salary'}) or safe_text('span', {'data-qa': 'vacancy-salary'})
    company = safe_text('a', {'data-qa': 'vacancy-company-name'})

    # Извлечение опыта работы
    experience = safe_text('span', {'data-qa': 'vacancy-experience'})

    # Извлечение описания
    description = soup.find('div', {'data-qa': 'vacancy-description'})
    description_text = description.get_text(separator="\n").strip() if description else "Описание не найдено"

    # Извлечение ключевых навыков
    skills = []
    skills_section = soup.find('div', {'data-qa': 'skills-table'})
    if skills_section:
        skills = [skill.text.strip() for skill in skills_section.find_all('span', {'data-qa': 'bloko-tag__text'})]

    markdown = f"# {title}\n\n"
    markdown += f"**Компания:** {company}\n\n"
    markdown += f"**Зарплата:** {salary}\n\n"
    markdown += f"**Требуемый опыт:** {experience}\n\n"
    markdown += f"## Описание\n\n{description_text}\n\n"

    if skills:
        markdown += f"## Ключевые навыки\n\n{', '.join(skills)}\n"

    return markdown.strip()


def extract_resume_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    def safe_text(selector, attrs=None):
        try:
            el = soup.find(selector, attrs or {})
            return el.text.strip() if el else "Не указано"
        except:
            return "Не указано"

    name = safe_text('span', {'data-qa': 'resume-personal-name'}) or safe_text('h2', {'data-qa': 'bloko-header-1'})
    gender_age = safe_text('span', {'data-qa': 'resume-personal-age'})
    location = safe_text('span', {'data-qa': 'resume-personal-address'})
    job_title = safe_text('span', {'data-qa': 'resume-block-title-position'})
    job_status = safe_text('span', {'data-qa': 'job-search-status'})

    # Извлечение опыта работы
    experiences = []
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
            except Exception:
                continue

    # Извлечение ключевых навыков
    skills = []
    skills_section = soup.find('div', {'data-qa': 'skills-table'})
    if skills_section:
        skills = [skill.text.strip() for skill in skills_section.find_all('span', {'data-qa': 'bloko-tag__text'})]

    markdown = f"# {name}\n\n"
    markdown += f"**Возраст:** {gender_age}\n\n" if gender_age != "Не указано" else ""
    markdown += f"**Местоположение:** {location}\n\n"
    markdown += f"**Должность:** {job_title}\n\n"
    markdown += f"**Статус поиска работы:** {job_status}\n\n"

    markdown += "## Опыт работы\n\n"
    if experiences:
        for exp in experiences:
            markdown += exp + "\n"
    else:
        markdown += "Опыт работы отсутствует\n\n"

    markdown += "## Ключевые навыки\n\n"
    markdown += ', '.join(skills) + "\n" if skills else "Навыки не указаны\n"

    return markdown.strip()