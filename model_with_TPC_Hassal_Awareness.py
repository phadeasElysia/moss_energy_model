import numpy as np
import pynetlogo
import pandas as pd
import random
import scipy.stats as stats

# Initialize PyNetLogo
netlogo = pynetlogo.NetLogoLink(netlogo_home='E:/netlogo/')

# Load the NetLogo model
netlogo.load_model('moss_energy_project.nlogo')

netlogo.command('setup')


# Retrieve agents data


# def break_down(age):
#     scale_parameter = 2
#     shape_parameter = 2
#
#     random_float = random.uniform(0, 1)
#
#     # Calculate the probability density function (PDF) of the Weibull distribution
#     pdf = stats.weibull_min.pdf(age, shape_parameter, scale=scale_parameter)
#
#     # Check if the random number is less than the PDF
#     if random_float < pdf and age >= 14:
#         return True
#     else:
#         return False

oil_price = 1.5
gas_price = 2
electricity_price = 2
hassel_factor = 0.2
subsidy = 0
insulation_cost = 0

def break_down(age):
    if age < 15:
        return False  # Assuming no breakdown probability before 15 years
    elif age > 20:
        return True  # Assuming certain breakdown after 20 years

    # Define probabilities at 15 and 20 years
    prob_at_15 = 0.1  # 10% probability at 15 years
    prob_at_20 = 1.0  # 100% probability at 20 years

    # Calculate the rate of increase per year
    rate_of_increase = (prob_at_20 - prob_at_15) / (20 - 15)

    # Calculate the probability for the given age
    breakdown_probability = prob_at_15 + (age - 15) * rate_of_increase

    # Generate a random number and compare with the breakdown probability
    return random.random() < breakdown_probability


# Press the green button in the gutter to run the script.
def get_available_systems(heating_system_type, heat_pumps_available, heating_budget, gas_prices, oil_prices, ASHP_price,
                          electic_boiler_price, GSHP_price, aware_of_heat_pumps, innovation=False):
    available_list = []
    budget = heating_budget * 10
    if budget >= oil_prices:
        available_list.append("oil")
    if budget >= gas_prices:
        available_list.append('gas')
    if budget >= electic_boiler_price:
        available_list.append('electric')
    if budget >= ASHP_price and heat_pumps_available and innovation and aware_of_heat_pumps:
        available_list.append('ASHP')
    if budget >= GSHP_price and heat_pumps_available and innovation and aware_of_heat_pumps:
        available_list.append('GSHP')
    # if heating_system_type in available_list:
    #     available_list.remove(heating_system_type)
    return available_list


def TCP_calculator(UIC,name):
    DC = random.uniform(500,2000)
    if name == 'oil':
        return UIC + oil_price*3 + DC - subsidy
    elif name == 'gas':
        return UIC + gas_price*3 + DC - subsidy
    elif name == 'electric':
        return UIC + electricity_price*3 + DC - subsidy
    elif name == "GSHP":
        return UIC + electricity_price * 3 + DC + insulation_cost - subsidy
    elif name == "ASHP":
        return UIC + electricity_price * 3 + DC + insulation_cost - subsidy
    else:
        return

def get_available_systems_with_TPC(heating_system_type, heat_pumps_available, heating_budget, gas_prices, oil_prices, ASHP_price,
                          electic_boiler_price, GSHP_price, aware_of_heat_pumps, innovation=False):
    available_list = {}
    budget = heating_budget * 10
    if budget >= oil_prices:
        available_list["oil"] = TCP_calculator(oil_prices,'oil')
    if budget >= gas_prices:
        available_list['gas'] = TCP_calculator(gas_price,'gas')
    if budget >= electic_boiler_price:
        available_list['electric'] = TCP_calculator(electic_boiler_price,'electric')
    if budget >= ASHP_price and heat_pumps_available and innovation and aware_of_heat_pumps:
        available_list['ASHP'] = TCP_calculator(ASHP_price, 'ASHP')
    if budget >= GSHP_price and heat_pumps_available and innovation and aware_of_heat_pumps:
        available_list['GSHP'] = TCP_calculator(GSHP_price, 'GSHP')
    # if heating_system_type in available_list:
    #     available_list.remove(heating_system_type)
    return available_list

def select_heating_system(system_costs, heating_budget, hassle_factors):
    probabilities = {}
    total_probability = 0

    # Calculate probabilities for each system
    for system, TPC in system_costs.items():
        if not(system == "GSHP" or system == "ASHP"):
            hassle_factor = 0
        probability = (1 - hassle_factors) * np.exp(-TPC / heating_budget)
        probabilities[system] = probability
        total_probability += probability

    # Normalize probabilities
    normalized_probabilities = {system: prob / total_probability for system, prob in probabilities.items()}

    # Random selection based on normalized probabilities
    systems, probs = zip(*normalized_probabilities.items())
    selected_system = np.random.choice(systems, p=probs)

    return selected_system

def renovation(i):
    # if i % 12 == 0:
    #     x = random.uniform(0, 10)
    #     if x <= 1:
    #         return True
    # return False
    return random.random() < 1/120


def insulation():
    random_float = random.uniform(0, 1)

    # Check if the random float is less than or equal to 0.18
    return random_float <= 0.18


def updata_heating_system():
    random_float = random.uniform(0, 1)

    # Check if the random float is less than or equal to 0.18
    return random_float <= 0.33


heating_system_type_start = list(netlogo.report("map [s -> [heating-system-type] of s] sort households"))
ashp_start = heating_system_type_start.count("ASHP")
gshp_start = heating_system_type_start.count("GSHP")
oil_start = heating_system_type_start.count('oil')
gas_start = heating_system_type_start.count('gas')
electric_start = heating_system_type_start.count('electric')
if __name__ == '__main__':
    results = []
    ban_announced = False
    for i in range(1, 100):
        if i == 36:
            ban_announced = True
        gas_boiler_prices = netlogo.report('gas-boiler-price')
        oil_boiler_prices = netlogo.report('oil-boiler-price')
        electic_boiler_price = netlogo.report("electric-boiler-price")
        ASHP_price = netlogo.report('ASHP')
        GSHP_price = netlogo.report('GSHP')
        who = netlogo.report("map [s -> [who] of s] sort households")
        heating_system_type = netlogo.report("map [s -> [heating-system-type] of s] sort households")
        heating_system_age = netlogo.report("map [s -> [heating-system-age] of s] sort households")
        heating_budget = netlogo.report("map [s -> [heating-budget] of s] sort households")
        heat_pumps_available = netlogo.report("map [s -> [heat-pumpsuitability] of s] sort households")
        color = netlogo.report("map [s -> [color] of s] sort households")
        awareness_of_heat_pumps = netlogo.report("map [s -> [aware-of-heat-pumps] of s] sort households")
        data = {
            'who': who,
            'heating-system-type': heating_system_type,
            'heating-system-age': heating_system_age,
            'heating-budget': heating_budget,
            'heat-pumpsuitability': heat_pumps_available,
            'awareness-of-heat-pumps': awareness_of_heat_pumps,
            'color': color
        }
        df = pd.DataFrame(data)
        for index, row in df.iterrows():
            df.at[index, 'heating-system-age'] += 1 / 12
            heating_system_type = df.loc[index, 'heating-system-type']
            heating_budget = df.loc[index, 'heating-budget']
            heating_system_age = df.loc[index, 'heating-system-age']
            heat_pumps_available = df.loc[index, 'heat-pumpsuitability']
            awareness_of_heat_pumps = df.loc[index, 'awareness-of-heat-pumps']
            if ban_announced:
                awareness_of_heat_pumps = True

            if break_down(heating_system_age):
                available_systems = get_available_systems_with_TPC(heating_system_type, heat_pumps_available, heating_budget,
                                                          gas_boiler_prices, oil_boiler_prices, ASHP_price, electic_boiler_price,
                                                          GSHP_price,awareness_of_heat_pumps)
                if available_systems:
                    df.at[index, 'heating-system-type'] = select_heating_system(available_systems,heating_budget,hassel_factor)
                    df.at[index, 'heating-system-age'] = 0
            elif renovation(i):
                if insulation():
                    df.at[index, 'heat-pumpsuitability'] = True
                if updata_heating_system():
                    available_systems = get_available_systems_with_TPC(heating_system_type, heat_pumps_available, heating_budget,
                                                              gas_boiler_prices, oil_boiler_prices, ASHP_price, electic_boiler_price,
                                                              GSHP_price,awareness_of_heat_pumps, innovation=True)
                    if available_systems:
                        df.at[index, 'heating-system-type'] = select_heating_system(available_systems,heating_budget,hassel_factor)
                        df.at[index, 'heating-system-age'] = 0
            if df.loc[index, 'heating-system-type'] in ['ASHP', 'GSHP']:
                df.at[index, 'color'] = 128

        netlogo.write_NetLogo_attriblist(
            df[["who", "heating-system-type", "heating-system-age", "heating-budget", "heat-pumpsuitability", "color"]],
            "household")
        heating_system_type_in_process = list(netlogo.report("map [s -> [heating-system-type] of s] sort households"))
        ashp_end = heating_system_type_in_process.count("ASHP")
        gshp_end = heating_system_type_in_process.count("GSHP")
        oil_end = heating_system_type_in_process.count('oil')
        gas_end = heating_system_type_in_process.count('gas')
        electric_end = heating_system_type_in_process.count('electric')
        hp_end = ashp_end + gshp_end
        results.append([oil_end, gas_end, electric_end, hp_end])
        print(
            'iteratuions' + str(i) + '\noil' + str(oil_end) + '\nelectric' + str(electric_end) + '\ngas' + str(gas_end)
            + '\nheat-pums' + str(hp_end))
    columns = ['oil', 'gas', 'electric', 'hp']

    results_df = pd.DataFrame(results, columns=columns)

heating_system_type_end = list(netlogo.report("map [s -> [heating-system-type] of s] sort households"))
ashp_end = heating_system_type_end.count("ASHP")
gshp_end = heating_system_type_end.count("GSHP")
oil_end = heating_system_type_end.count('oil')
gas_end = heating_system_type_end.count('gas')
electric_end = heating_system_type_end.count('electric')
hp_start = ashp_start + gshp_start
hp_end = ashp_end + gshp_end

print('oil' + str(oil_start) + '\nelectric' + str(electric_start) + '\ngas' + str(gas_start)
      + '\heat-pums' + str(hp_start))
print('oil' + str(oil_end) + '\nelectric' + str(electric_end) + '\ngas' + str(gas_end)
      + '\heat-pums' + str(hp_end))
netlogo.kill_workspace()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
