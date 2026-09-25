"""
False Positive Demonstration

A Bloom Filter can return a false positive:

* The filter says an item might be present.
* An exact lookup confirms that the item is absent.

This example inserts a small set of values, then searches for an
absent value that produces a false positive.
"""

from bloom_filter.bloom_filter import BloomFilter

def find_false_positive(bloom_filter, existing_items, candidates):
"""
Return the first candidate that is absent from the exact set
but is reported as possibly present by the Bloom Filter.

```
Returns None if no false positive is found among the candidates.
"""
for candidate in candidates:
    if candidate in existing_items:
        continue

    if bloom_filter.might_contain(candidate):
        return candidate

return None
```

def main():
# A deliberately small filter increases the chance of a collision.
bloom_filter = BloomFilter(size=10, num_hashes=3)

```
existing_items = {
    "user-1001",
    "user-1002",
    "user-1003",
}

for item in existing_items:
    bloom_filter.add(item)

# Generate absent values to test.
candidates = [
    f"user-{number}"
    for number in range(2000, 10000)
]

false_positive = find_false_positive(
    bloom_filter=bloom_filter,
    existing_items=existing_items,
    candidates=candidates,
)

print("False positive demonstration")
print("-" * 35)
print("Items inserted:", len(existing_items))
print("Bit array size:", bloom_filter.size)
print("Number of hash functions:", bloom_filter.num_hashes)

if false_positive is None:
    print()
    print("No false positive found in the tested candidates.")
    print("Try increasing the candidate range or changing the filter parameters.")
    return

print()
print("Test candidate:", false_positive)
print("Bloom Filter result:", "might be present")
print("Exact lookup result:", "absent")
print()
print("This is a false positive:")
print("The filter allowed an unnecessary exact lookup,")
print("but it did not incorrectly confirm that the item exists.")
```

if **name** == "**main**":
main()
