def product_demand_per_dc(dc_allocation, demand_data, product_data, unit_in_box=True):
    # Calculate the demand per product and DC in boxes (if unit_in_box = True) and in container (otherwise)
    dc_product_demand = {}
    
    for dc in dc_allocation:
        dc_product_demand[dc] = {}  # Create a dictionary for each DC
        for product in ['blender', 'swing', 'chair', 'scooter', 'skiprope']:
            total_demand_per_dc = 0
            for state in dc_allocation[dc]:
                box_demand_per_state = demand_data.loc[state, product]
                if unit_in_box:
                    product_data = True
                    total_demand_per_dc += box_demand_per_state

                elif not unit_in_box:
                    boxes_per_pallet = product_data.loc[product,'BOXES_PER_PALLET']
                    pallets_per_container = product_data.loc[product, 'PALLETS_PER_CONTAINER']
                    total_demand_per_dc += (box_demand_per_state/boxes_per_pallet)/pallets_per_container
            
            dc_product_demand[dc][product] = round(total_demand_per_dc) 

    return dc_product_demand
            
        
def volume_per_dc(dc_allocation, dc_product_demand, demand_data, product_data):
    products = ['blender', 'swing', 'chair', 'scooter', 'skiprope']
    volume_perBox = [0.0070, 0.0045, 0.0098, 0.0200, 0.0055]
    dc_product_demand = product_demand_per_dc(dc_allocation, demand_data)

    dc_product_volume = {}

    for state, products_dict in dc_product_demand.items():
        dc_product_volume[state] = {}
        for i, product in enumerate(products):
            num_boxes = products_dict[product]
            volume = volume_perBox[i]
            dc_product_volume[state][product] = num_boxes * volume

    return dc_product_volume

def shipping_costs_per_dc(dc_allocation, demand_data, outbound_data):
    shipping_costs = []
    for state in demand_data.index:
        for dc, states in dc_allocation.items():
            if state in states:
                weight_large_shipments_per_state = demand_data['total_weight_large_shipments'][state]
                weight_small_shipments_per_state = demand_data['total_weight_small_shipments'][state]
                
                tariff_from_dc_to_state = outbound_data.loc[state, dc]

                shipping_costs.append(weight_large_shipments_per_state * tariff_from_dc_to_state + weight_small_shipments_per_state * 7)

    return shipping_costs

def handling_out_costs_per_dc(dc_allocation, unit_data, handling_out_data):
    # Calculate the handling out costs (based on storage unit -- boxes or pallets)
    dc_handling_out_costs = []
    
    logistic_units = unit_data.columns.difference(['state'])

    for dc, states in dc_allocation.items():
        handling_out_costs_per_state = 0
        for state in unit_data.index:
            if state in states:
                for unit in logistic_units:
                    unit_of_prod_per_dc = unit_data[unit][state]
                    handling_out_costs_per_dc_and_unit = handling_out_data.loc[dc, unit]
                    handling_out_costs_per_state += unit_of_prod_per_dc * handling_out_costs_per_dc_and_unit
                
        dc_handling_out_costs.append(handling_out_costs_per_state)

    return dc_handling_out_costs

def total_operational_costs(dc_allocation, as_is_dc=False):
    # oc_costs_per_dc = oc_costs.loc['']
    operating_DC = (1 for value in dc_allocation.values() if value)
    num_operating_DC = sum(operating_DC)
    operating_costs = num_operating_DC*1000000

    if as_is_dc:
        num_as_is_DC = len(as_is_dc)

    # for dc, state in dc_allocation.items():
        
    # if num_operating_DC > num_as_is_DC:
    #     opening_costs = 

    # if num_operating_DC < num_as_is_DC:
    #     closing_costs = 

    return operating_costs




def storage_costs(volume_per_dc, warehousing_storageCost):
    total_storage_costs = {}
    # Calculate the total costs for each state
    for state, items in volume_per_dc.items():
        total_sum = sum(items.values())
        if state in warehousing_storageCost.index:
            cost_per_m3 = warehousing_storageCost.loc[state, 'storage_costs_m3_month']
            total_storage_costs[state] = total_sum * cost_per_m3

    total_warehousing_costs = sum(total_storage_costs.values())
    return total_warehousing_costs