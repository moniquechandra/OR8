import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Determine To-Be situation
outbound_data = pd.read_excel("Outbound.xlsx")
demand_data = pd.read_excel("Demand Forecast.xlsx")
unit_data = pd.read_excel('Product Data per State.xlsx')
handling_out_data = pd.read_excel('Warehousing.xlsx')

outbound_data.index = outbound_data.State
demand_data.index = demand_data.state
outbound_data = outbound_data.drop(['State','Small shipment'], axis=1)

class To_Be:
    dc_allocation = {}
    for state in outbound_data.index:
        best_dc = (outbound_data.loc[state]).idxmin()
        
        if best_dc not in dc_allocation:
            dc_allocation[best_dc] = state
        elif isinstance(dc_allocation[best_dc], list):
            dc_allocation[best_dc].append(state)
        else:
            dc_allocation[best_dc] = [dc_allocation[best_dc], state]
            
    dc_allocation['CA'] = ['CA']
    print(dc_allocation)

    # As-Is situation

    def outbound_costs(dc_allocation):
        dc_product_demand = {}
        for dc in dc_allocation:
            dc_product_demand[dc] = {}  # Create a dictionary for each DC
            for product in ['blender', 'swing', 'chair', 'scooter', 'skiprope']:
                total_demand_per_dc = 0
                for state in dc_allocation[dc]:
                    total_demand_per_dc += (demand_data.loc[state, product])
                dc_product_demand[dc][product] = total_demand_per_dc  # Store demand (in boxes) for each product based on DC

        # Calculate the outbound costs
        shipping_costs = []
        handling_out_costs_per_dc = []
        product_units = unit_data.columns.difference(['state'])
        handling_out_data.index = handling_out_data.DC
        unit_data.index = unit_data.state

        for state in demand_data.index:
            for dc, states in dc_allocation.items():
                if state in states:
                    shipping_costs.append((demand_data['total_weight'][state] * outbound_data.loc[state, dc]))
                    # handling_out_costs.append(demand_data['blender_boxes'] * handling_out_data.loc[dc, ])

        for dc, states in dc_allocation.items():
            out_costs_per_state = 0
            for state in unit_data.index:
                if state in states:
                    for product in product_units:
                        out_costs_per_state += unit_data[product][state] * handling_out_data.loc[dc, product]
                    
            handling_out_costs_per_dc.append(out_costs_per_state)

        shipping_costs = sum(shipping_costs)
        handling_out_costs = sum(handling_out_costs_per_dc)
        opening_costs = len(dc_allocation)*1000000 # Keep a DC open need $1M per year.
        total_outbound_costs = np.round(shipping_costs + handling_out_costs + opening_costs, 1)

        print('Total Shipping Costs (from DC to Customers):', shipping_costs)
        print('Total Handling Out Costs:', handling_out_costs)
        print(f'Total costs for keeping {len(dc_allocation)} DCs open:', opening_costs)
        print('Total Outbound Costs:', total_outbound_costs)

        return total_outbound_costs
    
    outbound_costs(dc_allocation)