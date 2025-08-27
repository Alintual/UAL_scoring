import streamlit as st
from openai import OpenAI
import sys
import os
import time

# Добавляем корневую директорию в путь Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from parse_hh import get_html, extract_vacancy_data, extract_resume_data
except ImportError as e:
    st.error(f"Ошибка импорта: {e}")
    st.stop()

# Инициализация OpenAI-клиента
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SYSTEM_PROMPT = """
Оцени кандидата, насколько он подходит для данной вакансии.
Сначала напиши короткий анализ, который будет пояснять оценку.
Отдельно оцени качество заполнения резюме (понятно ли, с какими задачами сталкивался кандидат и каким образом их решал?). Эта оценка должна учитываться при выставлении финальной оценки - нам важно нанимать таких кандидатов, которые могут рассказать про свою работу
Потом представь результат в виде оценки от 1 до 10.
""".strip()


def request_gpt(system_prompt, user_prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1000,
            temperature=0,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка при обращении к GPT: {e}"


# UI
st.title('📊 CV Scoring App')
st.markdown("Анализ соответствия кандидата вакансии на HH.ru")

# Исправленные названия переменных для форм ввода
job_url = st.text_input('Введите ссылку на вакансию (HH.ru)',
                        placeholder="https://hh.ru/vacancy/12345678")
resume_url = st.text_input('Введите ссылку на резюме (HH.ru)',
                           placeholder="https://hh.ru/resume/abcdef123456")

if st.button("🚀 Проанализировать соответствие"):
    if not job_url or not resume_url:
        st.warning("⚠️ Пожалуйста, введите обе ссылки")
    else:
        with st.spinner("⏳ Парсим данные с HH.ru..."):
            try:
                # Добавляем задержку между запросами
                time.sleep(1)

                # Получаем HTML содержимое
                job_response = get_html(job_url)
                time.sleep(1)  # Задержка между запросами
                resume_response = get_html(resume_url)

                # Извлекаем данные
                job_text = extract_vacancy_data(job_response.text)
                resume_text = extract_resume_data(resume_response.text)

                # Формируем промпт для GPT
                prompt = f"# ВАКАНСИЯ\n{job_text}\n\n# РЕЗЮМЕ\n{resume_text}"

                st.success("✅ Данные успешно получены! Отправляем в GPT...")

                # Отправляем запрос к GPT
                response = request_gpt(SYSTEM_PROMPT, prompt)

                # Отображаем результаты
                st.subheader("📊 Результат анализа:")
                st.markdown(response)

                # Дополнительно показываем извлеченные данные
                with st.expander("📋 Показать извлеченные данные вакансии"):
                    st.markdown(job_text)

                with st.expander("👤 Показать извлеченные данные резюме"):
                    st.markdown(resume_text)

            except Exception as e:
                st.error(f"❌ Произошла ошибка: {e}")
                st.info("""
                💡 Возможные причины:
                - Ссылки неверные или недоступны
                - HH.ru заблокировал запрос
                - Требуется авторизация на сайте
                - Попробуйте обновить страницу и повторить запрос
                """)