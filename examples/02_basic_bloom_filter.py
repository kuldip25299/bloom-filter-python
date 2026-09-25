"""
Basic Bloom Filter Usage

Demonstrates how a Bloom Filter can reduce unnecessary exact
membership lookups.

A Bloom Filter can say:

* Definitely not present
* Might be present

A positive result must still be checked against the exact dataset.
"""

from bloom_filter.bloom_filter import BloomFilter

def exact_lookup(dataset, item):
"""
Simulate an exact lookup against a source of truth.

```
In a real application, this might be a database query.
"""
return item in dataset
```

def main():
# Simulated source of truth.
dataset = {
"user-1001",
"user-1002",
"user-1003",
"user-1004",
"user-1005",
}

```
# Create a small Bloom Filter for this demonstration.
bloom_filter = BloomFilter(size=100, num_hashes=3)

# Add all known items to the filter.
for item in dataset:
    bloom_filter.add(item)

requests = [
    "user-1003",  # Existing item
    "user-9999",  # Missing item
    "user-1001",  # Existing item
    "user-8888",  # Missing item
]

exact_lookup_count = 0

print("Bloom Filter membership lookup")
print("-" * 35)

for requested_item in requests:
    if not bloom_filter.might_contain(requested_item):
        # A negative result means the item is definitely absent
        # from the set represented by this filter.
        print(f"{requested_item}: definitely not present (exact lookup skipped)")
        continue

    # A positive result is only a possibility, so verify it exactly.
    exact_lookup_count += 1
    exists = exact_lookup(dataset, requested_item)

    if exists:
        print(f"{requested_item}: present (confirmed by exact lookup)")
    else:
        print(f"{requested_item}: false positive (exact lookup says absent)")

print()
print("Total requests:", len(requests))
print("Exact lookups performed:", exact_lookup_count)
print("Exact lookups skipped:", len(requests) - exact_lookup_count)
```

if **name** == "**main**":
main()
