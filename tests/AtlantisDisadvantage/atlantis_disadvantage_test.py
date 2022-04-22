from ...main import run_simulation

run_simulation(input_country_file="inputs/atlantis_disadvantage_countries.xlsx",
               input_resource_file="inputs/atlantis_disadvantage_resources.xlsx",
               output_filename="outputs/atlantis_disadvantage_output_schedule.txt",
               output_count=10)