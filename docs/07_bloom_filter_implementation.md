# Bloom Filter Implementation in Python

We have now covered:

* Why large-scale membership checks can become expensive
* Why a Bloom Filter can reduce unnecessary lookups
* How the bit array works
* How multiple hash functions map values to bit positions
* Why false positives happen
* How memory size and false-positive rate are related

Now we can turn those concepts into a working implementation.

The goal of this implementation is not to build a production framework with unnecessary abstractions.

The goal is to understand exactly what is happening internally.

Our implementation will use only:

* A bit array
* Hash functions
* `add()`
* `might_contain()`

No Redis.

No database.

No external dependencies.

No distributed architecture.

The important part is understanding how a few simple operations can provide a very efficient membership filter.

---

## 1. What Are We Building?

We want an object that behaves conceptually like this:

```text
Bloom Filter

add("apple")
add("banana")
add("orange")

might_contain("apple")
    -> True

might_contain("banana")
    -> True

might_contain("grape")
    -> False
```

But the result has an important meaning.

For a standard Bloom Filter:

```text
False
    ↓
Definitely NOT present

True
    ↓
Might be present
```

It does **not** mean:

```text
True = definitely present
```

The actual source of truth must still be checked when necessary.

---

# 2. Internal Structure

Our Bloom Filter has three important pieces of state:

```text
BloomFilter
│
├── size
│   └── Number of bits
│
├── num_hashes
│   └── Number of hash functions / hash positions
│
└── bit_array
    └── Stores 0/1 membership information
```

For example:

```text
size = 10

bit array:

0 0 0 0 0 0 0 0 0 0
```

Initially, every bit is zero.

When values are inserted, some positions become `1`.

---

# 3. Why Use a Bit Array?

Suppose we have 10 positions:

```text
Index:

0 1 2 3 4 5 6 7 8 9

Bits:

0 0 0 0 0 0 0 0 0 0
```

If a hash function maps a value to position `3`, we set:

```text
0 0 0 1 0 0 0 0 0 0
      ↑
    position 3
```

If another hash function maps the same value to position `7`:

```text
0 0 0 1 0 0 0 1 0 0
              ↑
           position 7
```

The Bloom Filter does not store the original value.

It only stores information about the positions that were activated.

This is the main reason it can be much more memory efficient than storing complete values.

---

# 4. Python Representation

For learning purposes, we can represent the bit array using a Python list:

```python
self.bit_array = [0] * size
```

For example:

```python
size = 10

self.bit_array = [0] * size
```

produces:

```text
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

This representation is intentionally simple.

It makes the algorithm easy to understand.

A production implementation could use a more memory-efficient bit-level representation, but that is a separate optimization.

The algorithm itself does not change.

---

# 5. Hashing a Value

We need to convert an input value into one or more positions in the bit array.

For example:

```text
"apple"
```

could produce:

```text
hash 1 -> 3
hash 2 -> 7
hash 3 -> 1
```

Then the Bloom Filter sets:

```text
positions 3, 7 and 1
```

to `1`.

Conceptually:

```text
"apple"
    │
    ├── hash 1 → 3
    ├── hash 2 → 7
    └── hash 3 → 1
```

The hash positions must always be calculated consistently.

If `"apple"` maps to positions:

```text
3, 7, 1
```

during insertion, the same value must produce:

```text
3, 7, 1
```

during lookup.

Otherwise the Bloom Filter would not work.

---

# 6. Mapping Hash Values to Bit Positions

A hash function may produce a very large integer.

For example:

```text
hash("apple")
=
128736487364873648736487
```

Our bit array may contain only:

```text
10 bits
```

So we need to map the hash result into the valid range:

```text
0 → size - 1
```

We can do this with modulo:

```python
position = hash_value % self.size
```

If:

```text
hash_value = 37
size = 10
```

then:

```text
37 % 10 = 7
```

So the bit position is:

```text
7
```

This guarantees:

```text
0 <= position < size
```

---

# 7. Generating Multiple Hash Positions

A Bloom Filter needs multiple positions for each value.

Instead of implementing several completely independent hash algorithms, we can generate multiple positions from a pair of hash values.

A simple approach is:

```text
hash1
hash2
```

and then derive positions using:

```text
position_i = (hash1 + i × hash2) % size
```

where:

```text
i = 0, 1, 2, ..., k-1
```

This approach is commonly referred to as **double hashing**.

For example:

```text
hash1 = 13
hash2 = 7
size = 10
```

With:

```text
k = 3
```

we get:

```text
i = 0

(13 + 0 × 7) % 10
= 3
```

```text
i = 1

(13 + 1 × 7) % 10
= 0
```

```text
i = 2

(13 + 2 × 7) % 10
= 7
```

So:

```text
"apple"
    ↓
3, 0, 7
```

These become the positions we set.

The detailed reasoning around hash-function choices is covered separately in:

```text
docs/04_hash_functions.md
```

---

# 8. The Add Operation

The first important operation is:

```python
add(value)
```

Its job is simple:

1. Generate hash positions
2. Set those positions to `1`

Conceptually:

```text
add("apple")
```

might produce:

```text
positions:

3
7
1
```

Starting state:

```text
0 0 0 0 0 0 0 0 0 0
```

Set position `3`:

```text
0 0 0 1 0 0 0 0 0 0
```

Set position `7`:

```text
0 0 0 1 0 0 0 1 0 0
```

Set position `1`:

```text
0 1 0 1 0 0 0 1 0 0
```

The Bloom Filter has now recorded the membership information for `"apple"`.

Notice something important:

We never stored:

```text
"apple"
```

inside the Bloom Filter.

We only stored:

```text
1 0 1 1 0 0 0 1 0 0
```

The original value is not recoverable from the bit array.

---

# 9. Adding Another Value

Now insert:

```text
"banana"
```

Suppose its positions are:

```text
2
5
7
```

Current state:

```text
0 1 0 1 0 0 0 1 0 0
```

Set position `2`:

```text
0 1 1 1 0 0 0 1 0 0
```

Set position `5`:

```text
0 1 1 1 0 1 0 1 0 0
```

Position `7` is already `1`.

Nothing needs to change.

Final state:

```text
0 1 1 1 0 1 0 1 0 0
```

This is an important characteristic of Bloom Filters:

Multiple values can share the same bits.

That is expected.

---

# 10. Bit Overlap Is Not a Problem

Consider:

```text
apple → positions 1, 3, 7

banana → positions 2, 5, 7
```

Both values use:

```text
position 7
```

The bit array cannot tell us:

```text
position 7 belongs to apple
```

or:

```text
position 7 belongs to banana
```

It only knows:

```text
position 7 has been activated
```

This loss of individual identity is what makes the structure so memory efficient.

But it also explains why false positives are possible.

---

# 11. The Membership Operation

The second important operation is:

```python
might_contain(value)
```

Its job is to answer:

```text
Could this value have been inserted?
```

The process is:

1. Generate the same hash positions
2. Check every corresponding bit
3. If any bit is `0`, return `False`
4. If all bits are `1`, return `True`

The result should be interpreted as:

```text
False → definitely not present

True → might be present
```

---

# 12. Example: Definitely Not Present

Suppose our current bit array is:

```text
0 1 1 1 0 1 0 1 0 0
```

Now we check:

```text
"grape"
```

Suppose its hash positions are:

```text
2
4
8
```

Check them:

```text
position 2 → 1
position 4 → 0
position 8 → 0
```

At least one required bit is `0`.

Therefore:

```text
"grape"
```

could not have been inserted into this Bloom Filter.

Result:

```python
might_contain("grape")
```

returns:

```text
False
```

This is a guaranteed conclusion.

---

# 13. Why One Zero Bit Is Enough

Suppose a value requires these positions:

```text
2
4
8
```

For the value to have been inserted, all three positions would have been set:

```text
2 → 1
4 → 1
8 → 1
```

If we find:

```text
4 → 0
```

then something is impossible.

The value could not have been inserted because insertion would have set that position to `1`.

Therefore:

```text
Any required bit = 0
        ↓
Definitely not present
```

This is the most important logical property of a standard Bloom Filter.

---

# 14. Example: Might Be Present

Now suppose we check:

```text
"orange"
```

and its positions are:

```text
1
3
7
```

Current bit array:

```text
0 1 1 1 0 1 0 1 0 0
```

Check:

```text
position 1 → 1
position 3 → 1
position 7 → 1
```

All positions contain `1`.

The Bloom Filter returns:

```text
True
```

But it cannot prove that `"orange"` was actually inserted.

The bits might have been set by other values.

Therefore:

```text
True
```

means:

```text
Might be present
```

not:

```text
Definitely present
```

This distinction is fundamental.

---

# 15. Where False Positives Come From

Imagine:

```text
apple → 1, 3, 7
banana → 2, 5, 7
```

The resulting bit array contains:

```text
0 1 1 1 0 1 0 1 0 0
```

Now suppose:

```text
orange → 1, 3, 7
```

Even though `"orange"` was never inserted, all of its required bits are already `1`.

The Bloom Filter therefore returns:

```text
True
```

This is a false positive.

The filter is effectively saying:

```text
"I cannot prove that orange is absent."
```

It is **not** saying:

```text
"Orange definitely exists."
```

This is why the application must use the Bloom Filter correctly.

---

# 16. Complete Data Flow

The entire operation can be represented as:

```text
                  INSERT
                    │
                    ▼
                  value
                    │
                    ▼
             Generate hashes
                    │
                    ▼
             Calculate positions
                    │
                    ▼
             Set bits to 1
                    │
                    ▼
               Bit Array
```

For lookup:

```text
                  LOOKUP
                    │
                    ▼
                  value
                    │
                    ▼
             Generate hashes
                    │
                    ▼
             Calculate positions
                    │
                    ▼
             Check all bits
                    │
             ┌──────┴──────┐
             │             │
         Any bit 0      All bits 1
             │             │
             ▼             ▼
        Definitely       Might be
        not present      present
```

This is the complete Bloom Filter algorithm.

There is no database involved in the core data structure.

There is no network call.

There is no external service.

It is simply:

```text
hash → position → bit
```

---

# 17. A Simple Python Implementation

The implementation can now be written directly from the algorithm.

```python
import hashlib


class BloomFilter:
    def __init__(self, size, num_hashes):
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = [0] * size

    def _get_hashes(self, value):
        value = str(value).encode("utf-8")

        hash1 = int(
            hashlib.sha256(value).hexdigest(),
            16,
        )

        hash2 = int(
            hashlib.md5(value).hexdigest(),
            16,
        )

        for i in range(self.num_hashes):
            yield (hash1 + i * hash2) % self.size

    def add(self, value):
        for position in self._get_hashes(value):
            self.bit_array[position] = 1

    def might_contain(self, value):
        for position in self._get_hashes(value):
            if self.bit_array[position] == 0:
                return False

        return True
```

This implementation is intentionally small.

Every important line maps directly to one of the concepts we discussed.

---

# 18. Understanding the Constructor

The constructor is:

```python
def __init__(self, size, num_hashes):
    self.size = size
    self.num_hashes = num_hashes
    self.bit_array = [0] * size
```

There are two configuration parameters.

### `size`

Number of bits/positions in the logical Bloom Filter.

For example:

```python
size=10000
```

means:

```text
10,000 logical positions
```

### `num_hashes`

Number of hash positions generated for each value.

For example:

```python
num_hashes=5
```

means every inserted value activates five positions.

These two parameters strongly influence:

* Memory usage
* CPU cost
* False-positive rate

The sizing discussion is covered in:

```text
docs/06_memory_and_sizing.md
```

---

# 19. Understanding `_get_hashes()`

The private method:

```python
_get_hashes()
```

generates the positions that belong to a value.

It starts by converting the value into bytes:

```python
value = str(value).encode("utf-8")
```

This gives the hashing functions a consistent byte representation.

Then two hash values are generated:

```python
hash1
hash2
```

These are combined using:

```python
(hash1 + i * hash2) % self.size
```

For example:

```text
hash1 = 100
hash2 = 17
size = 20
```

With:

```text
num_hashes = 4
```

the positions become:

```text
i = 0
(100 + 0 × 17) % 20 = 0

i = 1
(100 + 1 × 17) % 20 = 17

i = 2
(100 + 2 × 17) % 20 = 14

i = 3
(100 + 3 × 17) % 20 = 11
```

So the value maps to:

```text
0, 17, 14, 11
```

---

# 20. Why Use `yield`?

The method uses:

```python
yield
```

instead of creating a list of all positions.

For example:

```python
for position in self._get_hashes(value):
```

generates positions one at a time.

This keeps the implementation simple and avoids creating another temporary collection.

However, this is not a critical optimization for the basic implementation.

The important concept is still:

```text
value → multiple positions
```

---

# 21. Understanding `add()`

The implementation is:

```python
def add(self, value):
    for position in self._get_hashes(value):
        self.bit_array[position] = 1
```

Suppose:

```text
_get_hashes("apple")
```

returns:

```text
3, 7, 9
```

Then:

```python
self.bit_array[3] = 1
self.bit_array[7] = 1
self.bit_array[9] = 1
```

The original value is not stored.

Only the corresponding bits are modified.

---

# 22. Understanding `might_contain()`

The implementation is:

```python
def might_contain(self, value):
    for position in self._get_hashes(value):
        if self.bit_array[position] == 0:
            return False

    return True
```

This follows the Bloom Filter logic exactly.

For each required position:

```text
Is the bit 0?
```

If yes:

```text
Definitely not present.
```

So we immediately return:

```python
False
```

If every bit is `1`:

```python
return True
```

But the meaning remains:

```text
Might be present.
```

---

# 23. Why Can We Return Early?

Consider:

```text
num_hashes = 5
```

Suppose the positions are:

```text
2, 4, 6, 8, 9
```

If we check:

```text
2 → 1
4 → 1
6 → 0
```

we already know the answer.

There is no reason to check:

```text
8
9
```

because one required bit being zero is enough to prove that the value was not inserted.

Therefore:

```python
if self.bit_array[position] == 0:
    return False
```

is both logically correct and efficient.

---

# 24. Why We Do Not Reset Bits

A standard Bloom Filter only performs:

```text
0 → 1
```

operations.

It does not normally perform:

```text
1 → 0
```

when a value is removed.

Why?

Because a single bit may represent multiple values.

For example:

```text
apple → position 7
banana → position 7
```

If we remove `"apple"` and set:

```text
position 7 = 0
```

we would also affect `"banana"`.

The Bloom Filter cannot know which value caused the bit to become `1`.

This is one reason standard Bloom Filters do not support straightforward deletion.

More advanced structures such as Counting Bloom Filters can address deletion, but that is outside the scope of this simple implementation.

---

# 25. Complete Usage Example

A simple application can create the filter like this:

```python
from bloom_filter.bloom_filter import BloomFilter


bloom_filter = BloomFilter(
    size=10000,
    num_hashes=5,
)

bloom_filter.add("apple")
bloom_filter.add("banana")
bloom_filter.add("orange")


print(bloom_filter.might_contain("apple"))
print(bloom_filter.might_contain("banana"))
print(bloom_filter.might_contain("grape"))
```

Possible output:

```text
True
True
False
```

The first two values were inserted.

The third value has at least one required bit that is still zero.

Therefore:

```text
grape → definitely not present
```

---

# 26. Important: `True` Does Not Mean Database-Free

Suppose the Bloom Filter is placed in front of a database.

The application might use:

```python
if not bloom_filter.might_contain(user_id):
    return "not found"

return database_lookup(user_id)
```

This works because:

```text
False
```

means:

```text
Definitely not present
```

But:

```text
True
```

means:

```text
Maybe present
```

Therefore the database lookup is still required.

A more realistic flow is:

```text
Request
   │
   ▼
Bloom Filter
   │
   ├── False ──→ Stop
   │
   └── True
         │
         ▼
   Cache / Database
         │
         ▼
   Exact result
```

This is where Bloom Filters provide their real system-design value.

They are not replacing the source of truth.

They are reducing unnecessary work before reaching it.

---

# 27. Complexity

Let:

```text
k = number of hash positions
```

For insertion:

```text
add(value)
```

we generate `k` positions and set `k` bits.

So the time complexity is approximately:

```text
O(k)
```

For membership checking:

```text
might_contain(value)
```

we inspect up to `k` positions.

So the time complexity is also:

```text
O(k)
```

The bit array requires:

```text
O(m)
```

memory, where:

```text
m = number of bits
```

The important point is that the memory requirement depends primarily on the configured Bloom Filter size, not on storing the full original values.

---

# 28. What This Implementation Does Well

This implementation gives us the fundamental Bloom Filter behavior:

* Very simple data structure
* Fast insertion
* Fast membership checking
* Memory-efficient logical representation
* No external dependencies
* No database dependency
* No network calls
* Controlled false positives
* No false negatives in the standard use case
* Easy to understand and test

It is intentionally small because the goal is to understand the underlying algorithm.

---

# 29. What This Implementation Does Not Solve

This implementation is not intended to be a complete production-ready Bloom Filter library.

It does not currently provide:

* Persistent storage
* Distributed synchronization
* Serialization
* Dynamic resizing
* Deletion
* Counting Bloom Filter support
* Advanced bit-level memory optimization
* Automatic capacity management
* Runtime false-positive monitoring
* Thread/process coordination
* Redis integration
* Database integration

Those are separate engineering concerns.

Adding them immediately would make the core algorithm harder to understand.

The purpose of this repository is to establish the fundamentals first.

---

# 30. Logical Bits vs Python Memory

One important implementation detail should be understood.

We are using:

```python
self.bit_array = [0] * size
```

This is convenient for learning, but a Python list does not store one physical bit per element.

Each Python integer/object and list reference introduces memory overhead.

Therefore:

```text
size = 10,000,000 bits
```

does not mean the Python list will consume exactly:

```text
10,000,000 / 8 bytes
```

of process memory.

The theoretical Bloom Filter memory calculation and the actual memory footprint of a Python implementation are different concepts.

This distinction becomes important when optimizing a real implementation.

For production-level memory efficiency, a packed bit representation can be used.

But the underlying Bloom Filter mathematics remains unchanged.

---

# 31. Why Start With This Simple Version?

There is a temptation to immediately introduce:

```text
Redis
Databases
Distributed Bloom Filters
Serialization
Compression
Kubernetes
Cloud infrastructure
```

But none of these are required to understand the data structure.

The important progression is:

```text
Business problem
       ↓
Why unnecessary lookups are expensive
       ↓
Bloom Filter concept
       ↓
Bit array
       ↓
Hash functions
       ↓
Insertion
       ↓
Membership check
       ↓
False positives
       ↓
Sizing
       ↓
Production integration
```

Once the algorithm is understood, infrastructure decisions become much easier to reason about.

---

# 32. Implementation Mental Model

The easiest way to remember the implementation is:

```text
ADD

value
  ↓
hash
  ↓
positions
  ↓
set bits to 1
```

And:

```text
CHECK

value
  ↓
hash
  ↓
positions
  ↓
check bits
  ↓
┌─────────────────────────────┐
│                             │
│ any bit = 0       all = 1   │
│     ↓                ↓       │
│ definitely         might     │
│ not present        exist     │
└─────────────────────────────┘
```

That is essentially the entire Bloom Filter algorithm.

---

# 33. The Most Important Design Property

The most valuable property is not simply:

```text
"Bloom Filter is fast."
```

The more important property is:

```text
Bloom Filter can cheaply prove absence.
```

That allows the application to avoid expensive operations.

For example:

```text
10 million requests
        ↓
Bloom Filter
        ↓
Remove requests that are definitely absent
        ↓
Only remaining requests reach expensive lookup
```

The performance benefit therefore comes from **work avoided**, not from making the expensive database operation itself faster.

This distinction matters when applying Bloom Filters to real systems.

---

# 34. Current Repository Architecture

At this stage, the repository conceptually looks like:

```text
bloom-filter-python/
│
├── docs/
│   ├── 01_business_problem.md
│   ├── 02_why_bloom_filter.md
│   ├── 03_how_bloom_filter_works.md
│   ├── 04_hash_functions.md
│   ├── 05_false_positives.md
│   ├── 06_memory_and_sizing.md
│   └── 07_bloom_filter_implementation.md
│
└── bloom_filter/
    ├── __init__.py
    └── bloom_filter.py
```

The documentation explains the reasoning.

The implementation contains the actual reusable data structure.

The examples will demonstrate how it behaves.

The tests will verify the important guarantees.

---

# 35. Key Takeaways

The implementation is based on a few simple rules.

### Rule 1 — Store bits, not values

The Bloom Filter does not store the original values.

It stores which bit positions have been activated.

### Rule 2 — Use multiple positions

Each value maps to multiple positions using multiple hash-derived values.

### Rule 3 — Insertion only sets bits

Insertion changes:

```text
0 → 1
```

It does not need to store the original value.

### Rule 4 — One zero proves absence

During lookup:

```text
Any required bit = 0
```

means:

```text
Definitely not present
```

### Rule 5 — All ones only prove possibility

If:

```text
All required bits = 1
```

the value:

```text
Might be present
```

### Rule 6 — False positives are expected

Different values can activate overlapping bits.

Therefore, another value can appear to be present even when it was never inserted.

### Rule 7 — Bloom Filter is not the source of truth

When the filter says:

```text
Might be present
```

the application should perform the exact lookup against the real source of truth when correctness matters.

---

# 36. What We Have Built

We now have a complete mental and implementation model:

```text
                  Bloom Filter
                       │
          ┌────────────┴────────────┐
          │                         │
       INSERT                     CHECK
          │                         │
          ▼                         ▼
       Hash value                Hash value
          │                         │
          ▼                         ▼
    Multiple positions       Multiple positions
          │                         │
          ▼                         ▼
      Set bits                  Check bits
          │                         │
          │                ┌────────┴────────┐
          │                │                 │
          │              Any 0             All 1
          │                │                 │
          │                ▼                 ▼
          │           Definitely          Might be
          │            absent             present
          │
          ▼
      Bit Array
```

This simple structure is enough to build a powerful filtering layer in front of expensive membership checks.

The next step is to use the implementation through realistic examples and verify its behavior, including false positives and sizing choices.

The implementation itself should remain simple.

The system around it is where the larger engineering trade-offs begin.
