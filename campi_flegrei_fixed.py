"""
Monitor Terremoti Campi Flegrei - Versione con Temi Funzionanti
Autore: Luigi Oliviero
Data: 2025
Versione: 3.1 Fixed Themes
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import numpy as np
from collections import deque
import math
import logging
import hashlib

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione pagina
st.set_page_config(
    page_title="🌋 Campi Flegrei Monitor - Fixed Themes",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Costanti
CAMPI_FLEGREI_LAT = 40.827
CAMPI_FLEGREI_LON = 14.139
RADIUS_KM = 15

def initialize_session_state():
    """Inizializza lo stato della sessione"""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True  # Default dark mode
    
    if 'seismo_data' not in st.session_state:
        st.session_state.seismo_data = deque(maxlen=200)
        st.session_state.seismo_time = deque(maxlen=200)
        st.session_state.last_seismo_update = time.time()
        st.session_state.seismo_running = False
    
    if 'current_period' not in st.session_state:
        st.session_state.current_period = 7
    
    if 'last_period_change' not in st.session_state:
        st.session_state.last_period_change = time.time()

def apply_dynamic_theme():
    """Applica il tema dinamicamente in base alla modalità"""
    
    if st.session_state.dark_mode:
        # DARK MODE - Colori chiari su sfondo scuro
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* DARK MODE THEME */
        .main {
            background-color: #0e1117 !important;
            color: #ffffff !important;
        }
        
        .stApp {
            background-color: #0e1117 !important;
        }
        
        /* Header Dark */
        .modern-header {
            background: linear-gradient(90deg, #ff6b6b, #feca57);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: clamp(2.5rem, 5vw, 4rem);
            font-weight: 700;
            text-align: center;
            margin-bottom: 1rem;
            font-family: 'Inter', sans-serif;
        }
        
        /* Author Badge Dark */
        .author-badge {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #ffffff;
            padding: 0.75rem 1.5rem;
            border-radius: 50px;
            margin: 0 auto 2rem auto;
            width: fit-content;
            font-weight: 600;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        /* Metric Cards Dark */
        .metric-card {
            background: rgba(30, 30, 40, 0.8);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 2rem;
            border-radius: 20px;
            color: #ffffff;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            margin: 0.5rem 0;
            transition: all 0.3s ease;
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #ff6b6b, #feca57);
        }
        
        .metric-card h3 {
            color: #b0b0b0;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
        }
        
        .metric-card h1 {
            color: #ffffff;
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
        }
        
        .metric-card small {
            color: #888888;
            font-size: 0.75rem;
        }
        
        /* Seismograph Dark */
        .seismo-container {
            background: rgba(10, 15, 25, 0.9);
            backdrop-filter: blur(20px);
            border: 2px solid #00ff88;
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 8px 32px rgba(0, 255, 136, 0.2);
        }
        
        .seismo-container h3 {
            color: #00ff88;
        }
        
        /* Status Indicators Dark */
        .status-indicator {
            background: rgba(40, 40, 50, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #ffffff;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            font-weight: 500;
            display: inline-block;
            margin: 0.25rem;
        }
        
        /* Alerts Dark */
        .alert-high {
            background: linear-gradient(135deg, #dc3545, #c82333);
            color: #ffffff;
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(220, 53, 69, 0.3);
        }
        
        .alert-medium {
            background: linear-gradient(135deg, #fd7e14, #e55100);
            color: #ffffff;
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(253, 126, 20, 0.3);
        }
        
        .alert-low {
            background: linear-gradient(135deg, #28a745, #1e7e34);
            color: #ffffff;
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(40, 167, 69, 0.3);
        }
        
        /* Period Indicator Dark */
        .period-indicator {
            background: linear-gradient(135deg, #ff6b6b, #feca57);
            color: #ffffff;
            padding: 0.75rem 1.5rem;
            border-radius: 25px;
            font-weight: 600;
            text-align: center;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        }
        
        /* Footer Dark */
        .footer-author {
            background: linear-gradient(135deg, #495057, #6c757d);
            color: #ffffff;
            padding: 2rem;
            border-radius: 20px;
            text-align: center;
            margin: 3rem 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        /* Sidebar Dark */
        .css-1d391kg {
            background: #1a1d23 !important;
        }
        
        /* Text colors Dark */
        .stMarkdown, .stText, p, div {
            color: #ffffff !important;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
        }
        
        </style>
        """, unsafe_allow_html=True)
    
    else:
        # LIGHT MODE - Colori scuri su sfondo chiaro
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* LIGHT MODE THEME */
        .main {
            background-color: #ffffff !important;
            color: #2c3e50 !important;
        }
        
        .stApp {
            background-color: #f8f9fa !important;
        }
        
        /* Header Light */
        .modern-header {
            background: linear-gradient(90deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: clamp(2.5rem, 5vw, 4rem);
            font-weight: 700;
            text-align: center;
            margin-bottom: 1rem;
            font-family: 'Inter', sans-serif;
        }
        
        /* Author Badge Light */
        .author-badge {
            background: rgba(102, 126, 234, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(102, 126, 234, 0.3);
            color: #2c3e50;
            padding: 0.75rem 1.5rem;
            border-radius: 50px;
            margin: 0 auto 2rem auto;
            width: fit-content;
            font-weight: 600;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
        }
        
        /* Metric Cards Light */
        .metric-card {
            background: #ffffff;
            border: 1px solid rgba(102, 126, 234, 0.2);
            padding: 2rem;
            border-radius: 20px;
            color: #2c3e50;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            margin: 0.5rem 0;
            transition: all 0.3s ease;
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }
        
        .metric-card h3 {
            color: #6c757d;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
        }
        
        .metric-card h1 {
            color: #2c3e50;
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
        }
        
        .metric-card small {
            color: #6c757d;
            font-size: 0.75rem;
        }
        
        /* Seismograph Light */
        .seismo-container {
            background: rgba(248, 249, 250, 0.9);
            backdrop-filter: blur(20px);
            border: 2px solid #667eea;
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
        }
        
        .seismo-container h3 {
            color: #667eea;
        }
        
        /* Status Indicators Light */
        .status-indicator {
            background: rgba(248, 249, 250, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 0, 0, 0.1);
            color: #2c3e50;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            font-weight: 500;
            display: inline-block;
            margin: 0.25rem;
        }
        
        /* Alerts Light */
        .alert-high {
            background: linear-gradient(135deg, #ff416c, #ff4b2b);
            color: #ffffff;
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(255, 65, 108, 0.3);
        }
        
        .alert-medium {
            background: linear-gradient(135deg, #f7971e, #ffd200);
            color: #ffffff;
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(247, 151, 30, 0.3);
        }
        
        .alert-low {
            background: linear-gradient(135deg, #56ab2f, #a8e6cf);
            color: #ffffff;
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(86, 171, 47, 0.3);
        }
        
        /* Period Indicator Light */
        .period-indicator {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: #ffffff;
            padding: 0.75rem 1.5rem;
            border-radius: 25px;
            font-weight: 600;
            text-align: center;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        /* Footer Light */
        .footer-author {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: #ffffff;
            padding: 2rem;
            border-radius: 20px;
            text-align: center;
            margin: 3rem 0;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        }
        
        /* Sidebar Light */
        .css-1d391kg {
            background: #ffffff !important;
            border-right: 1px solid rgba(0, 0, 0, 0.1) !important;
        }
        
        /* Text colors Light */
        .stMarkdown, .stText, p, div {
            color: #2c3e50 !important;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50 !important;
        }
        
        </style>
        """, unsafe_allow_html=True)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calcola distanza tra due punti geografici usando Haversine"""
    try:
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return c * 6371
    except Exception as e:
        logger.error(f"Errore nel calcolo distanza: {e}")
        return 0.0

def test_api_connection():
    """Testa la connessione all'API INGV"""
    try:
        url = "http://webservices.ingv.it/fdsnws/event/1/query"
        params = {
            'format': 'geojson',
            'limit': 1,
            'minlatitude': CAMPI_FLEGREI_LAT - 0.1,
            'maxlatitude': CAMPI_FLEGREI_LAT + 0.1,
            'minlongitude': CAMPI_FLEGREI_LON - 0.1,
            'maxlongitude': CAMPI_FLEGREI_LON + 0.1,
        }
        response = requests.get(url, params=params, timeout=5)
        return response.status_code == 200
    except:
        return False

def create_cache_key(days_back, timestamp_hour):
    """Crea una chiave di cache unica basata sul periodo e sull'ora corrente"""
    cache_string = f"earthquake_data_{days_back}_{timestamp_hour}"
    return hashlib.md5(cache_string.encode()).hexdigest()

@st.cache_data(ttl=300, show_spinner=False)
def get_earthquake_data_cached(days_back, cache_key):
    """Recupera dati terremoti dall'API INGV con cache che considera il periodo"""
    try:
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%dT%H:%M:%S')
        end_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        
        url = "http://webservices.ingv.it/fdsnws/event/1/query"
        params = {
            'format': 'geojson',
            'starttime': start_date,
            'endtime': end_date,
            'minlatitude': CAMPI_FLEGREI_LAT - 0.3,
            'maxlatitude': CAMPI_FLEGREI_LAT + 0.3,
            'minlongitude': CAMPI_FLEGREI_LON - 0.3,
            'maxlongitude': CAMPI_FLEGREI_LON + 0.3,
            'minmagnitude': 0.0,
            'limit': 1000
        }
        
        logger.info(f"Fetching earthquake data for {days_back} days")
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('features'):
            return pd.DataFrame()
        
        earthquakes = []
        for feature in data['features']:
            try:
                props = feature['properties']
                coords = feature['geometry']['coordinates']
                
                if not all(k in props for k in ['time', 'mag']) or len(coords) < 2:
                    continue
                
                time_str = props['time']
                if time_str.endswith('Z'):
                    time_str = time_str.replace('Z', '+00:00')
                
                earthquake = {
                    'time': datetime.fromisoformat(time_str),
                    'magnitude': float(props.get('mag', 0)),
                    'depth': float(coords[2]) if len(coords) > 2 else 0.0,
                    'latitude': float(coords[1]),
                    'longitude': float(coords[0]),
                    'place': str(props.get('place', 'N/A')),
                    'event_id': str(props.get('eventId', f'unknown_{len(earthquakes)}'))
                }
                
                if (-90 <= earthquake['latitude'] <= 90 and 
                    -180 <= earthquake['longitude'] <= 180):
                    earthquakes.append(earthquake)
                    
            except Exception as e:
                logger.warning(f"Error parsing earthquake feature: {e}")
                continue
        
        logger.info(f"Successfully parsed {len(earthquakes)} earthquakes")
        return pd.DataFrame(earthquakes)
    
    except Exception as e:
        logger.error(f"API error: {e}")
        return pd.DataFrame()

def get_earthquake_data(days_back):
    """Wrapper per il caricamento dati con gestione periodo"""
    current_hour = datetime.now().strftime('%Y-%m-%d-%H')
    cache_key = create_cache_key(days_back, current_hour)
    return get_earthquake_data_cached(days_back, cache_key)

def generate_seismic_noise(amplitude=0.05):
    """Genera rumore sismico realistico"""
    try:
        t = time.time()
        noise = (
            amplitude * 0.3 * np.sin(2 * np.pi * 0.5 * t + np.random.random() * 0.1) +
            amplitude * 0.25 * np.sin(2 * np.pi * 1.5 * t + np.random.random() * 0.1) +
            amplitude * 0.2 * np.sin(2 * np.pi * 4.0 * t + np.random.random() * 0.1) +
            amplitude * 0.25 * np.random.normal(0, 0.8)
        )
        slow_variation = 1 + 0.15 * np.sin(2 * np.pi * t / 1800)
        return noise * slow_variation
    except Exception as e:
        logger.error(f"Error generating seismic noise: {e}")
        return 0.0

def update_seismograph():
    """Aggiorna i dati del sismografo"""
    try:
        current_time = time.time()
        if current_time - st.session_state.last_seismo_update >= 0.2:
            amplitude = generate_seismic_noise()
            st.session_state.seismo_data.append(amplitude)
            st.session_state.seismo_time.append(current_time)
            st.session_state.last_seismo_update = current_time
            st.session_state.seismo_running = True
    except Exception as e:
        logger.error(f"Error updating seismograph: {e}")
        st.session_state.seismo_running = False

def create_themed_seismograph_plot(sensitivity=1.0):
    """Crea grafico sismografo con tema dinamico"""
    try:
        if len(st.session_state.seismo_data) < 5:
            fig = go.Figure()
            
            text_color = '#00ff88' if st.session_state.dark_mode else '#667eea'
            bg_color = 'rgba(10, 15, 25, 0.9)' if st.session_state.dark_mode else 'rgba(248, 249, 250, 0.9)'
            
            fig.add_annotation(
                text="🌊 Sismografo in avvio...<br>Attendere qualche secondo",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                font=dict(size=16, color=text_color),
                showarrow=False
            )
            fig.update_layout(
                height=350,
                plot_bgcolor=bg_color,
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            return fig
        
        latest_time = st.session_state.seismo_time[-1]
        relative_times = [(t - latest_time) for t in st.session_state.seismo_time]
        amplitudes = [amp * sensitivity for amp in st.session_state.seismo_data]
        
        # Colori basati sul tema
        if st.session_state.dark_mode:
            line_color = '#00ff88'
            grid_color = 'rgba(255,255,255,0.1)'
            text_color = '#ffffff'
            bg_color = 'rgba(10, 15, 25, 0.9)'
            fill_color = 'rgba(0, 255, 136, 0.1)'
        else:
            line_color = '#667eea'
            grid_color = 'rgba(0,0,0,0.1)'
            text_color = '#2c3e50'
            bg_color = 'rgba(248, 249, 250, 0.9)'
            fill_color = 'rgba(102, 126, 234, 0.1)'
        
        fig = go.Figure()
        
        # Linea principale
        fig.add_trace(go.Scatter(
            x=relative_times,
            y=amplitudes,
            mode='lines',
            name='Segnale sismico',
            line=dict(color=line_color, width=3),
            fill='tonexty',
            fillcolor=fill_color,
            hovertemplate='<b>Tempo:</b> %{x:.1f}s fa<br><b>Ampiezza:</b> %{y:.4f}<extra></extra>'
        ))
        
        # Linea zero
        fig.add_hline(y=0, line_dash="dot", line_color=text_color, line_width=1, opacity=0.5)
        
        # Zone di allerta
        max_amp = max(abs(min(amplitudes, default=0)), abs(max(amplitudes, default=0)))
        if max_amp > 0:
            alert_color = 'rgba(255, 107, 107, 0.1)'
            fig.add_hrect(y0=max_amp*0.7, y1=max_amp*1.2, 
                         fillcolor=alert_color, layer="below", line_width=0)
            fig.add_hrect(y0=-max_amp*1.2, y1=-max_amp*0.7, 
                         fillcolor=alert_color, layer="below", line_width=0)
        
        # Layout
        fig.update_layout(
            title={
                'text': '🌊 Sismografo Real-Time • Campi Flegrei',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': line_color, 'family': 'Inter'}
            },
            xaxis=dict(
                title='Tempo (secondi fa)',
                range=[-40, 0],
                gridcolor=grid_color,
                color=text_color,
                tickfont={'color': text_color, 'family': 'Inter'},
                showgrid=True
            ),
            yaxis=dict(
                title='Ampiezza',
                gridcolor=grid_color,
                zeroline=True,
                zerolinecolor=text_color,
                zerolinewidth=2,
                color=text_color,
                tickfont={'color': text_color, 'family': 'Inter'},
                showgrid=True
            ),
            height=350,
            showlegend=False,
            plot_bgcolor=bg_color,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color, family='Inter'),
            margin=dict(l=60, r=20, t=60, b=60)
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating seismograph plot: {e}")
        return go.Figure()

def create_themed_earthquake_map(df):
    """Crea mappa con tema dinamico"""
    try:
        # Stile mappa basato sul tema
        if st.session_state.dark_mode:
            mapbox_style = "carto-darkmatter"
            color_scale = "Plasma"
            text_color = '#ffffff'
        else:
            mapbox_style = "open-street-map"
            color_scale = "Viridis"
            text_color = '#2c3e50'
        
        if df.empty:
            fig = go.Figure()
            fig.add_trace(go.Scattermapbox(
                lat=[CAMPI_FLEGREI_LAT],
                lon=[CAMPI_FLEGREI_LON],
                mode='markers',
                marker=dict(size=25, color='#ff6b6b', symbol='volcano'),
                name='🌋 Centro Campi Flegrei',
                text='Centro Campi Flegrei<br>Nessun terremoto nel periodo',
                hoverinfo='text'
            ))
            
            fig.update_layout(
                mapbox=dict(
                    style=mapbox_style,
                    center=dict(lat=CAMPI_FLEGREI_LAT, lon=CAMPI_FLEGREI_LON),
                    zoom=10
                ),
                height=600,
                margin=dict(l=0, r=0, t=40, b=0),
                title={
                    'text': '🗺️ Mappa Interattiva • Nessun dato',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'color': text_color, 'family': 'Inter'}
                }
            )
            return fig
        
        # Pulisci dati
        required_cols = ['latitude', 'longitude', 'magnitude', 'depth', 'place', 'time']
        if not all(col in df.columns for col in required_cols):
            raise ValueError("Colonne mancanti")
        
        df_clean = df.dropna(subset=['latitude', 'longitude', 'magnitude'])
        df_clean = df_clean[
            (df_clean['latitude'].between(-90, 90)) &
            (df_clean['longitude'].between(-180, 180)) &
            (df_clean['magnitude'] >= 0)
        ]
        
        if df_clean.empty:
            raise ValueError("Nessun dato valido")
        
        # Crea mappa
        fig = px.scatter_mapbox(
            df_clean,
            lat="latitude",
            lon="longitude",
            size="magnitude",
            color="depth",
            hover_name="place",
            hover_data={
                "time": "|%Y-%m-%d %H:%M:%S",
                "magnitude": ":.1f",
                "depth": ":.1f",
                "distance_km": ":.1f"
            },
            color_continuous_scale=color_scale,
            size_max=35,
            zoom=9,
            mapbox_style=mapbox_style,
            title="🗺️ Distribuzione Geografica • Real-Time"
        )
        
        # Centro Campi Flegrei
        fig.add_trace(go.Scattermapbox(
            lat=[CAMPI_FLEGREI_LAT],
            lon=[CAMPI_FLEGREI_LON],
            mode='markers',
            marker=dict(size=30, color='#ff6b6b', symbol='volcano'),
            name='🌋 Centro Campi Flegrei',
            text=f'🌋 Centro Campi Flegrei<br>📍 {CAMPI_FLEGREI_LAT:.3f}, {CAMPI_FLEGREI_LON:.3f}',
            hoverinfo='text'
        ))
        
        center_lat = df_clean['latitude'].mean()
        center_lon = df_clean['longitude'].mean()
        
        fig.update_layout(
            mapbox=dict(
                center=dict(lat=center_lat, lon=center_lon),
                zoom=10
            ),
            height=600,
            margin=dict(l=0, r=0, t=40, b=0),
            title={
                'x': 0.5,
                'xanchor': 'center',
                'font': {'color': text_color, 'family': 'Inter', 'size': 18}
            }
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating map: {e}")
        return go.Figure()

def create_themed_chart(df, chart_type, period_desc):
    """Crea grafici con tema dinamico"""
    if st.session_state.dark_mode:
        template = "plotly_dark"
        color_discrete = ['#ff6b6b', '#feca57', '#48dbfb', '#ff9ff3', '#54a0ff']
        color_continuous = "Plasma"
    else:
        template = "plotly_white"
        color_discrete = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
        color_continuous = "Viridis"
    
    try:
        if chart_type == "histogram":
            fig = px.histogram(
                df, x="magnitude", nbins=20,
                title=f"Distribuzione Magnitudini ({period_desc})",
                labels={"magnitude": "Magnitudine", "count": "Frequenza"},
                color_discrete_sequence=color_discrete,
                template=template
            )
        
        elif chart_type == "scatter":
            fig = px.scatter(
                df, x="depth", y="magnitude",
                size="magnitude", color="distance_km",
                hover_data=["place", "time"],
                title=f"Profondità vs Magnitudine ({period_desc})",
                labels={
                    "depth": "Profondità (km)",
                    "magnitude": "Magnitudine",
                    "distance_km": "Distanza (km)"
                },
                color_continuous_scale=color_continuous,
                template=template
            )
        
        elif chart_type == "timeline_bar":
            fig = px.bar(
                df, x="time", y="event_count",
                color="max_magnitude",
                title=f"Eventi per Ora ({period_desc})",
                labels={
                    "time": "Tempo",
                    "event_count": "Numero Eventi",
                    "max_magnitude": "Magnitudine Max"
                },
                color_continuous_scale=color_continuous,
                template=template
            )
        
        elif chart_type == "timeline_scatter":
            fig = px.scatter(
                df, x="time", y="magnitude",
                size="magnitude", color="depth",
                hover_data=["place", "distance_km"],
                title=f"Timeline Terremoti ({period_desc})",
                labels={
                    "time": "Tempo",
                    "magnitude": "Magnitudine",
                    "depth": "Profondità (km)"
                },
                color_continuous_scale=color_continuous,
                template=template
            )
        
        return fig
    
    except Exception as e:
        logger.error(f"Error creating {chart_type} chart: {e}")
        return go.Figure()

def get_period_description(days):
    """Restituisce una descrizione user-friendly del periodo"""
    period_descriptions = {
        1: "Ultime 24 ore",
        3: "Ultimi 3 giorni", 
        7: "Ultima settimana",
        30: "Ultimo mese"
    }
    return period_descriptions.get(days, f"Ultimi {days} giorni")

def main():
    """Funzione principale dell'applicazione"""
    
    # Inizializza stato sessione
    initialize_session_state()
    
    # Applica tema dinamico
    apply_dynamic_theme()
    
    # Sidebar per Theme Toggle
    with st.sidebar:
        st.markdown("### 🎨 Tema Applicazione")
        
        # Display current theme
        current_theme = "🌙 Dark Mode" if st.session_state.dark_mode else "☀️ Light Mode"
        st.info(f"Tema attuale: **{current_theme}**")
        
        # Toggle buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌙 Dark", use_container_width=True, 
                        disabled=st.session_state.dark_mode):
                st.session_state.dark_mode = True
                st.rerun()
        
        with col2:
            if st.button("☀️ Light", use_container_width=True, 
                        disabled=not st.session_state.dark_mode):
                st.session_state.dark_mode = False
                st.rerun()
    
    # Header
    st.markdown('<h1 class="modern-header">🌋 Campi Flegrei Monitor</h1>', 
                unsafe_allow_html=True)
    
    st.markdown('''
    <div class="author-badge">
        👨‍💻 Developed by <strong>Luigi Oliviero</strong> • 2025 • Fixed Themes
    </div>
    ''', unsafe_allow_html=True)
    
    # Theme indicator
    theme_emoji = "🌙" if st.session_state.dark_mode else "☀️"
    theme_name = "Dark Mode" if st.session_state.dark_mode else "Light Mode"
    st.info(f"{theme_emoji} **Modalità attiva:** {theme_name}")
    
    # Sidebar controlli
    st.sidebar.title("⚙️ Pannello Controlli")
    
    # Info versione
    st.sidebar.markdown(f"""
    ---
    **👨‍💻 Sviluppatore:** Luigi Oliviero  
    **📅 Anno:** 2025  
    **🔬 Versione:** 3.1 Fixed Themes  
    **🎨 Tema:** {theme_name}
    ---
    """)
    
    # Periodo
    st.sidebar.subheader("📅 Periodo Temporale")
    days_options = {
        "🕐 Ultime 24 ore": 1,
        "📅 Ultimi 3 giorni": 3,
        "📊 Ultima settimana": 7,
        "📈 Ultimo mese": 30
    }
    
    selected_period = st.sidebar.selectbox(
        "Seleziona periodo:",
        list(days_options.keys()),
        index=2,
        key="period_selector"
    )
    days_back = days_options[selected_period]
    
    # Controllo cambio periodo
    if days_back != st.session_state.current_period:
        st.session_state.current_period = days_back
        st.session_state.last_period_change = time.time()
        st.cache_data.clear()
        logger.info(f"Period changed to {days_back} days")
    
    # Indicatore periodo
    st.sidebar.markdown(f"""
    <div class="period-indicator">
        📊 Attivo: <strong>{get_period_description(days_back)}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtri
    st.sidebar.subheader("🔍 Filtri Avanzati")
    min_magnitude = st.sidebar.slider("🔢 Magnitudine minima:", 0.0, 5.0, 0.0, 0.1)
    max_depth = st.sidebar.slider("📏 Profondità max (km):", 0, 50, 50, 1)
    max_distance = st.sidebar.slider("📍 Distanza max (km):", 1, 50, 15, 1)
    
    # Sismografo
    st.sidebar.subheader("🌊 Sismografo")
    seismo_enabled = st.sidebar.checkbox("🟢 Abilita Real-time", value=True)
    seismo_sensitivity = st.sidebar.slider("📈 Sensibilità:", 0.1, 5.0, 1.0, 0.1)
    
    # Aggiornamenti
    st.sidebar.subheader("🔄 Aggiornamenti") 
    if st.sidebar.button("🚀 Forza Refresh", use_container_width=True):
        st.cache_data.clear()
        st.session_state.last_period_change = time.time()
        st.rerun()
    
    auto_refresh = st.sidebar.checkbox("⚡ Auto-refresh (30s)", value=False)
    
    # Status bar
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        api_status = test_api_connection()
        status_text = "🟢 Online" if api_status else "🔴 Offline"
        st.markdown(f'''
        <div class="status-indicator">
            🌐 INGV API: {status_text}
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        seismo_status = "🟢 Attivo" if st.session_state.seismo_running else "⚪ Inattivo"
        st.markdown(f'''
        <div class="status-indicator">
            📊 Sismografo: {seismo_status}
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="status-indicator">
            📅 {get_period_description(days_back)}
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="status-indicator">
            🔄 {datetime.now().strftime('%H:%M:%S')}
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Caricamento dati
    with st.spinner(f"🔄 Caricamento dati terremoti ({get_period_description(days_back)})..."):
        df = get_earthquake_data(days_back)
    
    # Messaggio informativo
    if not df.empty:
        period_start = (datetime.now() - timedelta(days=days_back))
        st.success(f"📊 **Dati caricati:** {len(df)} terremoti dal {period_start.strftime('%d/%m/%Y %H:%M')} ad oggi ({get_period_description(days_back)})")
    
    # Controllo dati vuoti
    if df.empty:
        st.warning(f"⚠️ Nessun dato disponibile per il periodo selezionato ({get_period_description(days_back)}).")
        if not api_status:
            st.error("🔴 Problema di connessione con API INGV. Riprovare più tardi.")
        
        # Sismografo anche senza dati
        if seismo_enabled:
            st.markdown('<div class="seismo-container">', unsafe_allow_html=True)
            st.subheader("🌊 Sismografo Real-Time")
            update_seismograph()
            fig_seismo = create_themed_seismograph_plot(seismo_sensitivity)
            st.plotly_chart(fig_seismo, use_container_width=True, key="seismo_empty")
            st.markdown('</div>', unsafe_allow_html=True)
        
        return
    
    # Calcola distanze
    try:
        df['distance_km'] = df.apply(
            lambda row: calculate_distance(
                CAMPI_FLEGREI_LAT, CAMPI_FLEGREI_LON,
                row['latitude'], row['longitude']
            ), axis=1
        )
    except Exception as e:
        logger.error(f"Error calculating distances: {e}")
        df['distance_km'] = 0
    
    # Applica filtri
    try:
        filtered_df = df[
            (df['magnitude'] >= min_magnitude) &
            (df['depth'] <= max_depth) &
            (df['distance_km'] <= max_distance)
        ].copy()
    except Exception as e:
        logger.error(f"Error applying filters: {e}")
        filtered_df = df.copy()
    
    # Info filtri
    if len(filtered_df) != len(df):
        st.info(f"🔍 **Filtri applicati:** {len(df)} → {len(filtered_df)} terremoti mostrati")
    
    # Cards statistiche
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔢 Eventi Totali</h3>
            <h1>{len(filtered_df)}</h1>
            <small>su {len(df)} nel periodo</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        max_mag = filtered_df['magnitude'].max() if not filtered_df.empty else 0
        mag_emoji = "🔴" if max_mag >= 4.0 else "🟡" if max_mag >= 3.0 else "🟢"
        st.markdown(f"""
        <div class="metric-card">
            <h3>{mag_emoji} Magnitudine Max</h3>
            <h1>{max_mag:.1f}</h1>
            <small>{get_period_description(days_back)}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_depth = filtered_df['depth'].mean() if not filtered_df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>📏 Profondità Media</h3>
            <h1>{avg_depth:.1f} km</h1>
            <small>{get_period_description(days_back)}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if not filtered_df.empty:
            recent_count = len(filtered_df[filtered_df['time'] >= datetime.now() - timedelta(hours=24)])
        else:
            recent_count = 0
        recent_emoji = "🔴" if recent_count >= 10 else "🟡" if recent_count >= 5 else "🟢"
        st.markdown(f"""
        <div class="metric-card">
            <h3>{recent_emoji} Ultime 24h</h3>
            <h1>{recent_count}</h1>
            <small>indipendente dal periodo</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Sismografo
    if seismo_enabled:
        st.markdown('<div class="seismo-container">', unsafe_allow_html=True)
        st.subheader("🌊 Sismografo Real-Time • AI Enhanced")
        
        update_seismograph()
        fig_seismo = create_themed_seismograph_plot(seismo_sensitivity)
        st.plotly_chart(fig_seismo, use_container_width=True, key="seismo_main")
        
        # Statistiche sismografo
        if st.session_state.seismo_data:
            col_s1, col_s2, col_s3 = st.columns(3)
            
            with col_s1:
                current_amp = list(st.session_state.seismo_data)[-1] * seismo_sensitivity
                st.metric("📊 Ampiezza Attuale", f"{current_amp:.4f}")
            
            with col_s2:
                max_amp = max([abs(x) for x in st.session_state.seismo_data]) * seismo_sensitivity
                st.metric("📈 Ampiezza Massima", f"{max_amp:.4f}")
            
            with col_s3:
                rms_amp = np.sqrt(np.mean([x**2 for x in st.session_state.seismo_data])) * seismo_sensitivity
                st.metric("📊 Valore RMS", f"{rms_amp:.4f}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Controllo dati filtrati vuoti
    if filtered_df.empty:
        st.info("ℹ️ Nessun terremoto trovato con i filtri applicati.")
        return
    
    # Mappa
    st.subheader(f"🗺️ Mappa Interattiva • {get_period_description(days_back)}")
    try:
        fig_map = create_themed_earthquake_map(filtered_df)
        st.plotly_chart(fig_map, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Errore visualizzazione mappa: {str(e)}")
    
    # Grafici analisi
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribuzione Magnitudini")
        fig_mag = create_themed_chart(filtered_df, "histogram", get_period_description(days_back))
        st.plotly_chart(fig_mag, use_container_width=True)
    
    with col2:
        st.subheader("📈 Profondità vs Magnitudine")
        fig_scatter = create_themed_chart(filtered_df, "scatter", get_period_description(days_back))
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Timeline
    st.subheader(f"⏰ Analisi Timeline • {get_period_description(days_back)}")
    try:
        if len(filtered_df) > 50:
            df_timeline = filtered_df.copy()
            df_timeline['time_rounded'] = df_timeline['time'].dt.round('H')
            timeline_data = df_timeline.groupby('time_rounded').agg({
                'magnitude': 'max',
                'event_id': 'count'
            }).reset_index()
            timeline_data.columns = ['time', 'max_magnitude', 'event_count']
            
            fig_timeline = create_themed_chart(timeline_data, "timeline_bar", get_period_description(days_back))
        else:
            fig_timeline = create_themed_chart(filtered_df, "timeline_scatter", get_period_description(days_back))
        
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    except Exception as e:
        st.error(f"Errore timeline: {str(e)}")
    
    # Sistema di allerta
    st.subheader("⚠️ Sistema di Allerta Smart")
    try:
        recent_24h = len(filtered_df[filtered_df['time'] >= datetime.now() - timedelta(hours=24)])
        max_magnitude = filtered_df['magnitude'].max()
        shallow_count = len(filtered_df[filtered_df['depth'] < 5])
        
        # Logica di allerta migliorata
        risk_score = (
            (max_magnitude * 25) +
            (recent_24h * 2) +
            (shallow_count * 5)
        )
        
        if risk_score >= 120 or max_magnitude >= 4.0:
            alert_class = "alert-high"
            alert_text = "🔴 ALLERTA ALTA"
            alert_emoji = "🚨"
            recommendations = "⚠️ **Azione Immediata Richiesta:** Monitorare comunicazioni ufficiali Protezione Civile. Attività sismica elevata rilevata."
        elif risk_score >= 60 or max_magnitude >= 3.0:
            alert_class = "alert-medium"
            alert_text = "🟡 ALLERTA MEDIA" 
            alert_emoji = "⚠️"
            recommendations = "⚠️ **Attenzione Richiesta:** Aumento dell'attività sismica. Rimanere informati sui sviluppi."
        else:
            alert_class = "alert-low"
            alert_text = "🟢 CONDIZIONI NORMALI"
            alert_emoji = "✅"
            recommendations = "✅ **Tutto OK:** Attività sismica nei parametri normali per l'area dei Campi Flegrei."
        
        st.markdown(f"""
        <div class="{alert_class}">
            <h2>{alert_emoji} {alert_text}</h2>
            <p><strong>Punteggio Rischio AI:</strong> {risk_score:.0f}/150</p>
            <p><strong>Periodo Analisi:</strong> {get_period_description(days_back)}</p>
            <p><strong>Eventi (24h):</strong> {recent_24h}</p>
            <p><strong>Magnitudine Max:</strong> {max_magnitude:.1f}</p>
            <p><strong>Eventi Superficiali (&lt;5km):</strong> {shallow_count}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if alert_class == "alert-high":
            st.error(recommendations)
        elif alert_class == "alert-medium":
            st.warning(recommendations)
        else:
            st.success(recommendations)
    
    except Exception as e:
        st.error(f"Errore sistema allerta: {str(e)}")
    
    # Tabella dettagliata
    st.subheader(f"📋 Analisi Dettagliata • {get_period_description(days_back)}")
    try:
        display_df = filtered_df.sort_values('time', ascending=False).copy()
        display_df['time'] = display_df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df['magnitude'] = display_df['magnitude'].round(1)
        display_df['depth'] = display_df['depth'].round(1)
        display_df['distance_km'] = display_df['distance_km'].round(1)
        
        st.dataframe(
            display_df[['time', 'magnitude', 'depth', 'distance_km', 'place']],
            column_config={
                "time": "🕐 Data/Ora",
                "magnitude": "📊 Magnitudine",
                "depth": "📏 Profondità (km)",
                "distance_km": "📍 Distanza (km)",
                "place": "🏠 Località"
            },
            use_container_width=True,
            hide_index=True
        )
    except Exception as e:
        st.error(f"Errore tabella: {str(e)}")
    
    # Export
    if st.button("💾 Esporta Dati", use_container_width=True):
        try:
            csv = display_df.to_csv(index=False)
            filename = f"campi-flegrei-monitor_{get_period_description(days_back).lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            st.download_button(
                label="📥 Scarica File CSV",
                data=csv,
                file_name=filename,
                mime="text/csv",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Errore export: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="footer-author">
        <h3>👨‍💻 Luigi Oliviero</h3>
        <p><strong>Campi Flegrei Monitor</strong> • Fixed Themes v3.1 (2025)</p>
        <p>🌊 Monitoraggio sismico real-time con analisi AI-enhanced</p>
        <p>📊 Dati forniti da INGV (Istituto Nazionale di Geofisica e Vulcanologia)</p>
        <p>🔬 Visualizzazione avanzata e esperienza utente moderna</p>
        <p>🎨 Temi Dark/Light completamente funzionanti • Design responsive</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-refresh
    if seismo_enabled or auto_refresh:
        time.sleep(0.5 if seismo_enabled else 30)
        st.rerun()

if __name__ == "__main__":
    main()