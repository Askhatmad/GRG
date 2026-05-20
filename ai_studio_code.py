import streamlit as st
import pandas as pd
import plotly.express as px

# --- КОНСТАНТЫ ПРОЕКТА (Согласно ТЗ) ---
CO2_PER_KM = 0.185  # кг/км
AVG_DISTANCE = 7.5  # км
FUEL_CONSUMPTION = 0.11  # литров на 1 км
GAS_PRICE = 250  # тенге за литр
XP_PER_KG_CO2 = 10
GC_PER_KG_CO2 = 5

# --- ИНИЦИАЛИЗАЦИЯ ДАННЫХ (Имитация БД) ---
if 'db' not in st.session_state:
    # Создаем начальные данные для классов
    data = {
        'Класс': ['8F', '8G', '8H'],
        'Спасенный CO2 (кг)': [12.5, 8.2, 15.1],
        'Сэкономлено тенге': [1850.0, 1200.0, 2250.0],
        'XP (Опыт)': [125, 82, 151],
        'GreenCoins': [62, 41, 75]
    }
    st.session_state.db = pd.DataFrame(data)

# --- ФУНКЦИИ РАСЧЕТА ---
def calculate_savings(passengers_count):
    """
    Рассчитывает экономию на основе количества человек в машине.
    Если едет 4 человека, экономится 3 порции выбросов (так как едет 1 машина вместо 4).
    Формула: (N - 1) * Дистанция * Коэффициент
    """
    if passengers_count <= 1:
        return 0, 0
    
    saved_co2 = (passengers_count - 1) * AVG_DISTANCE * CO2_PER_KM
    saved_fuel = (passengers_count - 1) * AVG_DISTANCE * FUEL_CONSUMPTION
    saved_money = saved_fuel * GAS_PRICE
    
    return round(saved_co2, 4), round(saved_money, 2)

# --- ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ---
st.set_page_config(page_title="Green Ride: Эко-Синдикат", layout="wide")

st.title("🍀 Green Ride: Эко-Синдикат")
st.markdown("### Прототип системы геймификации школьного карпулинга")
st.divider()

# --- ВЕРХНЯЯ ПАНЕЛЬ МЕТРИК (ОБЩИЕ ПОКАЗАТЕЛИ ШКОЛЫ) ---
total_co2 = st.session_state.db['Спасенный CO2 (кг)'].sum()
total_money = st.session_state.db['Сэкономлено тенге'].sum()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🌳 Всего спасено CO2", f"{total_co2:.2f} кг")
with col2:
    st.metric("💰 Сэкономлено средств", f"{total_money:,.0f} ₸")
with col3:
    st.metric("🚗 Участников", "3 Класса")

# --- ОСНОВНОЙ КОНТЕНТ (2 КОЛОНКИ) ---
left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("📝 Регистрация поездки")
    with st.form("trip_form", clear_on_submit=True):
        selected_class = st.selectbox("Выберите ваш класс", st.session_state.db['Класс'])
        passengers = st.slider("Сколько учеников в экипаже?", 1, 4, 1)
        
        submitted = st.form_submit_button("Подтвердить поездку")
        
        if submitted:
            if passengers > 1:
                saved_co2, saved_money = calculate_savings(passengers)
                xp_gain = int(saved_co2 * XP_PER_KG_CO2)
                gc_gain = int(saved_co2 * GC_PER_KG_CO2)
                
                # Обновляем состояние "базы данных"
                idx = st.session_state.db.index[st.session_state.db['Класс'] == selected_class].tolist()[0]
                
                st.session_state.db.at[idx, 'Спасенный CO2 (кг)'] += saved_co2
                st.session_state.db.at[idx, 'Сэкономлено тенге'] += saved_money
                st.session_state.db.at[idx, 'XP (Опыт)'] += xp_gain
                st.session_state.db.at[idx, 'GreenCoins'] += gc_gain
                
                st.success(f"""
                ✅ **Поездка засчитана!**  
                Сэкономлено CO2: **{saved_co2} кг**  
                Экономия бюджета: **{saved_money} ₸**  
                Начислено: **+{xp_gain} XP** и **+{gc_gain} GreenCoins** (распределено на экипаж).
                """)
                st.balloons()
            else:
                st.warning("⚠️ За одиночную поездку эко-бонусы не начисляются. Объединяйтесь с одноклассниками!")

with right_col:
    st.subheader("🏆 Лидерборд классов")
    
    # Сортировка данных для таблицы и графика
    leaderboard_df = st.session_state.db.sort_values(by='Спасенный CO2 (кг)', ascending=False)
    
    # Отрисовка графика Plotly
    fig = px.bar(
        leaderboard_df, 
        x='Спасенный CO2 (кг)', 
        y='Класс', 
        orientation='h',
        text='Спасенный CO2 (кг)',
        color='Спасенный CO2 (кг)',
        color_continuous_scale='Greens',
        title="Рейтинг классов по вкладу в экологию"
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# --- ТАБЛИЦА С ДЕТАЛЯМИ ---
st.subheader("📊 Детальная статистика по валюте")
st.dataframe(
    st.session_state.db.style.highlight_max(axis=0, subset=['XP (Опыт)', 'GreenCoins'], color='#d4edda'),
    use_container_width=True,
    hide_index=True
)

# --- ИНФОРМАЦИОННЫЙ БЛОК ---
with st.expander("ℹ️ Как работает расчет? (Математическая модель)"):
    st.write(f"""
    - **База:** 1 ученик живет в {AVG_DISTANCE} км от школы.
    - **Одиночка:** 4 человека на 4 машинах выбрасывают {4 * AVG_DISTANCE * CO2_PER_KM:.3f} кг CO2.
    - **Экипаж:** 4 человека на 1 машине выбрасывают только {1 * AVG_DISTANCE * CO2_PER_KM:.3f} кг CO2.
    - **Экономия:** Система считает разницу между 'если бы вы поехали отдельно' и фактической совместной поездкой.
    - **Курс:** 1 кг спасенного CO2 = {XP_PER_KG_CO2} XP и {GC_PER_KG_CO2} GreenCoins.
    """)

# Footer
st.markdown("---")
st.caption("Разработано для проекта 'Green Ride: Эко-Синдикат' | Алматы 2024")