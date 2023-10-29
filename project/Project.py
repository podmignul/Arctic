import streamlit as st
import base64
import numpy as np
import pandas as pd
import plotly.express as px
import json
from urllib.request import urlopen
import plotly.graph_objects as go
import datetime
import os

st.set_page_config(page_title='Главная', layout="wide")

# Получить текущий каталог (где находится исполняемый скрипт)
current_directory = os.path.dirname(os.path.abspath(__file__))

# Путь к изображению логотипа
logo_path = os.path.join(current_directory, "mchs.png")

# Создание блока шапки с заданными цветами
header_container = st.container()
with header_container:
    st.markdown(
        f"""
        <div style="
            background-color: #194F9E;
            padding: 10px;
            border-radius: 20px;
            display: flex;
            align-items: center;
        ">
        <img src="data:image/png;base64,{base64.b64encode(open(logo_path, 'rb').read()).decode()}" alt="Логотип" style="width: 40px; margin: 20px;">
        <h2 style="color: white; line-height: 0.5; margin-right: 15px; font-size: 18pt;">МЧС России<br><span style="font-size: 10.7pt;">по Пермскому краю</span></h2>
        <h1 style="color: white; font-size: 23pt; margin-bottom: 5px;">Система Анализа и Прогнозирования Происшествий и ЧС</h1>
        </div>
        """,
        unsafe_allow_html=True
    )



# Создание вкладок для кнопок "Прогноз", "Статистика" и "Отчет"
map, pred, stat = st.tabs(["Карта", "Прогноз", "История"])

# # Создание вкладок для кнопок "Прогноз", "Статистика" и "Отчет"
# about, pred, map, stat, doc, upload = st.tabs(["О нас", "Прогноз", "Карта", "История", "Отчет", "Загрузка"])

data_path = os.path.join(current_directory, "data.csv")

data = pd.read_csv(data_path, encoding='utf-8')

columns_to_drop = ['T', 'Po', 'P', 'Pa', 'U', 'Ff', 'ff10', 'ff3', 'N', 
                    'Tn', 'Tx', 'Nh', 'VV', 'Td', 'RRR', 'tR', 'Tg', 'sss', 'Spring', 
                    'Winter', 'Summer', 'Autumn', 'heating network', 
                    'cold water network', 'hot water network', 'electricity network', 
                    'gas network', 'water treatment stations', 'water pumping stations', 
                    'water intake facilities', 'sewage network', 'sewage treatment plants', 
                    'sewage pumping stations', 'boiler houses', 'heat points']
data.drop(columns=columns_to_drop, inplace=True)

# Группировка по столбцам 'year', 'month', 'day'
data_grouped = data.groupby(['year', 'month', 'day']).agg({
    'accidents in transport': 'mean',
    'accidents with hazardous/toxic substances emission': 'mean',
    'explosions/fires/damages': 'mean',
    'housing and utilities': 'mean',
    'natural hazards': 'mean',
    'other hazards': 'mean',
    'Emergency Percentage': 'mean'
}).reset_index()

# Округление средних значений до целого
data_grouped['accidents in transport'] = data_grouped['accidents in transport'].round().astype(int)
data_grouped['accidents with hazardous/toxic substances emission'] = data_grouped['accidents with hazardous/toxic substances emission'].round().astype(int)
data_grouped['explosions/fires/damages'] = data_grouped['explosions/fires/damages'].round().astype(int)
data_grouped['housing and utilities'] = data_grouped['housing and utilities'].round().astype(int)
data_grouped['natural hazards'] = data_grouped['natural hazards'].round().astype(int)
data_grouped['other hazards'] = data_grouped['other hazards'].round().astype(int)
data_grouped['Emergency Percentage'] = data_grouped['Emergency Percentage'].round().astype(int)

# Создайте словарь, чтобы сопоставить имена столбцов с их описанием
emergency_columns = {
    'accidents in transport': 'Аварии на транспорте',
    'accidents with hazardous/toxic substances emission': 'Аварии с выбросом опасных или токсичных веществ',
    'explosions/fires/damages': 'Взрывы, пожары или разрушения',
    'housing and utilities': 'ЖКХ',
    'natural hazards': 'Опасные природные явления',
    'other hazards': 'Прочие опасности'
}

def pluralize(number, one_form, few_form, many_form):
    if number % 10 == 1 and number % 100 != 11:
        return one_form
    if 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return few_form
    return many_form


# Получаем текущую дату
current_date = datetime.date.today()

# Рассчитываем дату, которая находится три дня вперед относительно текущей даты
max_date = current_date + datetime.timedelta(days=10)


# with about:
#     st.header("О нас")


with map:
    st.header("Прогностическая карта предупреждений")

    st.markdown(
        f"""
        <style>
        .large-text {{
            font-size: 18px;
            margin-bottom: 20px;
        }}
        </style>
        <div class="large-text">
            Пожалуйста, выберите дату для предоставления прогноза.
        </div>
        """
        , unsafe_allow_html=True
    )

        # ЗАМЕНИТЬ НА ТЕКУЩУЮ ДАТУ!!!!


    # Создаем виджет выбора даты с ограничением
    selected_date = st.date_input("Выберите дату", current_date, max_value=max_date)
    

    # Проверяем, есть ли данные для выбранной даты
    if 'data' in locals() and not data[(data['year'] == selected_date.year) & (data['month'] == selected_date.month) & (data['day'] == selected_date.day)].empty:
        # Извлекаем значение вероятности для выбранной категории ЧС
        selected_emergency_prob = data[(data['year'] == selected_date.year) & (data['month'] == selected_date.month) & (data['day'] == selected_date.day)]['Emergency Percentage'].values[0]

        # Создайте словарь для замены месяцев
        month_names = {
            "January": "января",
            "February": "февраля",
            "March": "марта",
            "April": "апреля",
            "May": "мая",
            "June": "июня",
            "July": "июля",
            "August": "августа",
            "September": "сентября",
            "October": "октября",
            "November": "ноября",
            "December": "декабря"
        }

        # Преобразуйте выбранную дату в нужный формат с учетом винительного падежа
        formatted_date = selected_date.strftime("%d %B %Y")
        for month in month_names:
            if month in formatted_date:
                formatted_date = formatted_date.replace(month, month_names[month])

        # Выведите дату в указанном формате
        st.subheader(f"Прогноз происшествий и ЧС на {formatted_date} года")

        # Извлекаем значение вероятности для выбранной категории ЧС
        selected_emergency_prob = data[(data['year'] == selected_date.year) & (data['month'] == selected_date.month) & (data['day'] == selected_date.day)]['Emergency Percentage'].values[0]

        # Вычисляем значения x, y и z на основе значения prediction
        # В данном случае, давайте считать, что чем выше prediction, тем "опаснее" ситуация, и мы хотим, чтобы цвет был красным.
        # Чем ниже prediction, тем "безопаснее" ситуация, и мы хотим, чтобы цвет был зеленым.

        x = 255  # Красный
        y = 0  # Зеленый
        z = 0  # Синий

        # Масштабируем значение prediction от 0 до 100 в интервал значений x, y и z
        x = int(255 * (selected_emergency_prob / 100))
        y = int(255 - x)  # Таким образом, зеленый уменьшается по мере увеличения prediction
        z = 0  # Мы задаем синий на ноль, но вы можете изменить это значение по вашему усмотрению.

        # Создаем строку с форматом rgba
        rgb_color = f'rgb({x},{y},{z})'


        # Определяем функцию, которая преобразует значение вероятности в текстовое описание опасности
        def get_emergency_description(probability, rgb_color):
            if 0 <= probability <= 19:
                return f'<span style="color: {rgb_color}">низкая опасность</span>'
            elif 20 <= probability <= 39:
                return f'<span style="color: {rgb_color}">умеренная опасность</span>'
            elif 40 <= probability <= 59:
                return f'<span style="color: {rgb_color}">средняя опасность</span>'
            elif 60 <= probability <= 79:
                return f'<span style="color: {rgb_color}">высокая опасность</span>'
            elif 80 <= probability <= 100:
                return f'<span style="color: {rgb_color}">критическая опасность</span>'
            else:
                return "опасность"

        # Преобразуем значение вероятности в текстовое описание
        selected_emergency_description = get_emergency_description(selected_emergency_prob, rgb_color)

        # Теперь selected_emergency_description содержит текстовое описание опасности
        st.markdown(
            f"""
            <style>
            .large-text {{
                font-size: 18px;
                margin-bottom: 20px;
            }}
            </style>
            <div class="large-text">
                На выбранную дату ожидается {selected_emergency_description}
            </div>
            """
            , unsafe_allow_html=True
        )

        for column_key, column_description in emergency_columns.items():
            # Извлекаем среднее значение для каждой категории ЧС
            average_emergency_count = data[(data['year'] == selected_date.year) &
                                        (data['month'] == selected_date.month) &
                                        (data['day'] == selected_date.day)][column_key].values[0]

            # Получаем правильную форму слова "событие"
            event_form = pluralize(average_emergency_count, "событие", "события", "событий")

            st.markdown(
                f"""
                <style>
                .text {{
                    font-size: 15px;
                }}
                </style>
                <div class="text">
                    {column_description} - {average_emergency_count} {event_form}*
                </div>
                """
                , unsafe_allow_html=True
            )

        st.markdown(
            f"""
            <style>
            .text1 {{
                font-size: 12px;
                margin-top: 10px;
            }}
            </style>
            <div class="text1">
                *Среднее количество событий на один округ Пермского края
            </div>
            """
            , unsafe_allow_html=True
        )


        geojson = os.path.join(current_directory, "Perm.geojson")

        with open(geojson) as geojson_file:
            perm_geojson = json.load(geojson_file)

        coordinates = perm_geojson["geometry"]["coordinates"][0]
        lons, lats = zip(*coordinates)

        fig = go.Figure()

        # Добавляем полигон для отображения области
        fig.add_trace(go.Scattermapbox(
            lon=lons,
            lat=lats,
            mode="lines",
            fill="toself",
            line=dict(color=f"rgb({x},{y},{z})", width=4),
            fillcolor=f"rgba({x},{y},{z},0.2)",
            hoverinfo="skip"
        ))

        fig.update_geos(fitbounds="locations", visible=True)
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_zoom=4.8,
            mapbox_center={"lat": 59, "lon": 56},
            showlegend=False,
            height=500,
            margin={"r":0,"t":20,"l":0,"b":0}
        )

        fig.update_layout(
            dragmode=False)    

        config = {'staticPlot': True}

        st.plotly_chart(fig, use_container_width=True, config=config)

    else:
        st.warning("Для выбранной даты нет данных о вероятности чрезвычайных ситуаций.")
        selected_emergency_prob = 0




# Обработка нажатия на вкладку "Прогноз"
with pred:
    st.header("Прогноз возникновения происшествий и ЧС")

    st.markdown(
        f"""
        <style>
        .large-text {{
            font-size: 18px;
            margin-bottom: 20px;
        }}
        </style>
        <div class="large-text">
            Пожалуйста, выберите дату и район для предоставления прогноза.
        </div>
        """
        , unsafe_allow_html=True
    )

    # Создаем виджет выбора даты с ограничением
    selected_date = st.date_input("Выберите дату", current_date, min_value=current_date, max_value=max_date, key=1)
    
    # Выбор района
    selected_district = st.selectbox("Выберите район", data['district'].unique())

    # Проверяем, есть ли данные для выбранной даты и района
    if 'data' in locals() and not data[(data['year'] == selected_date.year) & (data['month'] == selected_date.month) & (data['day'] == selected_date.day) & (data['district'] == selected_district)].empty:
        # Создайте словарь для замены месяцев
        month_names = {
            "January": "января",
            "February": "февраля",
            "March": "марта",
            "April": "апреля",
            "May": "мая",
            "June": "июня",
            "July": "июля",
            "August": "августа",
            "September": "сентября",
            "October": "октября",
            "November": "ноября",
            "December": "декабря"
        }

        # Преобразуйте выбранную дату в нужный формат с учетом винительного падежа
        formatted_date = selected_date.strftime("%d %B %Y")
        for month in month_names:
            if month in formatted_date:
                formatted_date = formatted_date.replace(month, month_names[month])

        # Выведите дату и район в указанном формате
        st.subheader(f"Прогноз происшествий и ЧС на {formatted_date} года в {selected_district}")

        # Извлекаем данные только для выбранной даты и района
        selected_data = data[(data['year'] == selected_date.year) & (data['month'] == selected_date.month) & (data['day'] == selected_date.day) & (data['district'] == selected_district)]

        # Группируем данные по типам ЧС и считаем их количество
        grouped_data = selected_data[['accidents in transport', 'accidents with hazardous/toxic substances emission', 'explosions/fires/damages', 'housing and utilities', 'natural hazards', 'other hazards']].sum()

        # Переименовываем типы ЧС
        type_mapping = {
            'accidents in transport': 'Аварии на транспорте',
            'accidents with hazardous/toxic substances emission': 'Аварии с выбросом опасных или токсичных веществ',
            'explosions/fires/damages': 'Взрывы, пожары или разрушения',
            'housing and utilities': 'ЖКХ',
            'natural hazards': 'Опасные природные явления',
            'other hazards': 'Прочие опасности'
        }
        grouped_data = grouped_data.rename(index=type_mapping)

        # Задаем цвета для каждого типа ЧС
        colors = ["#C00000", "#ED7D31", "#FFC000", "#70AD47", "#2F5597", "#7030A0"]

        # Создаем столбчатую диаграмму для каждого типа ЧС, если количество больше 0
        fig = go.Figure()
        for i, type_chs in enumerate(grouped_data.index):
            if grouped_data.loc[type_chs] > 0:
                fig.add_trace(go.Bar(x=[type_chs], y=[grouped_data.loc[type_chs]], name=type_chs, marker_color=colors[i]))

        # Настройка внешнего вида диаграммы
        fig.update_layout(
            xaxis_title='Типы ЧС',
            yaxis_title='Количество ЧС'
        )

        # Добавляем легенду
        fig.update_layout(showlegend=True, height=700)

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"Для выбранной даты и района ({selected_district}) нет данных о вероятности чрезвычайных ситуаций.")



    

# Обработка нажатия на вкладку "История"
with stat:

    st.header("История происшествий и ЧС")

    st.markdown(
        f"""
        <style>
        .large-text {{
            font-size: 18px;
            margin-bottom: 20px;
        }}
        </style>
        <div class="large-text">
            Пожалуйста, выберите дату и район для предоставления истории.
        </div>
        """
        , unsafe_allow_html=True
    )

    # Создаем виджет выбора даты с ограничением
    selected_date = st.date_input("Выберите дату", current_date, max_value=current_date, key=2)
    
    # Выбор района
    selected_district = st.selectbox("Выберите район", data['district'].unique(), key=5)

    # Проверяем, есть ли данные для выбранной даты и района
    if 'data' in locals() and not data[(data['year'] == selected_date.year) & (data['month'] == selected_date.month) & (data['day'] == selected_date.day) & (data['district'] == selected_district)].empty:
        # Создайте словарь для замены месяцев
        month_names = {
            "January": "января",
            "February": "февраля",
            "March": "марта",
            "April": "апреля",
            "May": "мая",
            "June": "июня",
            "July": "июля",
            "August": "августа",
            "September": "сентября",
            "October": "октября",
            "November": "ноября",
            "December": "декабря"
        }

        # Преобразуйте выбранную дату в нужный формат с учетом винительного падежа
        formatted_date = selected_date.strftime("%d %B %Y")
        for month in month_names:
            if month in formatted_date:
                formatted_date = formatted_date.replace(month, month_names[month])

        # Выведите дату и район в указанном формате
        st.subheader(f"История происшествий и ЧС на {formatted_date} года в {selected_district}")

        # Извлекаем данные только для выбранной даты и района
        selected_data = data[(data['year'] == selected_date.year) & (data['month'] == selected_date.month) & (data['day'] == selected_date.day) & (data['district'] == selected_district)]

        # Группируем данные по типам ЧС и считаем их количество
        grouped_data = selected_data[['accidents in transport', 'accidents with hazardous/toxic substances emission', 'explosions/fires/damages', 'housing and utilities', 'natural hazards', 'other hazards']].sum()

        # Переименовываем типы ЧС
        type_mapping = {
            'accidents in transport': 'Аварии на транспорте',
            'accidents with hazardous/toxic substances emission': 'Аварии с выбросом опасных или токсичных веществ',
            'explosions/fires/damages': 'Взрывы, пожары или разрушения',
            'housing and utilities': 'ЖКХ',
            'natural hazards': 'Опасные природные явления',
            'other hazards': 'Прочие опасности'
        }
        grouped_data = grouped_data.rename(index=type_mapping)

        # Задаем цвета для каждого типа ЧС
        colors = ["#C00000", "#ED7D31", "#FFC000", "#70AD47", "#2F5597", "#7030A0"]

        # Создаем столбчатую диаграмму для каждого типа ЧС, если количество больше 0
        fig = go.Figure()
        for i, type_chs in enumerate(grouped_data.index):
            if grouped_data.loc[type_chs] > 0:
                fig.add_trace(go.Bar(x=[type_chs], y=[grouped_data.loc[type_chs]], name=type_chs, marker_color=colors[i]))

        # Настройка внешнего вида диаграммы
        fig.update_layout(
            xaxis_title='Типы ЧС',
            yaxis_title='Количество ЧС'
        )

        # Добавляем легенду
        fig.update_layout(showlegend=True, height=700)

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"Для выбранной даты и района ({selected_district}) нет данных о вероятности чрезвычайных ситуаций.")




# # Обработка нажатия на вкладку "Отчет"
# with doc:

#     st.header("Сохранение отчета")



# # Обработка нажатия на вкладку "Загрузка"
# with upload:
#     st.header("Загрузка файла")
#     st.markdown(
#         f"""
#         <style>
#         hr {{
#             border: 1px solid #dfdfdf;
#         }}
#         </style>
#         <hr>
#         """
#         , unsafe_allow_html=True
#     )
#     file=st.file_uploader("Пожалуйста загрузите файл")
#     if file is not None:
#         # Чтение CSV-файла
#         df = pd.read_csv(file)
#         # Отображение таблицы
#         st.table(df)