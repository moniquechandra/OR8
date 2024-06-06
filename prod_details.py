def product_demand_per_dc(dc_allocation, demand_data, product_data, unit_in_box=True):
    # Calculate the demand per product and DC in boxes (if unit_in_box = True) and in container (otherwise)
    dc_product_demand = {}
    
    for dc in dc_allocation:
        dc_product_demand[dc] = {}  # Create a dictionary for each DC
        for product in product_data.index:
            total_demand_per_dc = 0
            for state in dc_allocation[dc]:
                box_demand_per_state = demand_data.loc[state, product]
                if unit_in_box:
                    total_demand_per_dc += box_demand_per_state

                elif not unit_in_box:
                    boxes_per_pallet = product_data.loc[product,'BOXES_PER_PALLET']
                    pallets_per_container = product_data.loc[product, 'PALLETS_PER_CONTAINER']
                    total_demand_per_dc += (box_demand_per_state/boxes_per_pallet)/pallets_per_container
            
            dc_product_demand[dc][product] = round(total_demand_per_dc) 

    return dc_product_demand
            
        
def volume_per_dc(dc_product_demand, product_data):
    products = ['blender', 'swing', 'chair', 'scooter', 'skiprope']
    volume_perBox = [0.0070, 0.0045, 0.0098, 0.0200, 0.0055]
    dc_product_volume = {}

    for dc, products_dict in dc_product_demand.items():
        dc_product_volume[dc] = {}
        for i, product in enumerate(products):
            num_boxes = products_dict[product]
            volume = volume_perBox[i]
            dc_product_volume[dc][product] = num_boxes * volume

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

def handling_out_costs(dc_allocation, unit_data, handling_out_data):
    # Calculate the handling out costs (based on storage unit -- boxes or pallets)
    dc_handling_out_costs = 0
    logistic_units = unit_data.columns.difference(['state'])

    for dc, states in dc_allocation.items():
        handling_out_costs_per_state = 0
        for state in unit_data.index:
            if state in states:
                for unit in logistic_units:
                    unit_of_prod_per_dc = unit_data[unit][state]
                    handling_out_costs_per_dc_and_unit = handling_out_data.loc[dc, unit]
                    handling_out_costs_per_state += unit_of_prod_per_dc * handling_out_costs_per_dc_and_unit
                
        dc_handling_out_costs += handling_out_costs_per_state

    return dc_handling_out_costs

def handling_in_costs(dc_product_demand_container, handling_in_data):
    dc_handling_in_costs = 0
    num_containers_per_dc = 0
    for dc, products_dict in dc_product_demand_container.items():
        for product in products_dict.keys():
            num_containers_per_dc += products_dict[product]
            handling_in_costs = handling_in_data.loc[dc, 'handling_in_costs_per_container']

        dc_handling_in_costs += handling_in_costs * num_containers_per_dc
            
    return (dc_handling_in_costs)
def storage_costs(volume_per_dc, warehousing_storageCost):
    # Storage Costs (per cubic meter per month for each state)
    total_storage_costs = {}
    # Calculate the total costs for each state
    for state, items in volume_per_dc.items():
        total_sum = sum(items.values())
        if state in warehousing_storageCost.index:
            cost_per_m3 = warehousing_storageCost.loc[state, 'storage_costs_m3_month']
            total_storage_costs[state] = total_sum * cost_per_m3

    total_warehousing_costs = sum(total_storage_costs.values())
    return total_warehousing_costs

def total_operational_costs(dc_allocation, as_is_dc=False, costs_data=False):
    operating_DC = (1 for value in dc_allocation.values() if value)
    num_operating_DC = sum(operating_DC)
    operating_costs = num_operating_DC*1000000
    opening_costs = 0
    closing_costs = 0

    if as_is_dc:
        set_as_is = set(as_is_dc)
        set_to_be = set(dc_allocation)
        closed_dc = set_as_is - set_to_be
        open_dc = set_to_be - set_as_is
        
        if open_dc:
            for dc in open_dc:
            # state =
                opening_costs += costs_data['opening_price'][dc]*1000000

        if closed_dc:
            for dc in closed_dc:
                closing_costs += costs_data['closing_price'][dc]*1000000

    total_operational_costs = operating_costs + opening_costs + closing_costs

    return total_operational_costs

def warehousing_costs(storage, handling_in, handling_out):
    total_warehousing_costs = storage + handling_in + handling_out
    print('Storage Costs:', storage)
    print('Total Handling In Costs:', handling_in)
    print('Total Handling Out Costs:', handling_out)
    print('Total Warehousing Costs:', total_warehousing_costs)

    return total_warehousing_costs


