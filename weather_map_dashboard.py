import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import logging
import traceback
import sys

# Import dashboard functionality
try:
    import dashboard
    st.success("✅ Successfully imported dashboard module")
except ImportError as e:
    st.error(f"❌ Failed to import dashboard module: {e}")
    st.stop()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug mode toggle
debug_mode = st.sidebar.checkbox("🔧 Debug Mode", value=False)

def debug_print(message, data=None):
    """Helper function for debug output"""
    if debug_mode:
        st.write(f"🔍 DEBUG: {message}")
        if data is not None:
            st.json(data)
        logger.info(f"DEBUG: {message}")

try:
    # Load Singapore regions GeoJSON
    debug_print("Loading Singapore regions GeoJSON file...")
    regions_gdf = gpd.read_file('singapore_regions.geojson')
    debug_print("GeoJSON loaded successfully", {
        "shape": regions_gdf.shape,
        "columns": list(regions_gdf.columns),
        "regions": list(regions_gdf['region'].unique()) if 'region' in regions_gdf.columns else "No 'region' column found"
    })
    
    if regions_gdf.empty:
        st.error("❌ No data found in the GeoJSON file")
        st.stop()
        
except FileNotFoundError:
    st.error("❌ File 'singapore_regions.geojson' not found. Please ensure the file exists in the current directory.")
    st.stop()
except Exception as e:
    st.error(f"❌ Error loading GeoJSON file: {str(e)}")
    if debug_mode:
        st.code(traceback.format_exc())
    st.stop()

try:
    # Generate synthetic temperature data for each region
    debug_print("Generating synthetic temperature data...")
    np.random.seed(42)
    regions_gdf['Temperature'] = np.random.uniform(26, 34, size=len(regions_gdf))
    debug_print("Temperature data generated", {
        "min_temp": regions_gdf['Temperature'].min(),
        "max_temp": regions_gdf['Temperature'].max(),
        "mean_temp": regions_gdf['Temperature'].mean()
    })
except Exception as e:
    st.error(f"❌ Error generating temperature data: {str(e)}")
    if debug_mode:
        st.code(traceback.format_exc())
    st.stop()

try:
    # Create a folium map centered on Singapore
    debug_print("Creating folium map...")
    m = folium.Map(location=[1.35, 103.82], zoom_start=11)
    debug_print("Map created successfully")
except Exception as e:
    st.error(f"❌ Error creating map: {str(e)}")
    if debug_mode:
        st.code(traceback.format_exc())
    st.stop()

try:
    # Add choropleth layer
    debug_print("Adding choropleth layer...")
    folium.Choropleth(
        geo_data=regions_gdf,
        name='choropleth',
        data=regions_gdf,
        columns=['region', 'Temperature'],
        key_on='feature.properties.region',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Temperature (°C)',
        highlight=True
    ).add_to(m)
    debug_print("Choropleth layer added successfully")
except KeyError as e:
    st.error(f"❌ Missing required column: {e}")
    if debug_mode:
        st.write("Available columns:", list(regions_gdf.columns))
    st.stop()
except Exception as e:
    st.error(f"❌ Error adding choropleth layer: {str(e)}")
    if debug_mode:
        st.code(traceback.format_exc())
    st.stop()

try:
    # Add tooltips
    debug_print("Adding tooltips...")
    tooltip_count = 0
    for idx, r in regions_gdf.iterrows():
        try:
            sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
            geo_j = sim_geo.to_json()
            folium.GeoJson(
                data=geo_j,
                style_function=lambda x: {'fillColor': '#transparent', 'color': 'black', 'weight': 1, 'fillOpacity': 0},
                tooltip=folium.Tooltip(f"{r['region']}: {r['Temperature']:.1f} °C")
            ).add_to(m)
            tooltip_count += 1
        except Exception as tooltip_error:
            debug_print(f"Warning: Failed to add tooltip for region {r.get('region', idx)}: {tooltip_error}")
            continue
    
    debug_print(f"Tooltips added successfully for {tooltip_count} regions")
except Exception as e:
    st.error(f"❌ Error adding tooltips: {str(e)}")
    if debug_mode:
        st.code(traceback.format_exc())

# Main dashboard interface
st.title('Singapore Weather Tracker')

# Add tabs to organize the dashboard
tab1, tab2, tab3 = st.tabs(["Weather Map", "Time Series Data", "Debug Info"])

with tab1:
    st.markdown('### Singapore Weather Map')
    try:
        st_folium(m, width=700, height=500)
        st.success("✅ Map displayed successfully")
    except Exception as e:
        st.error(f"❌ Error displaying map: {str(e)}")
        if debug_mode:
            st.code(traceback.format_exc())

with tab2:
    try:
        # Check if dashboard data is available
        if dashboard.df is None:
            st.error("❌ No time series data available")
        else:
            # Call the dashboard functionality
            st.subheader('Current Values')
            col1, col2, col3 = st.columns(3)
            
            # Add error handling for each metric
            try:
                current_temp = dashboard.df['Temperature (°C)'].iloc[-1]
                col1.metric('Temperature (°C)', f"{current_temp:.1f}")
            except Exception as e:
                col1.error(f"Error loading temperature: {str(e)}")
                
            try:
                current_humidity = dashboard.df['Humidity (%)'].iloc[-1]
                col2.metric('Humidity (%)', f"{current_humidity:.1f}")
            except Exception as e:
                col2.error(f"Error loading humidity: {str(e)}")
                
            try:
                current_wind = dashboard.df['Wind Speed (km/h)'].iloc[-1]
                col3.metric('Wind Speed (km/h)', f"{current_wind:.1f}")
            except Exception as e:
                col3.error(f"Error loading wind speed: {str(e)}")

            st.markdown('---')
            st.subheader('Trends Over Time')
            st.line_chart(dashboard.df.set_index('Time')[['Temperature (°C)', 'Humidity (%)', 'Wind Speed (km/h)']])
            st.success("✅ Time series data displayed successfully")
        
    except Exception as e:
        st.error(f"❌ Error displaying time series data: {str(e)}")
        if debug_mode:
            st.code(traceback.format_exc())

with tab3:
    if debug_mode:
        st.subheader("🔧 Debug Information")
        
        # System information
        st.write("**System Information:**")
        st.write(f"- Python version: {sys.version}")
        st.write(f"- Streamlit version: {st.__version__}")
        
        # Data information
        st.write("**Data Information:**")
        st.write(f"- Regions DataFrame shape: {regions_gdf.shape}")
        if dashboard.df is not None:
            st.write(f"- Time series DataFrame shape: {dashboard.df.shape}")
        else:
            st.write("- Time series DataFrame: Not available")
        
        # Memory usage (approximate)
        st.write("**Memory Usage (approximate):**")
        st.write(f"- Regions data: {regions_gdf.memory_usage(deep=True).sum() / 1024:.2f} KB")
        if dashboard.df is not None:
            st.write(f"- Time series data: {dashboard.df.memory_usage(deep=True).sum() / 1024:.2f} KB")
        else:
            st.write("- Time series data: Not available")
        
        # Data samples
        st.write("**Sample Data:**")
        st.write("Regions data:")
        st.dataframe(regions_gdf.head())
        
        st.write("Time series data:")
        if dashboard.df is not None:
            st.dataframe(dashboard.df.head())
        else:
            st.write("No time series data available")
        
    else:
        st.info("Enable Debug Mode in the sidebar to see debug information")

# Success message
if not debug_mode:
    st.sidebar.success("✅ Dashboard loaded successfully!") 