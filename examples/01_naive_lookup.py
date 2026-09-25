"""
Naive Lookup: Checking Membership Without a Bloom Filter

This example demonstrates the straightforward approach to checking
whether an item exists in a dataset.

It is intentionally simple. Later examples will use a Bloom Filter
to reduce unnecessary exact lookups.
"""

def item_exists(dataset, item):
"""
Check whether an item exists in the dataset.

```
This uses a linear scan, so the work grows with the number
of items in the dataset.
"""
for existing_item in dataset:
    if existing_item == item:
        return True

return False
```

def main():
# Imagine this list represents records already stored in a database.
dataset = [
"user-1001",
"user-1002",
"user-1003",
"user-1004",
"user-1005",
]

```
requests = [
    "user-1003",  # Existing item
    "user-9999",  # Missing item
    "user-1001",  # Existing item
    "user-8888",  # Missing item
]

print("Naive membership lookup")
print("-" * 30)

for requested_item in requests:
    exists = item_exists(dataset, requested_item)

    if exists:
        print(f"{requested_item}: found")
    else:
        print(f"{requested_item}: not found")

print()
print("Dataset size:", len(dataset))
print("Number of requests:", len(requests))
```

if **name** == "**main**":
main()
