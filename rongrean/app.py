
import json
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import requests


app = dash.Dash(__name__, suppress_callback_exceptions=True)


with open('D:\\1_2567\\241_353\\p_boat\\rongrean\\rongrean\\province.json', 'r', encoding='utf-8') as file:
    geojson_data = json.load(file)

# DataFrame 
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

school_data = pd.read_csv('D:\\1_2567\\241_353\\p_boat\\rongrean\\rongrean\\graduated.csv')
merged_df = pd.merge(df, school_data, how='left', left_on='province', right_on='school_english')

# Ensure numerical columns are in the correct format
merged_df['totalstd'] = pd.to_numeric(merged_df['totalstd'], errors='coerce')
merged_df['totalfemale'] = pd.to_numeric(merged_df['totalfemale'], errors='coerce')
merged_df['totalmale'] = pd.to_numeric(merged_df['totalmale'], errors='coerce')

# Layout 
app.layout = html.Div([
    html.H1("School Statistics in Thailand", style={'textAlign': 'center'}),
    dcc.Graph(id='thailand-map'),
    html.Div(id='province-output'),
    dcc.Graph(id='bar-chart'),  
    dcc.Graph(id='pie-chart')   
])

# Callback update and click map
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

# Callback เupdate data when clicked
@app.callback(
    [Output('province-output', 'children'),
     Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure')],
    [Input('thailand-map', 'clickData')]
)
def display_province_data(click_data):
    if click_data:
        selected_province = click_data['points'][0]['location']
    else:
        selected_province = 'Surat Thani'  

    province_data = merged_df[merged_df['province'] == selected_province]
    if not province_data.empty:
        total_std = province_data['totalstd'].values[0]
        total_female = province_data['totalfemale'].values[0]
        total_male = province_data['totalmale'].values[0]

        # bar
        bar_data = pd.DataFrame({
            'Category': ['Total Students', 'Total Female', 'Total Male'],
            'Count': [total_std, total_female, total_male]
        })

        bar_fig = px.bar(
            bar_data,
            x='Category',
            y='Count',
            title=f"Information about schools in the province: {selected_province}",
            labels={'Count': 'number'},
            color='Category'
        )

        # pie
        total_std_all = merged_df['totalstd'].sum()
        total_std_selected = total_std

        pie_data = pd.DataFrame({
            'Category': ['Selected Province', 'Other Provinces'],
            'Count': [total_std_selected, total_std_all - total_std_selected]
        })

        pie_fig = px.pie(
            pie_data,
            names='Category',
            values='Count',
            title=f"Comparison of the number of students in the province {selected_province}",
            labels={'Count': 'number'}
        )

        return (
            html.Div([
                html.H4(f"Province: {selected_province}"),
                html.P(f"All students: {total_std}"),
                html.P(f"Female student: {total_female}"),
                html.P(f"Male student: {total_male}"),
            ]),
            bar_fig,
            pie_fig
        )
    return (
        "Click on a province to see more information.",
        {},
        {}
    )

# รันแอปพลิเคชัน
if __name__ == '__main__':
    app.run_server(debug=True)