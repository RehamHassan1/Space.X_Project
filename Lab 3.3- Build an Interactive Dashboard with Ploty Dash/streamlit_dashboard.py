import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Load and prepare data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_2.csv')
        
        # Map column names to match the expected format
        df = df.rename(columns={
            'PayloadMass': 'Payload mass',
            'LaunchSite': 'Launch site',
            'Outcome': 'Launch outcome',
            'BoosterVersion': 'Version Booster',
            'Class': 'class'
        })
        
        # Create success class if not already present
        if 'class' not in df.columns:
            df['class'] = df['Launch outcome'].apply(lambda x: 1 if 'Success' in str(x) else 0)
        
        # Convert Payload mass to numeric
        df['Payload mass'] = pd.to_numeric(df['Payload mass'], errors='coerce')
        
        # Remove rows with missing values
        df = df.dropna(subset=['Payload mass', 'class'])
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame on error

spacex_df = load_data()

# Dashboard Layout
st.title("🚀 SpaceX Launch Analytics Dashboard")

if spacex_df.empty:
    st.error("No valid data available after cleaning. Please check your dataset.")
    st.stop()  # This stops the script execution if no data is available
else:
    # Debug info (can be removed later)
    st.write("Data preview:")
    st.write(spacex_df.head())
    
    # Calculate payload range with robust error handling
    try:
        payload_min = max(0, int(np.nanmin(spacex_df['Payload mass']) - 500))
        payload_max = min(20000, int(np.nanmax(spacex_df['Payload mass']) + 500))
        default_min = int(np.nanpercentile(spacex_df['Payload mass'], 10))
        default_max = int(np.nanpercentile(spacex_df['Payload mass'], 90))
        
        # Ensure valid range
        if payload_min >= payload_max:
            payload_min = 0
            payload_max = 10000
            default_min = 2000
            default_max = 8000
    except:
        payload_min = 0
        payload_max = 10000
        default_min = 2000
        default_max = 8000

    # TASK 1: Launch Site Selector
    col1, col2 = st.columns(2)
    with col1:
        selected_site = st.selectbox(
            "Select Launch Site:",
            ['ALL'] + sorted(spacex_df['Launch site'].unique()),
            index=0
        )

    # TASK 3: Payload Range Slider
    with col2:
        payload_range = st.slider(
            "Select Payload Range (kg):",
            min_value=payload_min,
            max_value=payload_max,
            value=(default_min, default_max),
            step=100
        )

    # TASK 2: Success Pie Chart
    st.subheader("📊 Launch Success Rate")
    def update_pie_chart():
        try:
            if selected_site == 'ALL':
                data = spacex_df.groupby('Launch site')['class'].mean().reset_index()
                fig = px.pie(
                    data,
                    values='class',
                    names='Launch site',
                    title='Success Rate by Launch Site',
                    hole=0.3
                )
            else:
                site_data = spacex_df[spacex_df['Launch site'] == selected_site]
                success_rate = site_data['class'].mean()
                fig = px.pie(
                    values=[success_rate, 1-success_rate],
                    names=['Success', 'Failure'],
                    title=f'Success Rate for {selected_site}',
                    hole=0.3
                )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating pie chart: {str(e)}")

    update_pie_chart()

    # TASK 4: Payload Scatter Plot
    st.subheader("📈 Payload vs. Launch Outcome")
    def update_scatter_plot():
        try:
            low, high = payload_range
            filtered_df = spacex_df[
                (spacex_df['Payload mass'] >= low) & 
                (spacex_df['Payload mass'] <= high)
            ]
            if selected_site != 'ALL':
                filtered_df = filtered_df[filtered_df['Launch site'] == selected_site]
            
            fig = px.scatter(
                filtered_df,
                x='Payload mass',
                y='class',
                color='Version Booster',
                title='Payload Mass vs. Launch Outcome',
                labels={
                    'Payload mass': 'Payload Mass (kg)',
                    'class': 'Launch Outcome'
                }
            )
            fig.update_yaxes(
                tickvals=[0, 1],
                ticktext=['Failure', 'Success']
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating scatter plot: {str(e)}")

    update_scatter_plot()

    # Data summary
    with st.expander("ℹ️ Dataset Summary"):
        st.write(f"Total launches: {len(spacex_df)}")
        st.write(f"Payload range: {payload_min} kg to {payload_max} kg")
        st.write(f"Success rate: {spacex_df['class'].mean():.1%}")