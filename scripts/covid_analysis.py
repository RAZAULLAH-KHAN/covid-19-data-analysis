import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
from datetime import datetime

# Set style for better visualizations
plt.style.use('default')
sns.set_palette("husl")

def create_covid_visualizations(df, output_dir="outputs/charts"):
    """Create comprehensive COVID-19 analysis visualizations"""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print("Creating COVID-19 visualizations...")
    
    try:
        # Filter to latest date for country-level analysis
        latest_date = df['Date'].max()
        latest_data = df[df['Date'] == latest_date]
        
        # 1. Top 10 Countries by Total Confirmed Cases
        plt.figure(figsize=(14, 8))
        top_countries = latest_data.groupby('Country/Region')['Confirmed'].sum().nlargest(10)
        
        plt.subplot(1, 2, 1)
        sns.barplot(x=top_countries.values, y=top_countries.index)
        plt.title('Top 10 Countries - Total Confirmed Cases', fontsize=14, fontweight='bold')
        plt.xlabel('Confirmed Cases')
        
        # 2. Top 10 Countries by Total Deaths
        plt.subplot(1, 2, 2)
        top_deaths = latest_data.groupby('Country/Region')['Deaths'].sum().nlargest(10)
        sns.barplot(x=top_deaths.values, y=top_deaths.index, palette='Reds')
        plt.title('Top 10 Countries - Total Deaths', fontsize=14, fontweight='bold')
        plt.xlabel('Deaths')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/top_countries_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Created: top_countries_comparison.png")
        
        # 3. Global Cases Over Time
        plt.figure(figsize=(14, 10))
        
        # Aggregate global data by date
        global_daily = df.groupby('Date').agg({
            'Confirmed': 'sum',
            'Deaths': 'sum', 
            'Recovered': 'sum',
            'Active': 'sum'
        }).reset_index()
        
        plt.subplot(2, 2, 1)
        plt.plot(global_daily['Date'], global_daily['Confirmed'], linewidth=2, label='Confirmed')
        plt.title('Global Confirmed Cases Over Time', fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Cases')
        plt.legend()
        plt.xticks(rotation=45)
        
        plt.subplot(2, 2, 2)
        plt.plot(global_daily['Date'], global_daily['Deaths'], color='red', linewidth=2, label='Deaths')
        plt.title('Global Deaths Over Time', fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Deaths')
        plt.legend()
        plt.xticks(rotation=45)
        
        plt.subplot(2, 2, 3)
        plt.plot(global_daily['Date'], global_daily['Recovered'], color='green', linewidth=2, label='Recovered')
        plt.title('Global Recovered Cases Over Time', fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Recovered')
        plt.legend()
        plt.xticks(rotation=45)
        
        plt.subplot(2, 2, 4)
        plt.plot(global_daily['Date'], global_daily['Active'], color='orange', linewidth=2, label='Active')
        plt.title('Global Active Cases Over Time', fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Active Cases')
        plt.legend()
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/global_trends.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Created: global_trends.png")
        
        # 4. Mortality vs Recovery Rates Scatter Plot
        plt.figure(figsize=(12, 8))
        
        # Calculate rates for top 20 countries by confirmed cases
        country_rates = latest_data.groupby('Country/Region').agg({
            'Confirmed': 'sum',
            'Deaths': 'sum',
            'Recovered': 'sum'
        }).nlargest(20, 'Confirmed')
        
        country_rates['Mortality_Rate'] = (country_rates['Deaths'] / country_rates['Confirmed'] * 100).fillna(0)
        country_rates['Recovery_Rate'] = (country_rates['Recovered'] / country_rates['Confirmed'] * 100).fillna(0)
        
        # Create scatter plot
        scatter = plt.scatter(country_rates['Mortality_Rate'], country_rates['Recovery_Rate'], 
                             s=country_rates['Confirmed']/10000, alpha=0.6, 
                             c=country_rates['Confirmed'], cmap='viridis')
        
        # Add country labels for interesting points
        for country in country_rates.index:
            mortality = country_rates.loc[country, 'Mortality_Rate']
            recovery = country_rates.loc[country, 'Recovery_Rate']
            if mortality > 2 or recovery > 80:  # Label outliers
                plt.annotate(country, (mortality, recovery), xytext=(5, 5), 
                            textcoords='offset points', fontsize=8)
        
        plt.colorbar(scatter, label='Total Confirmed Cases')
        plt.xlabel('Mortality Rate (%)')
        plt.ylabel('Recovery Rate (%)')
        plt.title('Mortality Rate vs Recovery Rate by Country', fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/mortality_recovery_scatter.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Created: mortality_recovery_scatter.png")
        
    except Exception as e:
        print(f"Error creating visualizations: {e}")

def generate_covid_insights(df):
    """Generate key insights from COVID-19 data"""
    
    print("\n" + "="*60)
    print("COVID-19 DATA INSIGHTS")
    print("="*60)
    
    try:
        latest_date = df['Date'].max()
        latest_data = df[df['Date'] == latest_date]
        
        # Global totals
        total_confirmed = latest_data['Confirmed'].sum()
        total_deaths = latest_data['Deaths'].sum()
        total_recovered = latest_data['Recovered'].sum()
        total_active = latest_data['Active'].sum()
        
        # Global rates
        global_mortality_rate = (total_deaths / total_confirmed * 100) if total_confirmed > 0 else 0
        global_recovery_rate = (total_recovered / total_confirmed * 100) if total_confirmed > 0 else 0
        
        print(f"Data as of: {latest_date}")
        print(f"Global Totals:")
        print(f"  Confirmed Cases: {total_confirmed:,}")
        print(f"  Total Deaths: {total_deaths:,}")
        print(f"  Total Recovered: {total_recovered:,}")
        print(f"  Active Cases: {total_active:,}")
        print(f"  Global Mortality Rate: {global_mortality_rate:.2f}%")
        print(f"  Global Recovery Rate: {global_recovery_rate:.2f}%")
        
        # Country rankings
        top_5_confirmed = latest_data.groupby('Country/Region')['Confirmed'].sum().nlargest(5)
        top_5_deaths = latest_data.groupby('Country/Region')['Deaths'].sum().nlargest(5)
        
        print(f"Top 5 Countries by Confirmed Cases:")
        for i, (country, cases) in enumerate(top_5_confirmed.items(), 1):
            print(f"  {i}. {country}: {cases:,} cases")
            
        print(f"Top 5 Countries by Deaths:")
        for i, (country, deaths) in enumerate(top_5_deaths.items(), 1):
            mortality_rate = (deaths / top_5_confirmed.get(country, 1) * 100) if top_5_confirmed.get(country, 0) > 0 else 0
            print(f"  {i}. {country}: {deaths:,} deaths ({mortality_rate:.2f}% mortality)")
        
    except Exception as e:
        print(f"Error generating insights: {e}")

if __name__ == "__main__":
    print("Starting COVID-19 Data Analysis")
    
    try:
        # Load combined dataset
        df = pd.read_csv("data/covid19_combined_global.csv")
        df['Date'] = pd.to_datetime(df['Date'])
        
        print("COVID-19 data loaded successfully")
        print(f"Dataset shape: {df.shape}")
        print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
        print(f"Countries: {df['Country/Region'].nunique()}")
        
        # Create visualizations and generate insights
        create_covid_visualizations(df)
        generate_covid_insights(df)
        
        print("COVID-19 analysis completed successfully")
        
    except FileNotFoundError:
        print("Combined data file not found. Please run data_download.py first.")
    except Exception as e:
        print(f"Error in analysis: {e}")