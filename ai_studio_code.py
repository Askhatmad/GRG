import streamlit as st
import pandas as pd
import plotly.express as px
 
# --- КОНСТАНТЫ ---
CO2_PER_KM = 0.185      # кг/км
AVG_DISTANCE = 7.5      # км
FUEL_CONSUMPTION = 0.11 # л/км
GAS_PRICE = 250         # ₸/литр
XP_PER_KG_CO2 = 10
GC_PER_KG_CO2 = 5
 
# --- НАЧАЛЬНЫЕ ДАННЫЕ ---
if 'db' not in st.session_state:
    data = {
        'Класс': ['8F', '8G', '8H'],
        'Спасенный CO2 (кг)': [12.5, 8.2, 15.1],
        'Сэкономлено тенге': [1850.0, 1200.0, 2250.0],
        'XP (Опыт)': [125, 82, 151],
        'GreenCoins': [62, 41, 75]
    }
    st.session_state.db = pd.DataFrame(data)
 
# --- РАСЧЕТ ЭКОНОМИИ ---
def calculate_savings(passengers_count):
    """
    Считает экономию CO2 и денег.
    Логика: N человек едут на 1 машине вместо N машин — экономим (N-1) порции выбросов.
    """
    if passengers_count <= 1:
        return 0, 0
 
    saved_co2 = (passengers_count - 1) * AVG_DISTANCE * CO2_PER_KM
    saved_fuel = (passengers_count - 1) * AVG_DISTANCE * FUEL_CONSUMPTION
    saved_money = saved_fuel * GAS_PRICE
 
    return round(saved_co2, 4), round(saved_money, 2)
 
# --- СТРАНИЦА ---
st.set_page_config(page_title="Green Ride: Эко-Синдикат", layout="wide")
 
st.title("🍀 Green Ride: Эко-Синдикат")
st.markdown("### Система геймификации школьного карпулинга")
st.divider()
 
# --- МЕТРИКИ ШКОЛЫ ---
total_co2 = st.session_state.db['Спасенный CO2 (кг)'].sum()
total_money = st.session_state.db['Сэкономлено тенге'].sum()
 
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Спасено CO2", f"{total_co2:.2f} кг")
with col2:
    st.metric("Сэкономлено", f"{total_money:,.0f} ₸")
with col3:
    st.metric("Участники", "3 класса")
 
# --- ОСНОВНОЙ КОНТЕНТ ---
left_col, right_col = st.columns([1, 2])
 
with left_col:
    st.subheader("Регистрация поездки")
    with st.form("trip_form", clear_on_submit=True):
        selected_class = st.selectbox("Ваш класс", st.session_state.db['Класс'])
        passengers = st.slider("Учеников в экипаже", 1, 4, 1)
 
        submitted = st.form_submit_button("Подтвердить поездку")
 
        if submitted:
            if passengers > 1:
                saved_co2, saved_money = calculate_savings(passengers)
                xp_gain = int(saved_co2 * XP_PER_KG_CO2)
                gc_gain = int(saved_co2 * GC_PER_KG_CO2)
 
                idx = st.session_state.db.index[
                    st.session_state.db['Класс'] == selected_class
                ].tolist()[0]
 
                st.session_state.db.at[idx, 'Спасенный CO2 (кг)'] += saved_co2
                st.session_state.db.at[idx, 'Сэкономлено тенге'] += saved_money
                st.session_state.db.at[idx, 'XP (Опыт)'] += xp_gain
                st.session_state.db.at[idx, 'GreenCoins'] += gc_gain
 
                st.success(
                    f"✅ **Поездка засчитана!**\n\n"
                    f"CO2 сэкономлено: **{saved_co2} кг**\n\n"
                    f"Экономия: **{saved_money} ₸**\n\n"
                    f"Начислено: **+{xp_gain} XP** и **+{gc_gain} GreenCoins**"
                )
                st.balloons()
            else:
                st.warning("Бонусы начисляются только за совместные поездки — позови одноклассников!")
 
with right_col:
    st.subheader("Лидерборд классов")
 
    leaderboard_df = st.session_state.db.sort_values(
        by='Спасенный CO2 (кг)', ascending=False
    )
 
    fig = px.bar(
        leaderboard_df,
        x='Спасенный CO2 (кг)',
        y='Класс',
        orientation='h',
        text='Спасенный CO2 (кг)',
        color='Спасенный CO2 (кг)',
        color_continuous_scale='Greens',
        title="Рейтинг по вкладу в экологию"
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
 
# --- ТАБЛИЦА ---
st.subheader("Детальная статистика")
st.dataframe(
    st.session_state.db.style.highlight_max(
        axis=0, subset=['XP (Опыт)', 'GreenCoins'], color='#d4edda'
    ),
    use_container_width=True,
    hide_index=True
)
 
# --- КАК СЧИТАЕТСЯ ---
with st.expander("Как работает расчет?"):
    st.write(f"""
    - Средняя дистанция от дома до школы: **{AVG_DISTANCE} км**
    - 4 человека на 4 машинах: **{4 * AVG_DISTANCE * CO2_PER_KM:.3f} кг CO2**
    - 4 человека на 1 машине: **{1 * AVG_DISTANCE * CO2_PER_KM:.3f} кг CO2**
    - Система считает разницу между раздельными и совместной поездкой.
    - Курс: **1 кг CO2 = {XP_PER_KG_CO2} XP** и **{GC_PER_KG_CO2} GreenCoins**
    """)
