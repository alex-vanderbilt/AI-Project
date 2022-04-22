from main import run_simulation

run_simulation(input_country_file="inputs/atlantis_advantage_countries.xlsx",
               input_resource_file="inputs/atlantis_advantage_resources.xlsx",
               output_filename="outputs/atlantis_advantage_output_schedule.txt",
               output_count=10)