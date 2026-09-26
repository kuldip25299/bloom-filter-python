"""
Realistic Bloom Filter Usage

Scenario:
A service receives many requests asking whether user IDs exist.
The exact source of truth is represented by a Python set here.
A Bloom Filter is used as a fast pre-check to skip exact lookups
for IDs that are definitely absent.

Important:

* A Bloom Filter negative result can safely skip the exact lookup
  only when the filter accurately represents the relevant dataset.
* A positive result is not proof of existence and must be verified.
* This example simulates a static dataset. It does not implement
  database synchronization or concurrent updates.
  """

from bloom_filter.bloom_filter import BloomFilter

def build_filter(dataset, expected_items, false_positive_rate):
"""
Build a Bloom Filter sized for the expected dataset.

```
The filter implementation takes a bit count and hash count,
so calculate those values using the standard formulas.
"""
import math

if expected_items <= 0:
    raise ValueError("expected_items must be greater than zero")

if not 0 < false_positive_rate < 1:
    raise ValueError("false_positive_rate must be between 0 and 1")

ln2 = math.log(2)

bit_count = math.ceil(
    -(expected_items * math.log(false_positive_rate)) / (ln2 ** 2)
)

hash_count = max(
    1,
    round((bit_count / expected_items) * ln2),
)

bloom_filter = BloomFilter(
    size=bit_count,
    num_hashes=hash_count,
)

for item in dataset:
    bloom_filter.add(item)

return bloom_filter
```

def check_membership(item, bloom_filter, source_of_truth, stats):
"""
Check membership using the Bloom Filter and exact source.

```
Returns:
    True if the item exists, otherwise False.
"""
stats["requests"] += 1

if not bloom_filter.might_contain(item):
    stats["filter_negatives"] += 1
    stats["exact_lookups_skipped"] += 1
    return False

stats["filter_maybes"] += 1
stats["exact_lookups_performed"] += 1

exists = item in source_of_truth

if not exists:
    stats["false_positives"] += 1

return exists
```

def main():
# Simulated source of truth: in a real service this could be a DB.
user_ids = {
f"user-{number:06d}"
for number in range(1, 1001)
}

```
# Configure the filter for the expected number of records.
bloom_filter = build_filter(
    dataset=user_ids,
    expected_items=1_000,
    false_positive_rate=0.01,
)

incoming_requests = [
    "user-000001",
    "user-000250",
    "user-000999",
    "user-900001",
    "user-900002",
    "user-900003",
    "user-000500",
    "user-700000",
]

stats = {
    "requests": 0,
    "filter_negatives": 0,
    "filter_maybes": 0,
    "exact_lookups_performed": 0,
    "exact_lookups_skipped": 0,
    "false_positives": 0,
}

print("Realistic Bloom Filter membership checks")
print("=" * 48)
print(f"Records represented: {len(user_ids):,}")
print(f"Incoming requests: {len(incoming_requests):,}")
print()

for user_id in incoming_requests:
    exists = check_membership(
        item=user_id,
        bloom_filter=bloom_filter,
        source_of_truth=user_ids,
        stats=stats,
    )

    status = "exists" if exists else "does not exist"
    print(f"{user_id}: {status}")

print()
print("Summary")
print("-" * 48)
print(f"Requests processed:          {stats['requests']}")
print(f"Filter said definitely absent: {stats['filter_negatives']}")
print(f"Filter said maybe present:     {stats['filter_maybes']}")
print(f"Exact lookups performed:       {stats['exact_lookups_performed']}")
print(f"Exact lookups skipped:         {stats['exact_lookups_skipped']}")
print(f"False positives observed:      {stats['false_positives']}")

if stats["requests"]:
    avoided_percent = (
        stats["exact_lookups_skipped"] / stats["requests"]
    ) * 100

    print(f"Exact lookups avoided:         {avoided_percent:.1f}%")

print()
print(
    "The lookup savings depend on the request mix, filter sizing, "
    "and how accurately the filter reflects the source dataset."
)
```

if **name** == "**main**":
main()
