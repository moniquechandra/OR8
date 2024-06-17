import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

from attributes.product_details import Parameters
pm = Parameters()
outbound_data = pm.outbound_data

class To_Be:
    as_is_dc = {
    "NY": ['CT', 'DC', 'DE', 'MA', 'MD', 'ME', 'NH', 'NJ', 'NY', 'PA', 'RI', 'VT'],
    "ND": ['MN', 'MT', 'ND', 'SD', 'WY'],
    "IL": ['HI', 'IA', 'IL', 'IN', 'KS', 'KY', 'MI', 'MO', 'NE', 'OH', 'VA', 'WI', 'WV'],
    "TN": ['AL', 'FL', 'GA', 'NC', 'SC', 'TN'],
    "WA": ['AK', 'ID', 'OR', 'WA'],
    "TX": ['AR', 'AZ', 'LA', 'MS', 'NM', 'OK', 'TX'],
    "UT": ['CA', 'CO', 'NV', 'UT']
}

    greedy_dc_allocation = {}
    outbound_data = pm.outbound_data

    for state in outbound_data.index:
        current_dc = outbound_data[list(as_is_dc.keys())]
        best_dc = (current_dc.loc[state]).idxmin()
        if best_dc not in as_is_dc:
            print(best_dc)
        
        if best_dc not in greedy_dc_allocation:
            greedy_dc_allocation[best_dc] = [state]
        elif isinstance(greedy_dc_allocation[best_dc], list):
            greedy_dc_allocation[best_dc].append(state)
        else:
            greedy_dc_allocation[best_dc] = [greedy_dc_allocation[best_dc], state]

    # greedy_dc_allocation should return this: {
    # 'WA': ['AK', 'ID', 'OR', 'WA'], 
    # 'TN': ['AL', 'AR', 'FL', 'GA', 'KS', 'KY', 'MO', 'MS', 'NC', 'OH', 'PA', 'SC', 'TN', 'VA', 'WV'],
    # 'UT': ['AZ', 'CA', 'CO', 'NV', 'UT', 'WY'], 
    # 'NY': ['CT', 'DE', 'HI', 'MA', 'MD', 'ME', 'NH', 'NJ', 'NY', 'RI', 'VT', 'DC'],
    # 'ND': ['IA', 'IN', 'MN', 'MT', 'ND', 'NE', 'SD', 'WI'], 'IL': ['IL', 'MI'], 'TX': ['LA', 'NM', 'OK', 'TX']}
