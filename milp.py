import pulp
import pandas as pd
from prod_details import product_demand_per_dc, total_operational_costs, shipping_costs_per_dc, total_costs, storage_costs, volume_per_dc, handling_in_costs, handling_out_costs
outbound_data = pd.read_excel("Outbound.xlsx")
outbound_data.index = outbound_data.State
outbound_data = outbound_data.drop(['State', 'Small shipment'], axis=1)

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


# Define the problem
prob = pulp.LpProblem("DistributionNetworkOptimization", pulp.LpMinimize)
dc_locations = ["NY", "ND", "IL", "TX", "KS", "CA", "TN", "PA", "UT", "WA"]
states = [
    "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL",
    "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA",
    "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE",
    "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV",
    "WY"
]

as_is_dc = {
    "NY": ['CT', 'DC', 'DE', 'MA', 'MD', 'ME', 'NH', 'NJ', 'NY', 'PA', 'RI', 'VT'],
    "ND": ['MN', 'MT', 'ND', 'SD', 'WY'],
    "IL": ['HI', 'IA', 'IL', 'IN', 'KS', 'KY', 'MI', 'MO', 'NE', 'OH', 'VA', 'WI', 'WV'],
    "TN": ['AL', 'FL', 'GA', 'NC', 'SC', 'TN'],
    "WA": ['AK', 'ID', 'OR', 'WA'],
    "TX": ['AR', 'AZ', 'LA', 'MS', 'NM', 'OK', 'TX'],
    "UT": ['CA', 'CO', 'NV', 'UT']
}

# product_demand_per_dc()
# Define decision variables
y = pulp.LpVariable.dicts('DC_open', as_is_dc, 0, 1)
z = pulp.LpVariable.dicts("State_served_by_DC", as_is_dc, 0, 1, pulp.LpBinary)


# x = pulp.LpVariable.dicts("Containers_shipped", [(i, j) for i in dc_locations for j in factories], 0, None, pulp.LpInteger)

# d = pulp.LpVariable.dicts("Products_shipped", [(i, k, p) for i in dc_locations for k in states for p in products], 0, None, pulp.LpInteger)

# # # Define the objective function
# prob += (
#     pulp.lpSum([ * y[i] for i in dc_locations]) +
    
#     # Inbound transportation costs from factories to DCs
#     pulp.lpSum([C[i][j] * x[(i, j)] for i in dc_locations for j in factories]) +
    
#     # Inbound handling costs at DCs
#     pulp.lpSum([H[i] * x[(i, j)] for i in dc_locations for j in factories]) +
    
#     # Storage costs at DCs
#     pulp.lpSum([S[i] * y[i] for i in dc_locations]) +
    
#     # Outbound transportation costs from DCs to states
#     pulp.lpSum([T[i][k][p] * d[(i, k, p)] for i in dc_locations for k in states for p in products]) +
    
#     # Non-pallet outbound shipment costs
#     pulp.lpSum([P[k] * W[k] * d[(i, k, p)] for i in dc_locations for k in states for p in products]) +
    
#     # Courier costs for shipments
#     pulp.lpSum([C_courier * T[k] for k in states])
# )
# # Define constraints
# for k in states:
#     for p in products:
#         prob += pulp.lpSum([d[(i, k, p)] for i in dc_locations]) == D[k][p]

# for k in states:
#     prob += pulp.lpSum([z[(i, k)] for i in dc_locations]) == 1

# for i in dc_locations:
#     for k in states:
#         prob += z[(i, k)] <= y[i]

# for i in dc_locations:
#     prob += pulp.lpSum([d[(i, k, p)] for k in states for p in products]) == pulp.lpSum([x[(i, j)] for j in factories])

# # Solve the problem
# prob.solve()

# # Output results
# print(f"Status: {pulp.LpStatus[prob.status]}")
# print("Optimal distribution center locations and state allocations:")
# for i in dc_locations:
#     if y[i].varValue > 0.5:
#         print(f"Distribution Center {i} is open")
#         for k in states:
#             if z[(i, k)].varValue > 0.5:
#                 print(f"  Serves state {k}")
