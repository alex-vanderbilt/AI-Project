from main import run_simulation

run_simulation(input_country_file="inputs/minimal_resource_countries.xlsx",
               input_resource_file="inputs/minimal_resource_resources.xlsx",
               output_filename="outputs/minimal_resource_schedule.txt",
               output_count=10)
