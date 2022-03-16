
import os
from django.shortcuts import render
import plotly.graph_objects as go
import numpy as np
import plotly.express as px
import pandas as pd
from plotly.offline import plot

from dashboard.settings import BASE_DIR


def plot_fig(fig):
    return plot(fig, auto_open=False, output_type='div', include_plotlyjs="cdn")


def handle_df(path):
    df = pd.read_csv(os.path.join(BASE_DIR, path))
    df = df.drop(
        columns=['Lat', 'Long']).groupby(by='Country/Region').aggregate(np.sum).T
    df.index.name = 'Data'
    df = df.reset_index()
    melt_df = df.melt(id_vars='Data').copy()
    melt_df['Data'] = pd.to_datetime(melt_df['Data'])
    melt_df['Data'] = melt_df['Data'].dt.strftime('%m/%d/%y')

    return melt_df


melt_df = handle_df("time_series_covid19_confirmed_global.csv")
melt_df.rename(columns={'value': 'Confirmed'}, inplace=True)

deaths_melt_df = handle_df("time_series_covid19_deaths_global.csv")
deaths_melt_df.rename(columns={'value': 'Deaths'}, inplace=True)

recovered_melt_df = handle_df(
    "time_series_covid19_recovered_global.csv")
recovered_melt_df.rename(columns={'value': 'recovered'}, inplace=True)

max_data = melt_df['Data'].max()

total_confirmed_df = melt_df[melt_df['Data'] == max_data]

total_deaths_df = deaths_melt_df[deaths_melt_df['Data'] == max_data]
total_deaths = total_deaths_df['Deaths'].sum()

total_recovered_df = recovered_melt_df[recovered_melt_df['Data'] == max_data]
total_recovered = total_recovered_df['recovered'].sum()

total_confirmed = total_confirmed_df['Confirmed'].sum()

total_active = total_confirmed - total_deaths - total_recovered


def dahsboard(request):

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode='number', value=int(total_confirmed),
        number={"valueformat": "O,f"},
        title={"text": "Total Confirmed Cases"},
        domain={"row": 0, "column": 0}
    ))
    fig.add_trace(go.Indicator(
        mode='number', value=int(total_deaths),
        number={"valueformat": "O,f"},
        title={"text": "Total deaths Cases"},
        domain={"row": 0, "column": 1}
    ))
    fig.add_trace(go.Indicator(
        mode='number', value=int(total_recovered),
        number={"valueformat": "O,f"},
        title={"text": "Total Recovered Cases"},
        domain={"row": 1, "column": 0}
    ))
    fig.add_trace(go.Indicator(
        mode='number', value=int(total_active),
        number={"valueformat": "O,f"},
        title={"text": "Total Active Cases"},
        domain={"row": 1, "column": 1}
    ))
    fig.update_layout(
        grid={'rows': 2, 'columns': 2, 'pattern': 'independent'})

    data = {
        "fig": plot_fig(fig),

    }
    return render(request, "dashboard.html", context=data)


def map(request):
    fig = px.choropleth(total_confirmed_df,
                        locations='Country/Region',
                        locationmode='country names',
                        color_continuous_scale="dense",
                        title="Map overview",
                        color=np.log10(total_confirmed_df['Confirmed']),
                        range_color=(0, 10)
                        )
    return render(request, "graph.html", context={"fig": plot_fig(fig)})


def top(request):
    fig = px.bar(total_confirmed_df.sort_values(
        'Confirmed', ascending=False).head(30), x='Country/Region', y='Confirmed', title="Total confirmed cases bar diagram")
    return render(request, "graph.html", context={"fig": plot_fig(fig)})


def details(request):
    fig = px.scatter(melt_df, x='Data', y='Confirmed',
                     color='Country/Region', title="Confirmed cases per day")
    return render(request, "graph.html", context={"fig": plot_fig(fig)})
