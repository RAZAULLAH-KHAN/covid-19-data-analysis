import pandas as pd
from sqlalchemy import create_engine, text

def setup_covid_database():
    """Create SQLite database and tables for COVID-19 data"""
    
    try:
        # Create SQLite engine
        engine = create_engine('sqlite:///data/covid19_database.db')
        
        # Load combined data
        df = pd.read_csv("data/covid19_combined_global.csv")
        
        # Save to SQL database
        df.to_sql('covid19_global', engine, if_exists='replace', index=False)
        
        print("Data successfully loaded into SQL database")
        
        # Example SQL queries for COVID-19 analysis
        with engine.connect() as conn:
            print("EXAMPLE SQL QUERIES:")
            
            # First, check the actual column names
            result = conn.execute(text("PRAGMA table_info(covid19_global)"))
            columns = [row[1] for row in result]
            print("Available columns:", columns)
            
            # Top 10 countries by confirmed cases - FIXED COLUMN NAME
            result = conn.execute(text("""
                SELECT "Country/Region", SUM(Confirmed) as TotalConfirmed
                FROM covid19_global
                WHERE Date = (SELECT MAX(Date) FROM covid19_global)
                GROUP BY "Country/Region"
                ORDER BY TotalConfirmed DESC
                LIMIT 10
            """))
            print("Top 10 Countries by Confirmed Cases:")
            for row in result:
                print(f"  {row[0]}: {row[1]:,} cases")
            
            # Global totals
            result = conn.execute(text("""
                SELECT 
                    SUM(Confirmed) as TotalConfirmed,
                    SUM(Deaths) as TotalDeaths,
                    SUM(Recovered) as TotalRecovered,
                    SUM(Active) as TotalActive
                FROM covid19_global
                WHERE Date = (SELECT MAX(Date) FROM covid19_global)
            """))
            print("Global Totals:")
            for row in result:
                print(f"  Confirmed: {row[0]:,}")
                print(f"  Deaths: {row[1]:,}")
                print(f"  Recovered: {row[2]:,}")
                print(f"  Active: {row[3]:,}")
            
            # Monthly growth trends
            result = conn.execute(text("""
                SELECT 
                    strftime('%Y-%m', Date) as YearMonth,
                    SUM(New_Confirmed) as NewCases,
                    SUM(New_Deaths) as NewDeaths,
                    SUM(New_Recovered) as NewRecovered
                FROM covid19_global
                GROUP BY YearMonth
                ORDER BY YearMonth
                LIMIT 12
            """))
            print("Monthly Growth Trends (Last 12 months):")
            for row in result:
                print(f"  {row[0]}: {row[1]:,} new cases, {row[2]:,} deaths, {row[3]:,} recovered")
                
            # Countries with highest mortality rates
            result = conn.execute(text("""
                SELECT 
                    "Country/Region",
                    SUM(Confirmed) as TotalConfirmed,
                    SUM(Deaths) as TotalDeaths,
                    ROUND((SUM(Deaths) * 100.0 / SUM(Confirmed)), 2) as MortalityRate
                FROM covid19_global
                WHERE Date = (SELECT MAX(Date) FROM covid19_global)
                    AND Confirmed > 1000
                GROUP BY "Country/Region"
                ORDER BY MortalityRate DESC
                LIMIT 5
            """))
            print("Countries with Highest Mortality Rates:")
            for row in result:
                print(f"  {row[0]}: {row[3]}% ({row[2]:,} deaths)")
                
    except Exception as e:
        print(f"Error setting up database: {e}")

if __name__ == "__main__":
    print("Setting up COVID-19 SQL database...")
    setup_covid_database()