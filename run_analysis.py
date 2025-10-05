import subprocess
import sys
import os

def run_script(script_name):
    """Run a Python script and handle errors"""
    try:
        print("=" * 50)
        print(f"RUNNING: {script_name}")
        print("=" * 50)
        
        # Check if script exists
        if not os.path.exists(script_name):
            print(f"Script not found: {script_name}")
            return False
            
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"{script_name} completed successfully")
            print(result.stdout)
            return True
        else:
            print(f"Error in {script_name}:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"Failed to run {script_name}: {e}")
        return False

if __name__ == "__main__":
    scripts = [
        "scripts/data_download.py",
        "scripts/covid_analysis.py", 
        "scripts/covid_sql.py",
        
    ]
    
    print("STARTING COVID-19 DATA ANALYSIS PIPELINE")
    print("=" * 60)
    
    success_count = 0
    for script in scripts:
        if run_script(script):
            success_count += 1
    
    print("=" * 60)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Successful: {success_count}/{len(scripts)} scripts")
    
    if success_count == len(scripts):
        print("ALL SCRIPTS COMPLETED SUCCESSFULLY")
        print("Check these folders for outputs:")
        print("  outputs/charts/ - COVID-19 visualizations")
        print("  data/ - SQL database and cleaned data")
        print("  powerbi/ - Power BI ready dataset")
        print("Next: Open Power BI Desktop and load powerbi/covid19_powerbi_ready.csv")
    else:
        print(f"{len(scripts) - success_count} script(s) failed")
        print("Check the errors above and try running failed scripts individually")