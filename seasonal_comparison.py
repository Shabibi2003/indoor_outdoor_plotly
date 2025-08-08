import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Seasonal Data Comparison",
    page_icon="📊",
    layout='wide'
)



# Database credentials from environment variables
indoor_db_config = {
    "host": os.getenv("INDOOR_DB_HOST"),
    "user": os.getenv("INDOOR_DB_USER"),
    "password": os.getenv("INDOOR_DB_PASSWORD"),
    "database": os.getenv("INDOOR_DB_NAME")
}



# Device Data Dictionary (deviceID, address, typology, location)
device_data = {
        "1201240075": ("Hines Office, 12th Floor, One Horizon Centre, Sec-43, Gurugram", "Office","Hines Office Workstation-1"),
        "1201240078": ("Hines Office, 12th Floor, One Horizon Centre, Sec-43, Gurugram", "Office","Hines Office Workstation-2"),
        "1202240026": ("D-1/25 Vasant Vihar, New Delhi-110057(EDS Delhi)", "Office","EDS D Block Conference Room "),
        "1202240025": ("D-1/25 Vasant Vihar, New Delhi-110057(EDS Delhi)", "Office","EDS D Block Workstation"),
        "1203240081": ("26A Poorvi Marg, Vasant Vihar, New Delhi-110057 (EDS, E-Block, Delhi)", "Office","EDS E Block"),
        "1202240011": ("D-188, Abul Fazal Enclave-I, Jamia Nagar, New Delhi-110025", "Apartment","Mariyam Living Room"),
        "1202240027": ("D-188, Abul Fazal Enclave-I, Jamia Nagar, New Delhi-110025", "Apartment","Mariyam Bedroom"),
        "1203240076": ("D 184 ABUL FAZAL ENCLAVE, JAMIA NAGAR, OKHLA, NEW DELHI 25", "Midrise Apartment (G+5)","Hisham Living Room"),
        "1203240078": ("D 184 ABUL FAZAL ENCLAVE, JAMIA NAGAR, OKHLA, NEW DELHI 25", "Midrise Apartment (G+5)","Hisham Bedroom"),
        "1203240075": ("A 48/B, Third Floor, Abul Fazal Enclave Part II, New Delhi", "Residential","Shahzeb Kitchen"),
        "1201240072": ("448, Sector-9, Pocket-1 DDA Flats Dwarka, New Delhi-110075", "Residential","Lakshmi Living Room"),
        "1201240077": ("448, Sector-9, Pocket-1 DDA Flats Dwarka, New Delhi-110075", "Residential","Lakshmi Kitchen"),
        "1203240079": ("C-403, Prince Apartments, Plot 54, I.P. Extension, Patparganj, Delhi - 110092", "Residential, Multi-family","Piyush Living Room"),
        "1201240079": ("B-3/527, Ekta Gardens Apts, Patparganj, Delhi - 110092", "Residential","Piyush Bedroom"),
        "1201240085": ("B-3/527, Ekta Gardens Apts, Patparganj, Delhi - 110092", "Residential","Piyush Living Room"),
        "1203240083": ("Flat No. 25, Tower E2, Sector E1, Vasant Kunj, New Delhi", "Residential","Sheetal Living Room"),
        "1203240073": ("Flat no. 495, Block 14, Kaveri Apartments, D6, Vasant Kunj, Delhi - 110070", "Residential",'Nidhi Bedroom'),
        "1203240074": ("569 sector A pocket C Vasant Kunj, Delhi - 110070", "Residential","Ashish Living Room"),
        "1201240076": ("H No.-296 Near Durga Ashram, Chhatarpur, Delhi-110074", "Residential","Surender Living Room"),
        "1212230160": ("H No.-296 Near Durga Ashram, Chhatarpur, Delhi-110074", "Residential","Surender Bedroom"),
        "1202240009": ("D-13A 2nd Floor Left side, Paryavaran Complex, Delhi 1100030", "Office","Robin Bedroom"),
        "1202240008": ("D-13A 2nd Floor Left side, Paryavaran Complex, Delhi 1100030", "Office","Robin Living Room"),
        "1201240073": ("569 sector A pocket C Vasant Kunj, Delhi - 110070", "Residential","Tanmay Tathagat"),
        "1203240080": ("F-5, 318-N, Chirag Delhi, Delhi-110017", "Residential","Abhishek Bedroom"),
        "1201240074": ("F-5, 318-N, Chirag Delhi, Delhi-110017", "Residential","Abhishek Living Room"),
        "1203240077": ("B-2/51-A, Keshav Puram", "Apartment","Gurneet Mannat Room"),
        "1203240082": ("B-2/51-A, Keshav Puram", "Apartment","Gurneet Prabhansh Room"),
        "1202240029": ("St. Mary's School, Dwarka Sec-19", "Office","St. Mary's School (XII C)"),
        "1202240028": ("St. Mary's School, Dwarka Sec-19", "Office","St. Mary's School (sr. Library)"),
        "1202240010": ("St. Mary's School, Dwarka Sec-19", "Office","St. Mary's School (Middle Computer Lab)"),
        "1202240012": ("St. Mary's School, Dwarka Sec-19", "School","St. Mary's School (Chemistry Lab)"),
    }

# Mapping of indoor device IDs to outdoor device IDs
indoor_to_outdoor_mapping = {
        "1202240026": "THIRD_DPCC_SCR_RKPURAM",
        "1202240025": "THIRD_DPCC_SCR_RKPURAM",
        "1203240081": "THIRD_DPCC_SCR_RKPURAM",
        "1201240075": "CPCB1703205345",
        "1202240011": "DELCPCB010",
        "1202240027": "DELCPCB010",
        "1203240076": "DELCPCB010",
        "1203240078": "DELCPCB010",
        "1203240075": "DELCPCB010",
        "1201240077": "DELDPCC016",
        "1201240072": "DELDPCC016",
        "1203240079": "DELDPCC006",
        "1201240079": "DELDPCC006",
        "1201240085": "DELDPCC006",
        "1203240083": "THIRD_DPCC_SCR_RKPURAM",
        "1203240073": "DELDPCC018",
        "1203240074": "DELDPCC011",
        "1201240076": "DELDPCC018",
        "1212230160": "DELDPCC018",
        "1202240009": "DELDPCC018",
        "1202240008": "DELDPCC018",
        "1201240073": "DELDPCC018",
        "1203240080": "DELCPCB005",
        "1201240074": "DELCPCB005",
        "1203240077": "DELDPCC014",
        "1203240082": "DELDPCC014",
        "1202240029": "DELDPCC016",
        "1202240028": "DELDPCC016",
        "1202240010": "DELDPCC016",
        "1202240012": "DELDPCC016"
        
    }

def plot_seasonal_comparison(indoor_df, outdoor_df, location, pollutant):
    # Define seasons with their months and colors
    seasons = {
        "Spring": ([3, 4], '#90EE90'),      # March 2024, April 2024, March 2025
        "Summer": ([5, 6], '#FFD700'),      # May 2024, June 2024
        "Monsoon": ([7, 8, 9], '#FFA500'),  # July 2024, August 2024, September 2024
        "Autumn": ([10, 11], '#D2691E'),    # October 2024, November 2024
        "Winter": ([12, 1, 2], '#87CEEB')   # December 2024, January 2024/2025, February 2024/2025
    }

    # Create figures for both indoor and outdoor data
    fig_indoor = go.Figure()
    fig_outdoor = go.Figure()
    all_seasons_data_indoor = {}
    all_seasons_data_outdoor = {}

    # Process indoor data
    for season, (months, color) in seasons.items():
        # Filter data for each season (similar to your existing logic)
        if season == "Winter":
            seasonal_data = indoor_df[
                ((indoor_df.index.month == 12) & (indoor_df.index.year == 2024)) |
                ((indoor_df.index.month.isin([1, 2])) & (indoor_df.index.year == 2025))
            ]
        else:
            if season == "Spring":
                seasonal_data = indoor_df[
                    ((indoor_df.index.month.isin(months)) & (indoor_df.index.year == 2024)) |
                    ((indoor_df.index.month == 3) & (indoor_df.index.year == 2025))
                ]
            else:
                seasonal_data = indoor_df[
                    (indoor_df.index.month.isin(months)) & (indoor_df.index.year == 2024)
                ]

        seasonal_data = seasonal_data[seasonal_data[pollutant] != 0]
        
        if not seasonal_data.empty:
            hourly_data = seasonal_data[pollutant].groupby(seasonal_data.index.hour).mean()
            all_seasons_data_indoor[season] = hourly_data

            hours = list(range(24))
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)

            fig_indoor.add_trace(go.Scatter(
                x=hours,
                y=[hourly_data.get(hour, None) for hour in hours],
                name=f"{season}",
                line=dict(color=color),
                fill='tonexty',
                fillcolor=f"rgba({r}, {g}, {b}, 0.3)"
            ))

    # Process outdoor data (if available)
    if outdoor_df is not None:
        for season, (months, color) in seasons.items():
            # Similar seasonal filtering for outdoor data
            if season == "Winter":
                seasonal_data = outdoor_df[
                    ((outdoor_df.index.month == 12) & (outdoor_df.index.year == 2024)) |
                    ((outdoor_df.index.month.isin([1, 2])) & (outdoor_df.index.year == 2025))
                ]
            else:
                if season == "Spring":
                    seasonal_data = outdoor_df[
                        ((outdoor_df.index.month.isin(months)) & (outdoor_df.index.year == 2024)) |
                        ((outdoor_df.index.month == 3) & (outdoor_df.index.year == 2025))
                    ]
                else:
                    seasonal_data = outdoor_df[
                        (outdoor_df.index.month.isin(months)) & (outdoor_df.index.year == 2024)
                    ]

            seasonal_data = seasonal_data[seasonal_data[pollutant] != 0]
            
            if not seasonal_data.empty:
                hourly_data = seasonal_data[pollutant].groupby(seasonal_data.index.hour).mean()
                all_seasons_data_outdoor[season] = hourly_data

                hours = list(range(24))
                fig_outdoor.add_trace(go.Scatter(
                    x=hours,
                    y=[hourly_data.get(hour, None) for hour in hours],
                    name=f"{season}",
                    line=dict(color=color),
                    fill='tonexty',
                    fillcolor=f"rgba({r}, {g}, {b}, 0.1)"
                ))

    # Update layout for both figures
    fig_indoor.update_layout(
        title = dict(
            text = f"Indoor {pollutant} Seasonal Patterns - {location}",
            font = dict(size = 24)
        ),
        xaxis_title="Hour of Day",
        yaxis_title=f"{pollutant} Value",
        hovermode='x unified',
        xaxis=dict(
            tickmode='linear',
            dtick=1,
            tick0=0,
            tickvals=list(range(24)),
            ticktext=[str(i) for i in range(24)]
        )
    )

    if outdoor_df is not None:
        fig_outdoor.update_layout(
            title=f"Outdoor {pollutant} Seasonal Patterns - {location}",
            xaxis_title="Hour of Day",
            yaxis_title=f"{pollutant} Value",
            hovermode='x unified',
            xaxis=dict(
                tickmode='linear',
                dtick=1,
                tick0=0,
                tickvals=list(range(24)),
                ticktext=[str(i) for i in range(24)]
            )
        )

    # Create DataFrames for download
    indoor_download_data = pd.DataFrame()
    for season in all_seasons_data_indoor:
        indoor_download_data[season] = [all_seasons_data_indoor[season].get(hour, None) for hour in range(24)]
    indoor_download_data.index = range(24)
    indoor_download_data.index.name = 'Hour'

    if outdoor_df is not None:
        outdoor_download_data = pd.DataFrame()
        for season in all_seasons_data_outdoor:
            outdoor_download_data[season] = [all_seasons_data_outdoor[season].get(hour, None) for hour in range(24)]
        outdoor_download_data.index = range(24)
        outdoor_download_data.index.name = 'Hour'

    return fig_indoor, fig_outdoor, indoor_download_data, outdoor_download_data

def plot_seasonal_indoor_outdoor(indoor_df, outdoor_df, location, pollutant):
    seasons = {
        "Spring": ([3, 4], '#90EE90'),
        "Summer": ([5, 6], '#FFD700'),
        "Monsoon": ([7, 8, 9], '#FFA500'),
        "Autumn": ([10, 11], '#D2691E'),
        "Winter": ([12, 1, 2], '#87CEEB')
    }
    figs = []
    for season, (months, color) in seasons.items():
        if season == "Winter":
            indoor_season = indoor_df[((indoor_df.index.month == 12) & (indoor_df.index.year == 2024)) |
                                      ((indoor_df.index.month.isin([1, 2])) & (indoor_df.index.year == 2025))]
            outdoor_season = outdoor_df[((outdoor_df.index.month == 12) & (outdoor_df.index.year == 2024)) |
                                        ((outdoor_df.index.month.isin([1, 2])) & (outdoor_df.index.year == 2025))] if outdoor_df is not None else None
        else:
            if season == "Spring":
                indoor_season = indoor_df[((indoor_df.index.month.isin(months)) & (indoor_df.index.year == 2024)) |
                                          ((indoor_df.index.month == 3) & (indoor_df.index.year == 2025))]
                outdoor_season = outdoor_df[((outdoor_df.index.month.isin(months)) & (outdoor_df.index.year == 2024)) |
                                              ((outdoor_df.index.month == 3) & (outdoor_df.index.year == 2025))] if outdoor_df is not None else None
            else:
                indoor_season = indoor_df[(indoor_df.index.month.isin(months)) & (indoor_df.index.year == 2024)]
                outdoor_season = outdoor_df[(outdoor_df.index.month.isin(months)) & (outdoor_df.index.year == 2024)] if outdoor_df is not None else None
        indoor_season = indoor_season[indoor_season[pollutant] != 0]
        if outdoor_season is not None:
            outdoor_season = outdoor_season[outdoor_season[pollutant] != 0]
        fig = go.Figure()
        hours = list(range(24))
        if not indoor_season.empty:
            indoor_hourly = indoor_season[pollutant].groupby(indoor_season.index.hour).mean()
            fig.add_trace(go.Scatter(
                x=hours,
                y=[indoor_hourly.get(hour, None) for hour in hours],
                name=f"Indoor",
                line=dict(color="#1f77b4", dash='solid'),
                fill='tozeroy',
                fillcolor=f"rgba(31,119,180,0.05)"
            ))
        if outdoor_season is not None and not outdoor_season.empty:
            outdoor_hourly = outdoor_season[pollutant].groupby(outdoor_season.index.hour).mean()
            fig.add_trace(go.Scatter(
                x=hours,
                y=[outdoor_hourly.get(hour, None) for hour in hours],
                name=f"Outdoor",
                line=dict(color="#ff7f0e", dash='solid'),
                fill=None
            ))
        fig.update_layout(
            title=dict(
                text=f"{season} - Indoor vs Outdoor {pollutant} ({location})",
                font=dict(size=24)
            ),
            xaxis_title="Hour of Day",
            yaxis_title=f"{pollutant} Value",
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=20)
            ),
            xaxis=dict(
                tickmode='linear',
                dtick=1,
                tick0=0,
                tickvals=list(range(24)),
                ticktext=[str(i) for i in range(24)]
            )
        )
        figs.append(fig)

    return figs

def main():
    st.title("Seasonal Data Comparison")
    st.write("Compare indoor and outdoor air quality patterns across seasons")
    
    # Create device and pollutant selection in two columns
    col1, col2 = st.columns(2)
    with col1:
        selected_device = st.selectbox("Select Device:", list(device_data.keys()), 
                                     format_func=lambda x: f"{device_data[x][2]} ({x})")
    st.markdown("<br>", unsafe_allow_html=True)  # Add a line break for better layout

    with col2:
        pollutant_options = {
            "PM2.5": "pm25",
            "PM10": "pm10",
            "AQI": "aqi",
            "CO2": "co2",
            "VOC": "voc",
            "Temperature": "temp",
            "Humidity": "humidity"
        }
        selected_pollutant_display = st.selectbox("Select Pollutant:", list(pollutant_options.keys()))
        selected_pollutant = pollutant_options[selected_pollutant_display]

    # Assign outdoor_device_id after select boxes
    outdoor_device_id = indoor_to_outdoor_mapping.get(selected_device)

    if st.button("Generate Seasonal Comparison"):
        with st.spinner("Generating Charts...please wait"):
            try:
                # Connect to database
                conn = mysql.connector.connect(**indoor_db_config)
                cursor = conn.cursor()

                # Fetch indoor data
                indoor_query = """
                    SELECT datetime, {}
                    FROM reading_db
                    WHERE deviceID = %s 
                    AND (
                        (YEAR(datetime) = 2024)
                        OR (YEAR(datetime) = 2025 AND MONTH(datetime) <= 3)
                    )
                """.format(selected_pollutant)

                cursor.execute(indoor_query, (selected_device,))
                indoor_rows = cursor.fetchall()

                if indoor_rows:
                    indoor_df = pd.DataFrame(indoor_rows, columns=["datetime", selected_pollutant])
                    indoor_df['datetime'] = pd.to_datetime(indoor_df['datetime'])
                    indoor_df.set_index('datetime', inplace=True)
                    #remove the row if the zero valusepresent in the data
                    indoor_df = indoor_df[indoor_df[selected_pollutant]!= 0]

                    # Fetch outdoor data if mapping exists
                    outdoor_df = None
                    if outdoor_device_id:
                        outdoor_query = """
                            SELECT datetime, {}
                            FROM cpcb_data
                            WHERE deviceID = %s 
                            AND (
                                (YEAR(datetime) = 2024)
                                OR (YEAR(datetime) = 2025 AND MONTH(datetime) <= 3)
                            )
                        """.format(selected_pollutant)

                        cursor.execute(outdoor_query, (outdoor_device_id,))
                        outdoor_rows = cursor.fetchall()

                        if outdoor_rows:
                            outdoor_df = pd.DataFrame(outdoor_rows, columns=["datetime", selected_pollutant])
                            outdoor_df['datetime'] = pd.to_datetime(outdoor_df['datetime'])
                            outdoor_df.set_index('datetime', inplace=True)
                            outdoor_df=outdoor_df[outdoor_df[selected_pollutant]!= 0]

                    # Generate plots
                    fig_indoor, fig_outdoor, indoor_data, outdoor_data = plot_seasonal_comparison(
                        indoor_df, outdoor_df, device_data[selected_device][2], selected_pollutant
                    )
                    figs_seasonal = plot_seasonal_indoor_outdoor(
                        indoor_df, outdoor_df, device_data[selected_device][2], selected_pollutant
                    )
                    # Display plots
                    st.plotly_chart(fig_indoor, use_container_width=True)
                    if outdoor_df is not None:
                        st.plotly_chart(fig_outdoor, use_container_width=True)
                    st.markdown("---")
                    st.subheader("Indoor vs Outdoor by Season")
                    for fig in figs_seasonal:
                        st.plotly_chart(fig, use_container_width=True)

                    # Add download buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="Download Indoor Seasonal Data",
                            data=indoor_data.to_csv(),
                            file_name=f"indoor_{selected_pollutant}_seasonal_data.csv",
                            mime="text/csv"
                        )
                    if outdoor_df is not None:
                        with col2:
                            st.download_button(
                                label="Download Outdoor Seasonal Data",
                                data=outdoor_data.to_csv(),
                                file_name=f"outdoor_{selected_pollutant}_seasonal_data.csv",
                                mime="text/csv"
                            )

                else:
                    st.warning("No data found for the selected device.")

            except mysql.connector.Error as e:
                st.error(f"Database error: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
            finally:
                if 'conn' in locals() and conn.is_connected():
                    cursor.close()
                    conn.close()

if __name__ == "__main__":
    main()
