import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
import traceback
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug mode toggle (only if running standalone)
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

def debug_print(message, data=None):
    """Helper function for debug output"""
    if st.session_state.debug_mode:
        st.write(f"🔍 DEBUG: {message}")
        if data is not None:
            st.json(data)
        logger.info(f"DEBUG: {message}")

def generate_weather_data():
    """Generate synthetic weather data with error handling"""
    try:
        debug_print("Generating synthetic weather data...")
        
        np.random.seed(42)
        num_points = 100
        time_index = [datetime.now() - timedelta(minutes=99-i) for i in range(num_points)]
        
        # Generate data with error checking
        temperature_data = 20 + 5 * np.sin(np.linspace(0, 3 * np.pi, num_points)) + np.random.normal(0, 0.5, num_points)
        humidity_data = 50 + 10 * np.cos(np.linspace(0, 2 * np.pi, num_points)) + np.random.normal(0, 1, num_points)
        wind_data = 10 + 3 * np.sin(np.linspace(0, 4 * np.pi, num_points)) + np.random.normal(0, 0.7, num_points)
        
        # Validate data ranges
        if np.any(temperature_data < -50) or np.any(temperature_data > 60):
            raise ValueError("Temperature data contains unrealistic values")
        if np.any(humidity_data < 0) or np.any(humidity_data > 100):
            raise ValueError("Humidity data contains unrealistic values")
        if np.any(wind_data < 0):
            raise ValueError("Wind speed data contains negative values")
        
        data = {
            'Time': time_index,
            'Temperature (°C)': temperature_data,
            'Humidity (%)': humidity_data,
            'Wind Speed (km/h)': wind_data,
        }
        
        df = pd.DataFrame(data)
        debug_print("Weather data generated successfully", {
            "shape": df.shape,
            "columns": list(df.columns),
            "temp_range": [df['Temperature (°C)'].min(), df['Temperature (°C)'].max()],
            "humidity_range": [df['Humidity (%)'].min(), df['Humidity (%)'].max()],
            "wind_range": [df['Wind Speed (km/h)'].min(), df['Wind Speed (km/h)'].max()]
        })
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error generating weather data: {str(e)}")
        if st.session_state.debug_mode:
            st.code(traceback.format_exc())
        return None

def validate_dataframe(df):
    """Validate the DataFrame for required columns and data types"""
    try:
        debug_print("Validating DataFrame...")
        
        required_columns = ['Time', 'Temperature (°C)', 'Humidity (%)', 'Wind Speed (km/h)']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Check for NaN values
        nan_counts = df.isnull().sum()
        if nan_counts.any():
            st.warning(f"⚠️ Found NaN values: {nan_counts.to_dict()}")
        
        # Check data types
        if not pd.api.types.is_datetime64_any_dtype(df['Time']):
            st.warning("⚠️ Time column is not datetime type")
        
        debug_print("DataFrame validation completed successfully")
        return True
        
    except Exception as e:
        st.error(f"❌ DataFrame validation failed: {str(e)}")
        if st.session_state.debug_mode:
            st.code(traceback.format_exc())
        return False

# Generate synthetic time-series data with error handling
df = generate_weather_data()

if df is None:
    st.error("❌ Failed to generate weather data. Please check the error messages above.")
    st.stop()

# Validate the generated data
if not validate_dataframe(df):
    st.error("❌ Data validation failed. Please check the error messages above.")
    st.stop()

def show_dashboard():
    """Display the weather dashboard with error handling"""
    try:
        st.title('Weather Dashboard')
        
        # Check if df is available
        if df is None:
            st.error("❌ No data available to display")
            return
        
        # Show current values with error handling
        st.subheader('Current Values')
        col1, col2, col3 = st.columns(3)
        
        try:
            current_temp = df['Temperature (°C)'].iloc[-1]
            col1.metric('Temperature (°C)', f"{current_temp:.1f}")
            debug_print(f"Current temperature: {current_temp:.1f}°C")
        except Exception as e:
            col1.error(f"Error loading temperature: {str(e)}")
            debug_print(f"Temperature loading error: {str(e)}")
            
        try:
            current_humidity = df['Humidity (%)'].iloc[-1]
            col2.metric('Humidity (%)', f"{current_humidity:.1f}")
            debug_print(f"Current humidity: {current_humidity:.1f}%")
        except Exception as e:
            col2.error(f"Error loading humidity: {str(e)}")
            debug_print(f"Humidity loading error: {str(e)}")
            
        try:
            current_wind = df['Wind Speed (km/h)'].iloc[-1]
            col3.metric('Wind Speed (km/h)', f"{current_wind:.1f}")
            debug_print(f"Current wind speed: {current_wind:.1f} km/h")
        except Exception as e:
            col3.error(f"Error loading wind speed: {str(e)}")
            debug_print(f"Wind speed loading error: {str(e)}")

        st.markdown('---')

        # Line charts with error handling
        st.subheader('Trends Over Time')
        try:
            chart_data = df.set_index('Time')[['Temperature (°C)', 'Humidity (%)', 'Wind Speed (km/h)']]
            st.line_chart(chart_data)
            debug_print("Chart displayed successfully")
        except Exception as e:
            st.error(f"❌ Error displaying chart: {str(e)}")
            if st.session_state.debug_mode:
                st.code(traceback.format_exc())
        
        # Add data summary in debug mode
        if st.session_state.debug_mode:
            st.markdown('---')
            st.subheader('🔧 Data Summary')
            st.write(f"**Data Points:** {len(df)}")
            st.write(f"**Time Range:** {df['Time'].min()} to {df['Time'].max()}")
            st.write("**Statistics:**")
            st.dataframe(df.describe())
        
        st.success("✅ Dashboard displayed successfully")
        
    except Exception as e:
        st.error(f"❌ Error displaying dashboard: {str(e)}")
        if st.session_state.debug_mode:
            st.code(traceback.format_exc())

# Only run the dashboard if this file is run directly
if __name__ == "__main__":
    # Add debug mode toggle for standalone execution
    st.session_state.debug_mode = st.sidebar.checkbox("🔧 Debug Mode", value=False)
    
    # Add system information in debug mode
    if st.session_state.debug_mode:
        st.sidebar.subheader("🔧 System Info")
        st.sidebar.write(f"Python: {sys.version.split()[0]}")
        st.sidebar.write(f"Streamlit: {st.__version__}")
        st.sidebar.write(f"Pandas: {pd.__version__}")
        st.sidebar.write(f"Numpy: {np.__version__}")
    
    show_dashboard() 