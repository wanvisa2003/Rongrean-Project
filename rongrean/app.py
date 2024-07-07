

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import requests
import json

# สร้างแอปพลิเคชัน Dash
app = dash.Dash(__name__)

# โหลดข้อมูล GeoJSON ของประเทศไทยจาก SimpleMaps
geojson_url = 'https://simplemaps.com/static/svg/country/th/admin1/th.json'
geojson_data = requests.get(geojson_url).json()

# สร้าง DataFrame ตัวอย่าง

provinces = [
    "Amnat Charoen", "Ang Thong", "Bangkok", "Bueng Kan", "Buriram", "Chachoengsao",
    "Chai Nat", "Chaiyaphum", "Chanthaburi", "Chiang Mai", "Chiang Rai", "Chonburi",
    "Chumphon", "Kalasin", "Kamphaeng Phet", "Kanchanaburi", "Khon Kaen", "Krabi",
    "Lampang", "Lamphun", "Loei", "Lopburi", "Mae Hong Son", "Maha Sarakham",
    "Mukdahan", "Nakhon Nayok", "Nakhon Pathom", "Nakhon Phanom", "Nakhon Ratchasima",
    "Nakhon Sawan", "Nakhon Si Thammarat", "Nan", "Narathiwat", "Nong Bua Lam Phu",
    "Nong Khai", "Nonthaburi", "Pathum Thani", "Pattani", "Phang Nga", "Phatthalung",
    "Phayao", "Phetchabun", "Phetchaburi", "Phichit", "Phitsanulok", "Phra Nakhon Si Ayutthaya",
    "Phrae", "Phuket", "Prachinburi", "Prachuap Khiri Khan", "Ranong", "Ratchaburi",
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

# Layout ของแอปพลิเคชัน Dash
app.layout = html.Div([
    html.H1("Thailand Map", style={'textAlign': 'center'}),
    dcc.Graph(id='thailand-map'),
    html.Div(id='province-output')
])

# Callback เพื่ออัปเดตแผนที่และจัดการการคลิกที่จังหวัด
@app.callback(
    Output('thailand-map', 'figure'),
    [Input('thailand-map', 'clickData')]
)
def update_map(click_data):
    fig = px.choropleth_mapbox(
        df,
        geojson=geojson_data,
        locations='province',
        featureidkey='properties.name',
        color='value',
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron",
        center={"lat": 13.736717, "lon": 100.523186},
        zoom=5
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    if click_data:
        selected_province = click_data['points'][0]['location']
        fig.update_traces(marker=dict(line=dict(width=2, color='red')))
        fig.add_trace(
            px.scatter_mapbox(
                df[df['province'] == selected_province],
                lat=[13.736717],
                lon=[100.523186],
                text=[selected_province],
                marker=dict(size=10, color='red'),
            ).data[0]
        )

    return fig

# Callback เพื่ออัปเดตข้อมูลที่แสดงเมื่อมีการคลิกที่จังหวัด
@app.callback(
    Output('province-output', 'children'),
    [Input('thailand-map', 'clickData')]
)
def display_province_data(click_data):
    if click_data:
        selected_province = click_data['points'][0]['location']
        province_value = df[df['province'] == selected_province]['value'].values[0]
        return html.Div([
            html.H4(f"Province: {selected_province}"),
            html.P(f"Value: {province_value}")
        ])
    return "Click on a province to see more details."

# รันแอปพลิเคชัน
if __name__ == '__main__':
    app.run_server(debug=True)

