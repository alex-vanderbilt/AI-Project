from main import run_simulation

run_simulation(input_country_file="inputs/massive_resource_countries.xlsx",
               input_resource_file="inputs/massive_resource_resources.xlsx",
               output_filename="outputs/massive_resource_output_schedule.txt",
               output_count=10)