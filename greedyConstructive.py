from product_details import Parameters
from to_be import To_Be
pm = Parameters()
tb = To_Be()

def dc_greedy_constructive_search(open_dc=True):
    # If open_dc = True -> Algorithm 1:
    #       Allocate dc based on the distance/costs greedily, allows to opening DC

    # If open_dc = False -> Algorithm 2:
    # (Now, knowing that opening/closing and operating new DC can be costly,
    # we apply the same algorithm without opening a new DC.)
    #       Allocate dc based on the distance/costs greedily, disallows to opening DC

    greedy_dc_allocation = {}
    outbound_data = pm.outbound_data
    for state in outbound_data.index:
        if open_dc:
            best_dc = (outbound_data.loc[state]).idxmin()

            if best_dc not in greedy_dc_allocation:
                greedy_dc_allocation[best_dc] = [state]
            elif isinstance(greedy_dc_allocation[best_dc], list):
                greedy_dc_allocation[best_dc].append(state)
            else:
                greedy_dc_allocation[best_dc] = [greedy_dc_allocation[best_dc], state]

        if not open_dc:
                current_dc = outbound_data[list(tb.as_is_dc.keys())]
                best_dc = (current_dc.loc[state]).idxmin()
                if best_dc not in tb.as_is_dc:
                    print(best_dc)
                
                if best_dc not in greedy_dc_allocation:
                    greedy_dc_allocation[best_dc] = [state]
                elif isinstance(greedy_dc_allocation[best_dc], list):
                    greedy_dc_allocation[best_dc].append(state)
                else:
                    greedy_dc_allocation[best_dc] = [greedy_dc_allocation[best_dc], state]

    return greedy_dc_allocation

all_costs = pm.total_costs(dc_greedy_constructive_search(open_dc=False), tb.as_is_dc)
print('Total Costs:', round(all_costs[0]))
print('Total Inbound Costs:', round(all_costs[1]))
print('Total Warehousing Costs:', round(all_costs[2]))
print('Total Outbound Costs:', round(all_costs[3]))
print('Total Operational Costs:', round(all_costs[4]))
print(dc_greedy_constructive_search(open_dc=False))
