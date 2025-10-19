#arithmetic coding 
import numpy as np 
from typing import List, Tuple 

probs_dict ={'A':0.5, 'B':0.3, 'C':0.2}
text = "BAC"

#encoding  part 

interval =[0.0, 1.0] 
cum_probs = np.cumsum(list(probs_dict.values()))

def split_interval(interval: List[float], probs: List[float])->List:
    a = interval[0]
    b = interval[1]
    probs = np.array(probs, dtype=np.float32)
    boundaries = np.concatenate(([a], a+np.cumsum(probs) * (b-a)))
    return list(zip(boundaries[:-1], boundaries[1:]))

splity= split_interval(interval, list(probs_dict.values()))
interval_dict = {}

for i,j in zip(splity, 'ABC'):
    interval_dict[j] = i

def new_interval(low, high, cum_prob, cum_prob2):
    new_low = low + (high - low) * cum_prob
    new_high = low + (high-low) * cum_prob2
    return new_low, new_high

for ch in text:
    symbols = list(probs_dict.keys())
    prev_cum = 0 if symbols.index(ch) == 0 else cum_probs[symbols.index(ch)-1]
    curr_cum = cum_probs[symbols.index(ch)]

    low, high = interval
    interval = new_interval(low, high, prev_cum, curr_cum)

encoded_value = np.random.uniform(interval[0], interval[1])
print(interval)
print(f"Encoded Value: {encoded_value}")


#decoding part 
def rescale(v, low, high):
    return (v-low)/(high-low)

decoded_text = ''

def find_index(v):
    for i, (a,b) in enumerate(splity):
        if a <= v < b:
            return i 

V = encoded_value
for i in range(3):
    id = find_index(V)
    text = symbols[id]
    low, high = interval_dict[text]
    decoded_text += text
    V = rescale(V, low, high)
print('Decoded Text:', decoded_text) 
