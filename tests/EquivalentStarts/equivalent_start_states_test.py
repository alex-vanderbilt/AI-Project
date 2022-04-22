from main import run_simulation

run_simulation(input_country_file="inputs/equivalent_countries.xlsx",
               input_resource_file="inputs/equivalent_resources.xlsx",
               output_filename="outputs/equivalent_starts_output_schedule.txt",
               output_count=10)