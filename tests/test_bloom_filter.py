"""
Unit tests for the Bloom Filter implementation.

Run from the repository root:

```
python -m unittest discover -s tests -v
```

"""

import unittest

from bloom_filter import BloomFilter

class TestBloomFilter(unittest.TestCase):
def setUp(self):
self.bloom_filter = BloomFilter(size=1000, num_hashes=5)

```
def test_new_filter_reports_uninserted_items_as_absent(self):
    self.assertFalse(self.bloom_filter.might_contain("user-1001"))
    self.assertFalse(self.bloom_filter.might_contain("missing-item"))

def test_inserted_items_might_be_present(self):
    items = ["user-1001", "user-1002", "user-1003"]

    for item in items:
        self.bloom_filter.add(item)

    for item in items:
        with self.subTest(item=item):
            self.assertTrue(self.bloom_filter.might_contain(item))

def test_adding_same_item_multiple_times_is_safe(self):
    item = "user-1001"

    self.bloom_filter.add(item)
    self.bloom_filter.add(item)
    self.bloom_filter.add(item)

    self.assertTrue(self.bloom_filter.might_contain(item))

def test_adding_one_item_does_not_remove_another(self):
    first_item = "user-1001"
    second_item = "user-1002"

    self.bloom_filter.add(first_item)
    self.bloom_filter.add(second_item)

    self.assertTrue(self.bloom_filter.might_contain(first_item))
    self.assertTrue(self.bloom_filter.might_contain(second_item))

def test_no_false_negatives_for_inserted_items(self):
    items = [f"record-{number}" for number in range(500)]

    for item in items:
        self.bloom_filter.add(item)

    # A standard Bloom Filter must not report an inserted item
    # as definitely absent, assuming the filter has not been
    # corrupted and the same normalization is used.
    for item in items:
        with self.subTest(item=item):
            self.assertTrue(self.bloom_filter.might_contain(item))

def test_bytes_values_can_be_added_and_checked(self):
    item = b"binary-id-123"

    self.bloom_filter.add(item)

    self.assertTrue(self.bloom_filter.might_contain(item))

def test_integer_values_use_string_normalization(self):
    self.bloom_filter.add(12345)

    self.assertTrue(self.bloom_filter.might_contain(12345))
    self.assertTrue(self.bloom_filter.might_contain("12345"))

def test_hash_positions_are_within_bit_array_bounds(self):
    positions = list(self.bloom_filter._get_hashes("user-1001"))

    self.assertEqual(len(positions), self.bloom_filter.num_hashes)

    for position in positions:
        with self.subTest(position=position):
            self.assertGreaterEqual(position, 0)
            self.assertLess(position, self.bloom_filter.size)

def test_hash_positions_are_deterministic(self):
    first_positions = list(self.bloom_filter._get_hashes("stable-id"))
    second_positions = list(self.bloom_filter._get_hashes("stable-id"))

    self.assertEqual(first_positions, second_positions)

def test_invalid_size_is_rejected(self):
    invalid_sizes = [0, -1, 1.5, "100", None, True]

    for size in invalid_sizes:
        with self.subTest(size=size):
            with self.assertRaises(ValueError):
                BloomFilter(size=size, num_hashes=3)

def test_invalid_hash_count_is_rejected(self):
    invalid_hash_counts = [0, -1, 2.5, "3", None, True]

    for num_hashes in invalid_hash_counts:
        with self.subTest(num_hashes=num_hashes):
            with self.assertRaises(ValueError):
                BloomFilter(size=100, num_hashes=num_hashes)
```

if **name** == "**main**":
unittest.main()
