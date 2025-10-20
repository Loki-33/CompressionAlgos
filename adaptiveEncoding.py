'''ADAPTIVE ARITHMETIC ENCODING '''
import string
from typing import List, Tuple
from collections import Counter
import numpy as np 
import gzip 
import bz2 
import lzma
import time 
def read_file(path: str)->str:
    with open(path, 'r') as f:
        text = f.read()
    return text 

def renormalize(low: int, high: int, pending_bits: int, MAX_VALUE: int)->Tuple[int, int, str, int]:
    HALF = 0x80000000 #2^31
    QUARTER = 0x40000000 #2^30
    THREE_QUARTER = 0xC0000000 #3 * 2^30

    output_bits = ''
    while True:
        if high < HALF:
            output_bits += '0' + '1'*pending_bits
            pending_bits=0 
        elif low >= HALF:
            output_bits += '1' + '0' * pending_bits
            pending_bits=0 
            low -= HALF
            high -= HALF
        elif low >= QUARTER and high < THREE_QUARTER:
            pending_bits+=1
            low -= QUARTER
            high -= QUARTER
        else:
            break

        low = (low <<1) & MAX_VALUE
        high = ((high << 1) | 1) & MAX_VALUE
    return low, high, output_bits, pending_bits

def encode(text: str, alphabets: str)->str:
    MAX_VALUE = 0xFFFFFFFF # 2^32 -1 
    low = 0 
    high = MAX_VALUE 

    letter_counter = Counter(alphabets)
    total_count = len(alphabets)
    output_bits=''
    pending_bits=0 
    
    cumulative = {}
    cum_sum = 0 
    for a in alphabets:
        cumulative[a] = cum_sum
        cum_sum += letter_counter[a]

    for ch in text:
        if ch not in cumulative:
            continue 
        cum_low = cumulative[ch]
        cum_high = cum_low + letter_counter[ch]

        range_size = high-low + 1 
        high = low + (range_size * cum_high)// total_count-1 
        low = low + (range_size*cum_low) // total_count
        
        low, high, bits, pending_bits = renormalize(low, high, pending_bits, MAX_VALUE)
        output_bits += bits 

        letter_counter[ch] += 1 
        total_count += 1 

        cum_sum = 0 
        for a in alphabets:
            cumulative[a] = cum_sum 
            cum_sum += letter_counter[a]

        if total_count > 0x3FFF:
            for a in alphabets:
                letter_counter[a] = (letter_counter[a]+1)>>1 
            total_count = sum(letter_counter.values())

    pending_bits += 1 
    if low < 0x40000000:
        output_bits += '0' + '1' * pending_bits
    else:
        output_bits += '1' + '0'*pending_bits

    return output_bits

def decode(compressed_bits: str, alphabets: str, original_length:int)->str:
    MAX_VALUE = 0xFFFFFFFF 
    HALF = 0X80000000 
    QUARTER = 0x40000000  
    THREE_QUARTER = 0xC0000000  

    letter_counter = Counter(alphabets)
    total_count = len(alphabets)

    cumulative={}
    cum_sum=0 
    for a in alphabets:
        cumulative[a] = cum_sum 
        cum_sum += letter_counter[a]
    low=0 
    high=MAX_VALUE
    value=0 

    bit_index=0 
    for i in range(32):
        value = (value << 1)
        if bit_index < len(compressed_bits):
            value |= int(compressed_bits[bit_index])
            bit_index+=1 
    decoded_text=''

    for _ in range(original_length):
        range_size = high-low+1
        scaled_value = ((value - low + 1)*total_count-1)//range_size 
        symbol = None 
        for ch in alphabets:
            cum_low = cumulative[ch]
            cum_high = cum_low + letter_counter[ch]

            if cum_low <= scaled_value< cum_high:
                symbol=ch 
                break 
        if symbol is None:
            break

        decoded_text+= symbol
        cum_low = cumulative[symbol]
        cum_high=cum_low+letter_counter[symbol]

        high = low + (range_size*cum_high)//total_count-1 
        low = low + (range_size*cum_low) // total_count 

        while True: 
            if high<HALF:
                pass 
            elif low >= HALF:
                low -= HALF 
                high -= HALF 
                value -= HALF
            elif low >= QUARTER and high < THREE_QUARTER:
                low -= QUARTER
                high -= QUARTER
                value -= QUARTER
            else:
                break 

            low = (low<<1)&MAX_VALUE
            high = ((high<<1)|1)&MAX_VALUE
            value = (value<<1) & MAX_VALUE

            if bit_index < len(compressed_bits):
                value |= int(compressed_bits[bit_index])
                bit_index+=1 
        letter_counter[symbol]+= 1 
        total_count+= 1 

        cum_sum=0 
        for a in alphabets:
            cumulative[a] = cum_sum
            cum_sum += letter_counter[a]

        if total_count>0x3FFF:
            for a in alphabets:
                letter_counter[a] = (letter_counter[a]+1) >> 1 
            total_count=sum(letter_counter.values())
    return decoded_text 

def bechmark(text: str, alphabets: str):
    print('========================================')
    print('    ADAPTIVE ARITHMETIC ENCODING(MINE)  ')
    print('========================================')
    start = time.time()
    compressed_bits = encode(text, alphabets)
    encode_time = time.time()-start 

    compressed_bytes = len(compressed_bits) // 8*(1 if len(compressed_bits) % 8 else 0)
    ratio = 100 * (1- len(compressed_bits) / (len(text)*8))

    print(f" Compressed: {len(compressed_bits)} bits = {compressed_bytes} bytes")
    print(f" Ratio: {ratio:.2f}%")
    print(f" Time: {encode_time:.4f}s")
    print(f" Bits per char: {len(compressed_bits)/len(text):.2f}\n")

    print('========================================')
    print("          GZIP METHOD                   ")
    print('========================================')

    text_bytes = text.encode('utf-8')
    start = time.time()
    gzip_compressed = gzip.compress(text_bytes, compresslevel=9)
    gzip_time = time.time() - start 

    gzip_ratio = 100 * (1 - len(gzip_compressed)/len(text_bytes))

    print(f" Compressed: {len(gzip_compressed)} bytes")
    print(f" Ratio: {gzip_ratio:.2f}%")
    print(f" Time: {gzip_time:.4f}s")
    print(f" Bits per char: {len(gzip_compressed)*8/len(text):.2f}\n")

    print('========================================')
    print("          BZ2 METHOD                   ")
    print('========================================')
    
    start = time.time() 
    bz2_compressed = bz2.compress(text_bytes, compresslevel=9)
    bz2_time=time.time() - start 

    bz2_ratio = 100 * (1-len(bz2_compressed)/len(text_bytes))

    print(f" Compressed: {len(bz2_compressed)} bytes")
    print(f" Ratio: {bz2_ratio:.2f}%")
    print(f" Time: {bz2_time:.4f}s")
    print(f" Bits per char: {len(bz2_compressed)*8/len(text):.2f}\n")

    print('========================================')
    print("          LZMA METHOD                   ")
    print('========================================')
    
    start = time.time()
    lzma_compressed = lzma.compress(text_bytes, preset=9)
    lzma_time = time.time() - start 

    lzma_ratio = 100 * (1-len(lzma_compressed)/len(text_bytes))

    print(f" Compressed: {len(lzma_compressed)} bytes")
    print(f" Ratio: {lzma_ratio:.2f}%")
    print(f" Time: {lzma_time:.4f}s")
    print(f" Bits per char: {len(lzma_compressed)*8/len(text):.2f}\n")

    print('+++++++++++++END++++++++++++++++++++++++')
if __name__ == '__main__':
    alphabets = string.ascii_lowercase + ',. '
    text= read_file('File/b.txt')
    bechmark(text, alphabets)
