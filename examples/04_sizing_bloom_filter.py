"""
Bloom Filter Sizing Example

Estimate the bit-array size and number of hash functions required
for a target capacity and false-positive probability.

Formula:
m = -(n * ln(p)) / (ln(2) ** 2)
k = (m / n) * ln(2)

Where:
n = expected number of inserted items
p = desired false-positive probability
m = number of bits in the filter
k = number of hash functions

This example only calculates the sizing parameters. It does not
allocate the bit array, which keeps large estimates inexpensive.
"""

import math

def calculate_bloom_filter_size(expected_items, false_positive_rate):
"""
Calculate the recommended bit-array size and hash count.

```
Args:
    expected_items: Expected number of unique inserted items.
    false_positive_rate: Target probability, between 0 and 1.

Returns:
    A tuple of (bit_array_size, number_of_hashes).

Raises:
    ValueError: If the input values are invalid.
"""
if not isinstance(expected_items, int) or isinstance(expected_items, bool):
    raise ValueError("expected_items must be a positive integer")

if expected_items <= 0:
    raise ValueError("expected_items must be greater than zero")

if not isinstance(false_positive_rate, (int, float)):
    raise ValueError("false_positive_rate must be a number")

if not 0 < false_positive_rate < 1:
    raise ValueError("false_positive_rate must be between 0 and 1")

ln2 = math.log(2)

bit_array_size = math.ceil(
    -(expected_items * math.log(false_positive_rate)) / (ln2 ** 2)
)

number_of_hashes = max(
    1,
    round((bit_array_size / expected_items) * ln2),
)

return bit_array_size, number_of_hashes
```

def format_bytes(number_of_bits):
"""
Convert bits to an approximate byte and megabyte estimate.

```
The result represents packed bit storage, not the actual memory
used by a Python list of integers.
"""
number_of_bytes = math.ceil(number_of_bits / 8)
megabytes = number_of_bytes / (1024 * 1024)

return number_of_bytes, megabytes
```

def main():
expected_items = 1_000_000

```
false_positive_targets = [
    0.10,
    0.05,
    0.01,
    0.001,
    0.0001,
]

print("Bloom Filter sizing")
print("=" * 75)
print(f"Expected inserted items: {expected_items:,}")
print()
print(
    f"{'Target FP rate':<18}"
    f"{'Bits':>16}"
    f"{'Hashes':>10}"
    f"{'Approx. memory':>20}"
)
print("-" * 75)

for target_rate in false_positive_targets:
    bits, hashes = calculate_bloom_filter_size(
        expected_items=expected_items,
        false_positive_rate=target_rate,
    )

    memory_bytes, memory_mb = format_bytes(bits)

    print(
        f"{target_rate * 100:>6.3f}%{'':<11}"
        f"{bits:>16,}"
        f"{hashes:>10}"
        f"{memory_mb:>16.2f} MB"
    )

print()
print("Important:")
print("- Lower false-positive targets require more memory.")
print("- The hash count is rounded to a practical whole number.")
print("- Memory shown assumes a packed bit array.")
print("- A Python list of integers uses substantially more memory.")
```

if **name** == "**main**":
main()
