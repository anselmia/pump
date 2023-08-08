""" Used to calculate Installation time
- If True, installation duration will be the difference between date and first installation.
- If False, installation duration will be the difference between date and first installation, removing uninstalled period"""
continuous_installation_time = True

""" 
Used to determine the period of valid maintenance time as :
PM date - outdated_period (week) <= PM Date <= PM Date + outdated_period (week)
"""
outdated_period = 8

"""saving directory"""

data_dir = "Data/"
