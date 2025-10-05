import pandas as pd
import requests
import os
from datetime import datetime

def download_covid_data():
    """Download COVID-19 data from Johns Hopkins University"""
    
    print("Downloading COVID-19 data from Johns Hopkins University...")
    
    # Johns Hopkins COVID-19 data URLs
    base_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"
    
    datasets = {
        'confirmed': 'time_series_covid19_confirmed_global.csv',
        'deaths': 'time_series_covid19_deaths_global.csv', 
        'recovered': 'time_series_covid19_recovered_global.csv'
    }
    
    try:
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        for data_type, filename in datasets.items():
            url = base_url + filename
            print(f"Downloading {data_type} data...")
            
            # Download and save the data
            df = pd.read_csv(url)
            output_path = f'data/covid19_{data_type}_global.csv'
            df.to_csv(output_path, index=False)
            print(f"Saved: {output_path}")
            
        print("All COVID-19 datasets downloaded successfully!")
        return True
        
    except Exception as e:
        print(f"Error downloading data: {e}")
        print("Creating sample dataset instead...")
        return create_sample_dataset()

def create_sample_dataset():
    """Create sample COVID-19 data for testing"""
    print("Creating sample COVID-19 dataset...")
    
    # Create sample data
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    countries = ['US', 'India', 'Brazil', 'UK', 'Germany', 'France', 'Italy', 'Spain', 'Russia', 'China']
    
    sample_data = []
    for date in dates:
        for country in countries:
            confirmed = abs(hash(f"{country}{date}")) % 10000000
            deaths = int(confirmed * 0.02)  # 2% mortality
            recovered = int(confirmed * 0.85)  # 85% recovery
            active = confirmed - deaths - recovered
            
            sample_data.append({
                'Country/Region': country,
                'Date': date,
                'Confirmed': confirmed,
                'Deaths': deaths,
                'Recovered': recovered,
                'Active': active,
                'New_Confirmed': abs(hash(f"new{country}{date}")) % 10000,
                'New_Deaths': abs(hash(f"death{country}{date}")) % 100,
                'New_Recovered': abs(hash(f"recover{country}{date}")) % 5000,
                'Mortality_Rate': 2.0,
                'Recovery_Rate': 85.0,
                'Year': date.year,
                'Month': date.month,
                'DayOfWeek': date.day_name()
            })
    
    df = pd.DataFrame(sample_data)
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Save the dataset
    df.to_csv('data/covid19_combined_global.csv', index=False)
    print("Sample dataset created: data/covid19_combined_global.csv")
    print(f"Records: {len(df)}")
    print(f"Countries: {df['Country/Region'].nunique()}")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    
    return True

def create_combined_dataset():
    """Create combined dataset from downloaded files"""
    try:
        print("Creating combined dataset...")
        
        confirmed = pd.read_csv('data/covid19_confirmed_global.csv')
        deaths = pd.read_csv('data/covid19_deaths_global.csv')
        recovered = pd.read_csv('data/covid19_recovered_global.csv')
        
        print("Loaded datasets successfully")
        
        # Melt datasets to long format
        def melt_dataframe(df, value_name):
            id_vars = ['Province/State', 'Country/Region', 'Lat', 'Long']
            melted_df = df.melt(id_vars=id_vars, var_name='Date', value_name=value_name)
            melted_df['Date'] = pd.to_datetime(melted_df['Date'])
            return melted_df
        
        confirmed_long = melt_dataframe(confirmed, 'Confirmed')
        deaths_long = melt_dataframe(deaths, 'Deaths')
        recovered_long = melt_dataframe(recovered, 'Recovered')
        
        # Merge datasets
        merged_df = confirmed_long.merge(
            deaths_long, on=['Province/State', 'Country/Region', 'Lat', 'Long', 'Date'], how='left'
        ).merge(
            recovered_long, on=['Province/State', 'Country/Region', 'Lat', 'Long', 'Date'], how='left'
        )
        
        # Clean and calculate metrics
        merged_df['Deaths'] = merged_df['Deaths'].fillna(0)
        merged_df['Recovered'] = merged_df['Recovered'].fillna(0)
        merged_df['Active'] = merged_df['Confirmed'] - merged_df['Deaths'] - merged_df['Recovered']
        
        # Calculate daily new cases
        merged_df = merged_df.sort_values(['Country/Region', 'Date'])
        merged_df['New_Confirmed'] = merged_df.groupby('Country/Region')['Confirmed'].diff().fillna(0)
        merged_df['New_Deaths'] = merged_df.groupby('Country/Region')['Deaths'].diff().fillna(0)
        merged_df['New_Recovered'] = merged_df.groupby('Country/Region')['Recovered'].diff().fillna(0)
        
        # Calculate rates
        merged_df['Mortality_Rate'] = (merged_df['Deaths'] / merged_df['Confirmed'] * 100).fillna(0)
        merged_df['Recovery_Rate'] = (merged_df['Recovered'] / merged_df['Confirmed'] * 100).fillna(0)
        
        # Add time features
        merged_df['Year'] = merged_df['Date'].dt.year
        merged_df['Month'] = merged_df['Date'].dt.month
        merged_df['DayOfWeek'] = merged_df['Date'].dt.day_name()
        
        # Save combined dataset
        merged_df.to_csv('data/covid19_combined_global.csv', index=False)
        print("Saved combined dataset: data/covid19_combined_global.csv")
        
        return merged_df
        
    except Exception as e:
        print(f"Error creating combined dataset: {e}")
        return None

if __name__ == "__main__":
    print("Starting COVID-19 Data Processing")
    print("=" * 50)
    
    if download_covid_data():
        combined_data = create_combined_dataset()
        if combined_data is not None:
            print("COVID-19 data processing completed successfully")
            print(f"Total records: {len(combined_data)}")
            print(f"Countries: {combined_data['Country/Region'].nunique()}")
        else:
            print("Failed to create combined dataset")
    else:
        print("Data download failed, but sample data created for testing")