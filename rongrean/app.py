
import json
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import requests

# สร้างแอปพลิเคชัน Dash
app = dash.Dash(__name__)

with open('D:\\1_2567\\241_353\\p_boat\\rongrean\\rongrean\\province.json', 'r', encoding='utf-8') as file:
    geojson_data = json.load(file)

# สร้าง DataFrame ตัวอย่าง
provinces = [
    "Amnat Charoen", "Ang Thong", "Bangkok Metropolis", "Bueng Kan", "Buri Ram", "Chachoengsao",
    "Chai Nat", "Chaiyaphum", "Chanthaburi", "Chiang Mai", "Chiang Rai", "Chonburi",
    "Chumphon", "Kalasin", "Kamphaeng Phet", "Kanchanaburi", "Khon Kaen", "Krabi",
    "Lampang", "Lamphun", "Loei", "Lop Buri", "Mae Hong Son", "Maha Sarakham",
    "Mukdahan", "Nakhon Nayok", "Nakhon Pathom", "Nakhon Phanom", "Nakhon Ratchasima",
    "Nakhon Sawan", "Nakhon Si Thammarat", "Nan", "Narathiwat", "Nong Bua Lam Phu",
    "Nong Khai", "Nonthaburi", "Pathum Thani", "Pattani", "Phang Nga", "Phatthalung",
    "Phayao", "Phetchabun", "Phetchaburi", "Phichit", "Phitsanulok", "Phra Nakhon Si Ayutthaya",
    "Phrae", "Phuket", "Prachin Buri", "Prachuap Khiri Khan", "Ranong", "Ratchaburi",
    "Rayong", "Roi Et", "Sa Kaeo", "Sakon Nakhon", "Samut Prakan", "Samut Sakhon",
    "Samut Songkhram", "Saraburi", "Satun", "Si Sa Ket", "Sing Buri", "Songkhla",
    "Sukhothai", "Suphan Buri", "Surat Thani", "Surin", "Tak", "Trang", "Trat",
    "Ubon Ratchathani", "Udon Thani", "Uthai Thani", "Uttaradit", "Yala", "Yasothon"
]

data = {
    'province': provinces,
    'value': [i % 100 for i in range(77)]
}
df = pd.DataFrame(data)

# อ่านข้อมูลจากไฟล์ CSV
school_data = pd.read_csv('D:\\1_2567\\241_353\\p_boat\\rongrean\\rongrean\\graduated.csv')
# เชื่อมคอลัมน์ 'province' กับ 'school_english'
merged_df = pd.merge(df, school_data, how='left', left_on='province', right_on='school_english')

# print(merged_df.head())

# Layout ของ Dash
app.layout = html.Div([
    html.H1("แผนที่ประเทศไทย", style={'textAlign': 'center'}),
    dcc.Graph(id='thailand-map'),
    html.Div(id='province-output'),
    html.Div(id='school-output')  # ส่วนแสดงข้อมูลโรงเรียน
])

# Callback เพื่ออัปเดตแผนที่และจัดการการคลิกที่จังหวัด
@app.callback(
    Output('thailand-map', 'figure'),
    [Input('thailand-map', 'clickData')]
)
def update_map(click_data):
    fig = px.choropleth_mapbox(
        merged_df,
        geojson=geojson_data,
        locations='province',
        featureidkey='properties.name',
        color='value',
        color_continuous_scale="Plasma",
        mapbox_style="carto-positron",
        center={"lat": 13.736717, "lon": 100.523186},
        zoom=5
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    if click_data:
        selected_province = click_data['points'][0]['location']
        fig.update_traces(
            marker=dict(size=10, color='red'),
            selector=dict(type='scattermapbox', customdata=merged_df[merged_df['province'] == selected_province]['value'])
        )

    return fig

# Callback 
@app.callback(
    Output('province-output', 'children'),
    Output('school-output', 'children'),
    [Input('thailand-map', 'clickData')]
)
def display_province_data(click_data):
    if click_data:
        selected_province = click_data['points'][0]['location']
        province_data = merged_df[merged_df['province'] == selected_province]
        if not province_data.empty:
            total_std = province_data['totalstd'].values[0]
            total_female = province_data['totalfemale'].values[0]
            total_male = province_data['totalmale'].values[0]
            return (
                html.Div([
                    html.H4(f"จังหวัด: {selected_province}"),
                    html.P(f"ค่า: {province_data['value'].values[0]}"),
                ]),
                html.Div([
                    html.H4(f"ข้อมูลโรงเรียนในจังหวัด: {selected_province}"),
                    html.P(f"นักเรียนทั้งหมด: {total_std}"),
                    html.P(f"นักเรียนหญิง: {total_female}"),
                    html.P(f"นักเรียนชาย: {total_male}")
                ])
            )
    return (
        "คลิกที่จังหวัดเพื่อดูข้อมูลเพิ่มเติม.",
        ""
    )

# รันแอปพลิเคชัน
if __name__ == '__main__':
    app.run_server(debug=True)