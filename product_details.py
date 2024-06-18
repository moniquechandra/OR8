import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class Parameters:
    # Dataset
    outbound_data = pd.read_excel("Outbound.xlsx")
    outbound_data.index = outbound_data.State
    outbound_data = outbound_data.drop(['State', 'Small shipment'], axis=1)

    inbound_data = pd.read_excel("Inbound Costs.xlsx")
    gas_emission_data = pd.read_excel("Inbound Costs.xlsx", sheet_name='Gas Emission Inbound')
    inbound_data.index = inbound_data.State
    gas_emission_data.index = gas_emission_data.State
    gas_emission_data = gas_emission_data.drop('State', axis=1)
    
    demand_data = pd.read_excel('Demand Forecast.xlsx')
    demand_data.index = demand_data.state

    unit_data = pd.read_excel('Product Data per State.xlsx')
    oc_data = pd.read_excel('Opening-Closing Costs.xlsx')
    unit_data.index = unit_data.state
    oc_data.index = oc_data.State

    costs_data = pd.read_excel('Opening-Closing Costs.xlsx')
    costs_data.index = costs_data.State

    product_data = pd.read_excel('Product Master Data.xlsx')
    product_data.index = product_data.COMM_NAME

    warehousing_handlingOut_data = pd.read_excel('Warehousing.xlsx', sheet_name='Handling Out')
    warehousing_handlingIn_data = pd.read_excel('Warehousing.xlsx', sheet_name='Handling In')
    warehousing_storageCost = pd.read_excel('Warehousing.xlsx', sheet_name='Storage')

    warehousing_handlingOut_data.index = warehousing_handlingOut_data.DC
    warehousing_handlingIn_data.index = warehousing_handlingIn_data.DC
    warehousing_storageCost.index = warehousing_storageCost.DC

    # Functions
    def product_demand_per_dc(self, dc_allocation, demand_data, product_data, unit_in_box=True):
        """
        Calculates the demand per product and distribution center (DC).

        Parameters:
        - dc_allocation: dict, allocation of states to DCs.
        - demand_data: DataFrame, the demand forecast data.
        - product_data: DataFrame, the product master data.
        - unit_in_box: bool, if True calculates demand in boxes, otherwise in containers.

        Returns:
        - dc_product_demand: dict, demand per product and DC.
        """
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
                        total_demand_per_dc += np.ceil(box_demand_per_state/boxes_per_pallet)/pallets_per_container
                
                dc_product_demand[dc][product] = np.ceil(total_demand_per_dc)

        return dc_product_demand            

    def inbound_costs(self, dc_allocation, dc_product_demand_containers, product_data, inbound_data):
        """
        Calculate the total inbound costs.

        Parameters:
        - dc_product_demand_containers: dict, product demand per DC in containers.

        Returns:
        - inbound_costs: int, calculated inbound costs
        """

        inbound_costs = 0
        for dc in dc_allocation:
            for product in product_data.index:        
                inbound_costs_per_dc = inbound_data.loc[dc, product]
                amount_container_per_product = dc_product_demand_containers[dc][product]
                inbound_costs += inbound_costs_per_dc * amount_container_per_product

        return inbound_costs

        # # Create lists to hold the data
        # states = []
        # products = []
        # containers = []

        # # Extract data from the dictionary
        # for state, products_data in dc_product_demand_containers.items():
        #     for product, container_count in products_data.items():
        #         states.append(state)
        #         products.append(product)
        #         containers.append(container_count)

        # # Create a DataFrame
        # df = pd.DataFrame({'State': states, 'Product': products, 'Containers': containers})

        # # Pivot the DataFrame to get the desired format
        # output_data = df.pivot(index='State', columns='Product', values='Containers')

        # # Export the DataFrame to an Excel file
        # output_file_path = "containers_output.xlsx"  # Specify the complete file path
        # output_data.to_excel(output_file_path)
        # print("Excel file created successfully:", output_file_path)
            

    def volume_per_dc(self, dc_product_demand):
        """
        Calculates the volume required per DC based on product demand.

        Parameters:
        - dc_product_demand: dict, product demand per DC in boxes.

        Returns:
        - volumes_perDC: dict, volume required per DC for each product.
        """
        products = ['blender', 'swing', 'chair', 'scooter', 'skiprope']
        volume_perBox = [0.0070, 0.0045, 0.0098, 0.0200, 0.0055]
        average_stock_level_per_product = [20, 30, 25, 10, 40]

        divided_dict = {}
        for key, nested_dict in dc_product_demand.items():
            divided_dict[key] = {nested_key: np.ceil(nested_value / 365) for nested_key, nested_value in nested_dict.items()}

        volumes_perDC = {}
        averagestockLevelForProductPerState = {}

        for state, products_dict in divided_dict.items():
            averagestockLevelForProductPerState[state] = {}
            for i, product in enumerate(products):
                num_boxes = products_dict[product]
                hashtagdays = average_stock_level_per_product[i]
                averagestockLevelForProductPerState[state][product] = np.ceil(num_boxes * hashtagdays)

        for state, products_dict in averagestockLevelForProductPerState.items():
            volumes_perDC[state] = {}
            for i, product in enumerate(products):
                num_boxes = products_dict[product]
                volume = volume_perBox[i]
                volumes_perDC[state][product] = np.ceil(num_boxes * volume)

        return volumes_perDC

    def outbound_costs(self, dc_allocation, demand_data, outbound_data):
        """
        Calculates the outbound shipping costs.

        Parameters:
        - dc_allocation: dict, allocation of states to DCs.
        - demand_data: DataFrame, the demand forecast data.
        - outbound_data: DataFrame, the outbound cost data.

        Returns:
        - outbound_per_dc: list, calculated outbound costs.
        """
        outbound_per_dc = []
        for state in demand_data.index:
            for dc, states in dc_allocation.items():
                if state in states:
                    weight_large_shipments_per_state = demand_data['total_weight_large_shipments'][state]
                    num_small_shipments_per_state = demand_data['num_small_shipments'][state]
                    
                    tariff_from_dc_to_state = outbound_data.loc[state, dc]
                    outbound_per_dc.append(weight_large_shipments_per_state * tariff_from_dc_to_state + num_small_shipments_per_state * 7)
                                    
        return outbound_per_dc

    def handling_out_costs(self, dc_allocation, unit_data, handling_out_data):
        """
        Calculates the handling out costs based on storage unit (boxes or pallets).

        Parameters:
        - dc_allocation: dict, allocation of states to DCs.
        - unit_data: DataFrame, the unit data per state.
        - handling_out_data: DataFrame, the handling out cost data.

        Returns:
        - total_handling_out_costs: float, total handling out costs.
        """
        total_handling_out_costs = 0
        logistic_units = unit_data.columns.difference(['state'])

        for dc, states in dc_allocation.items():
            dc_handling_out_costs = 0
            for state in unit_data.index:
                if state in states:
                    for unit in logistic_units:
                        unit_of_prod_per_dc = unit_data[unit][state]
                        handling_out_costs_per_dc_and_unit = handling_out_data.loc[dc, unit]
                        dc_handling_out_costs += unit_of_prod_per_dc * handling_out_costs_per_dc_and_unit
                    
            total_handling_out_costs += dc_handling_out_costs

        return total_handling_out_costs
    
    def handling_in_costs(self, dc_product_demand_container, handling_in_data):
        """
        Calculates the handling in costs for each DC.

        Parameters:
        - dc_product_demand_container: dict, product demand per DC in containers.
        - handling_in_data: DataFrame, the handling in cost data.

        Returns:
        - dc_handling_in_costs: float, total handling in costs.
        """
        
        dc_handling_in_costs = 0
        for dc, products_dict in dc_product_demand_container.items():
            num_containers_per_dc = 0
            for product in products_dict.keys():
                num_containers_per_dc += products_dict[product]
                handling_in_costs = handling_in_data.loc[dc, 'handling_in_costs_per_container']

            dc_handling_in_costs += handling_in_costs * num_containers_per_dc
                
        return dc_handling_in_costs
    
    def storage_costs(self, volume_per_dc, warehousing_storageCost):
        """
        Calculates the storage costs per cubic meter per month for each state.

        Parameters:
        - volume_per_dc: dict, volume required per DC for each product.
        - warehousing_storageCost: DataFrame, the storage cost data.

        Returns:
        - total_storage_costs: float, total annual storage costs.
        """
        total_sums = {} # total volume for each state
        total_storage_costs = {} # total costs for each state

        # Calculate the total volume for each state
        for state, items in volume_per_dc.items():
            total_sum = sum(items.values())
            total_sums[state] = total_sum

        # Calculate the total cost for each state
        for state, total_sum in total_sums.items():
            if state in warehousing_storageCost.index:
                cost_per_m3 = warehousing_storageCost.loc[state, 'storage_costs_m3_month']
                total_storage_costs[state] = total_sum * cost_per_m3

        total_storage_costs = sum(total_storage_costs.values())
        return total_storage_costs * 12

    def warehousing_costs(self, storage, handling_in, handling_out):
        """
        Calculates the total warehousing costs.

        Parameters:
        - storage: float, total storage costs.
        - handling_in: float, total handling in costs.
        - handling_out: float, total handling out costs.

        Returns:
        - total_warehousing_costs: float, total warehousing costs.
        """
        total_warehousing_costs = storage + handling_in + handling_out
        return total_warehousing_costs

    def operational_costs(self, dc_allocation, costs_data, as_is_dc=False):
        """
        Calculates the total operational costs including operating, opening, and closing costs.

        Parameters:
        - dc_allocation: dict, allocation of states to DCs.
        - as_is_dc: dict, current state of DC allocation.
        - costs_data: DataFrame, opening and closing cost data.

        Returns:
        - total_operational_costs: float, total operational costs.
        """
        num_operating_DC = sum(1 for values in dc_allocation.values() if values)
        operating_costs = num_operating_DC * 1000000
        opening_costs = 0
        closing_costs = 0

        if as_is_dc:
            non_empty_as_is_dc = {k: v for k, v in as_is_dc.items() if v}
            non_empty_dc_allocation = {k: v for k, v in dc_allocation.items() if v}

            # New keys in dc_allocation that don't exist in as_is_dc (excluding empty dictionaries)
            open_dc = [key for key in non_empty_dc_allocation.keys() if key not in non_empty_as_is_dc]

            # Keys in as_is_dc that don't exist in dc_allocation (excluding empty dictionaries)
            closed_dc = [key for key in non_empty_as_is_dc.keys() if key not in non_empty_dc_allocation]

            if open_dc:
                for dc in open_dc:
                    opening_costs += costs_data['opening_price'][dc] * 1000000

            if closed_dc:
                for dc in closed_dc:
                    closing_costs += costs_data['closing_price'][dc] * 1000000

        total_operational_costs = operating_costs + opening_costs + closing_costs

        return total_operational_costs
    
    def total_storage_costs(self, dc_allocation, as_is_dc=False):
        """
        Calculates the total storage costs including warehousing, outbound, operational, and inbound costs.

        Parameters:
        - dc_allocation: dict, allocation of states to DCs.
        - as_is_dc: dict, current state of DC allocation (optional).

        Returns:
        - total_storage_costs: float, total storage costs.
        """
        inbound = 1124750
        outbound = sum(self.outbound_costs(dc_allocation, self.demand_data, self.outbound_data))
        operational = self.operational_costs(dc_allocation, as_is_dc, self.costs_data)

        dc_product_demand_in_box = self.product_demand_per_dc(dc_allocation, self.demand_data, self.product_data)
        dc_product_demand_in_container = self.product_demand_per_dc(dc_allocation, self.demand_data, self.product_data, False)
        volume_dc = self.volume_per_dc(dc_product_demand_in_box)

        storage = self.storage_costs(volume_dc, self.warehousing_storageCost)
        handling_in = self.handling_in_costs(dc_product_demand_in_container, self.warehousing_handlingIn_data)
        handling_out = self.handling_out_costs(dc_allocation, self.unit_data, self.warehousing_handlingOut_data)
        warehousing = storage + handling_in + handling_out
        
        total_storage_costs = warehousing + outbound + operational + inbound
        # print('Total Costs:', total_storage_costs)
        
        return total_storage_costs
    
    def total_costs(self, dc_allocation, as_is_dc=False):
        """
        Calculates the total costs including warehousing, outbound, operational, and inbound costs.

        Parameters:
        - dc_allocation: dict, allocation of states to DCs.
        - as_is_dc: dict, current state of DC allocation (optional).

        Returns:
        - costs: list, total costs breakdown including total costs, inbound, warehousing, outbound, and operational costs.
        """
        dc_product_demand = self.product_demand_per_dc(dc_allocation, self.demand_data, self.product_data)
        dc_product_demand_container = self.product_demand_per_dc(dc_allocation, self.demand_data, self.product_data, False)
        volume_dc = self.volume_per_dc(dc_product_demand)
        storage = self.storage_costs(volume_dc, self.warehousing_storageCost)
        handling_in = self.handling_in_costs(dc_product_demand_container, self.warehousing_handlingIn_data)
        handling_out = self.handling_out_costs(dc_allocation, self.unit_data, self.warehousing_handlingOut_data)

        outbound = sum(self.outbound_costs(dc_allocation, self.demand_data, self.outbound_data))
        inbound = self.inbound_costs(dc_allocation, dc_product_demand_container, self.product_data, self.inbound_data) # has to be changed later
        warehousing = self.warehousing_costs(storage, handling_in, handling_out)
        operational = self.operational_costs(dc_allocation, self.costs_data, as_is_dc)

        total_costs = outbound + inbound + operational + warehousing
        
        costs = [total_costs, inbound, handling_in, storage, handling_out, outbound, operational]

        return costs

    def total_gas_emission(self, dc_allocation, dc_product_demand_container, gas_emission_data):
                
        total_gas_emission = 0
        for dc, products_dict in dc_product_demand_container.items():
            num_containers_per_dc = 0
            for product in products_dict.keys():
                num_containers_per_dc += products_dict[product]
                gas_emission_container = gas_emission_data.loc[dc, product]

            total_gas_emission += gas_emission_container * num_containers_per_dc

        return total_gas_emission
        