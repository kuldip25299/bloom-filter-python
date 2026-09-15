# Bloom Filter in Python

A practical, from-scratch implementation of a **Bloom Filter** in Python, explained from the business problem all the way to real-world usage and production considerations.

The goal of this repository is not just to implement a Bloom Filter, but to understand **why it exists, what problem it solves, how it works internally, what trade-offs it introduces, and when it should or should not be used.**

---

## Why This Repository?

Many applications repeatedly need to answer a simple question:

> **"Have we seen this value before?"**

Examples include:

* Has this URL already been processed?
* Does this username probably exist?
* Have we already processed this transaction ID?
* Could this product ID exist?
* Have we already crawled this page?
* Could this key exist in our database?

The obvious solution is to query a database or maintain a large in-memory set.

That works well at small scale.

But when the number of checks becomes very large, repeatedly querying an external data source can become expensive.

A **Bloom Filter** provides a lightweight way to eliminate values that are **definitely not present**, before performing an expensive lookup.

```text
Incoming Value
      |
      v
+----------------+
|  Bloom Filter  |
+----------------+
      |
      +------------------+
      |                  |
  Definitely NOT       MAYBE
      |                  |
      v                  v
   Skip lookup       Check DB/Cache
```

The important idea is:

> **A Bloom Filter does not replace the database. It can reduce unnecessary database lookups.**

---

# What Is a Bloom Filter?

A Bloom Filter is a **space-efficient probabilistic data structure** used to test whether an element is a member of a set.

It provides two possible answers:

```text
Definitely NOT present
Probably present
```

It can produce **false positives**, but a correctly implemented standard Bloom Filter does not produce false negatives.

For example:

```text
Bloom Filter:

"apple"  -> probably present
"banana" -> probably present
"orange" -> probably present
"grape"  -> definitely NOT present
```

A result of:

```text
probably present
```

does not guarantee that the item actually exists.

The application may need to perform a second check against the real data source.

---

# Core Idea

Suppose we have a database containing:

```text
apple
banana
orange
mango
```

Without a Bloom Filter:

```text
Request
   |
   v
Database
   |
   v
Does item exist?
```

Every request requires a database lookup.

With a Bloom Filter:

```text
Request
   |
   v
Bloom Filter
   |
   +-----------------------+
   |                       |
Definitely NOT           MAYBE
   |                       |
   v                       v
Skip database          Query database
```

If the Bloom Filter says:

```text
Definitely NOT
```

we know the value was not inserted into the filter.

Therefore, we don't need to query the database.

If it says:

```text
MAYBE
```

we perform the actual lookup.

---

# How Does It Work?

A Bloom Filter mainly consists of two things:

1. A **bit array**
2. Multiple **hash functions**

Conceptually:

```text
                 "kuldip"
                    |
          +---------+---------+
          |         |         |
        hash1     hash2     hash3
          |         |         |
          v         v         v
         bit 2     bit 7     bit 11
          |         |         |
          +---------+---------+
                    |
                    v
             Set bits to 1
```

The underlying bit array might look like:

```text
Index:

0 1 2 3 4 5 6 7 8 9 10 11
0 0 1 0 0 0 0 1 0 0  0  1
```

When an item is added, the hash functions determine which positions should be set to `1`.

When checking an item, the same hash functions determine the positions to inspect.

---

# Example

Suppose we add:

```text
apple
```

Three hash functions might produce:

```text
hash1("apple") -> 2
hash2("apple") -> 7
hash3("apple") -> 11
```

The corresponding bits become:

```text
0 0 1 0 0 0 0 1 0 0 0 1
    ^           ^       ^
    2           7      11
```

Now check:

```text
apple
```

The same positions are:

```text
2 -> 1
7 -> 1
11 -> 1
```

Therefore:

```text
apple -> probably present
```

Now suppose we check:

```text
grape
```

and its hashes produce:

```text
2 -> 1
5 -> 0
9 -> 0
```

Because at least one required bit is `0`, we know:

```text
grape -> definitely NOT present
```

This is the fundamental property of a Bloom Filter.

---

# False Positives

False positives are one of the most important concepts in understanding Bloom Filters.

Suppose we insert:

```text
apple
banana
orange
```

After several insertions, many bits in the bit array become `1`.

Now we check:

```text
grape
```

It is possible that all of `grape`'s hash positions happen to already contain `1`s because other values set those bits.

The Bloom Filter therefore returns:

```text
grape -> probably present
```

even though `grape` was never inserted.

That is a **false positive**.

---

# False Positive vs False Negative

A standard Bloom Filter has an important guarantee.

| Result                 | Meaning                         |
| ---------------------- | ------------------------------- |
| Definitely NOT present | The item was not inserted       |
| Probably present       | The item may have been inserted |
| False positive         | Possible                        |
| False negative         | Not possible                    |

This makes Bloom Filters useful as a **filter in front of another source of truth**.

For example:

```text
                 Request
                    |
                    v
             +-------------+
             | Bloom Filter|
             +-------------+
                    |
          +---------+---------+
          |                   |
       NOT FOUND            MAYBE
          |                   |
          v                   v
      Stop here          Database lookup
                              |
                              v
                         Final answer
```

---

# Why Not Just Use a Set?

A normal Python `set` can answer membership queries exactly:

```python
if value in my_set:
    ...
```

But a set stores the actual values.

For a very large number of items, the memory requirements can become significant.

A Bloom Filter stores only bits representing the membership information.

This creates an important trade-off:

```text
Hash Set

Exact membership
        +
More memory


Bloom Filter

Probabilistic membership
        +
Much lower memory
```

Bloom Filters are useful when:

> **A small amount of uncertainty is acceptable in exchange for significant memory and lookup efficiency.**

---

# Repository Structure

```text
bloom-filter-python/
│
├── README.md
│
├── docs/
│   ├── 01_business_problem.md
│   ├── 02_why_bloom_filter.md
│   ├── 03_how_bloom_filter_works.md
│   ├── 04_hash_functions.md
│   ├── 05_false_positives.md
│   ├── 06_memory_and_sizing.md
│   ├── 07_bloom_filter_implementation.md
│   ├── 08_real_world_use_cases.md
│   ├── 09_bloom_filter_vs_alternatives.md
│   └── 10_production_considerations.md
│
├── examples/
│   ├── 01_naive_lookup.py
│   ├── 02_basic_bloom_filter.py
│   ├── 03_false_positive.py
│   ├── 04_sizing_bloom_filter.py
│   └── 05_realistic_usage.py
│
├── bloom_filter/
│   ├── __init__.py
│   └── bloom_filter.py
│
├── tests/
│   └── test_bloom_filter.py
│
├── requirements.txt
│
└── LICENSE
```

The repository intentionally keeps the implementation small.

There is no unnecessary:

* Redis dependency
* Database dependency
* Message queue
* Microservice architecture
* Container orchestration
* External framework
* Complex abstraction layer

The core Bloom Filter is implemented directly in Python so the underlying mechanism remains easy to understand.

---

# Learning Path

The repository follows a problem-first approach.

```text
Business Problem
       |
       v
Why Normal Lookup Becomes Expensive
       |
       v
What Is a Bloom Filter?
       |
       v
Bit Array + Hash Functions
       |
       v
False Positives
       |
       v
Memory & Sizing
       |
       v
Python Implementation
       |
       v
Real-World Use Cases
       |
       v
Bloom Filter vs Alternatives
       |
       v
Production Considerations
```

Each stage builds on the previous one.

---

# Documentation

## 1. Business Problem

`docs/01_business_problem.md`

Introduces the real-world membership-check problem and explains why repeatedly checking an external data source can become expensive.

---

## 2. Why Bloom Filter?

`docs/02_why_bloom_filter.md`

Explains how a Bloom Filter can act as a lightweight first-level filter before an expensive database, cache, or external lookup.

---

## 3. How Bloom Filter Works

`docs/03_how_bloom_filter_works.md`

Explains:

* Bit arrays
* Hash functions
* Insert operations
* Membership checks
* Bit positions
* Why multiple hashes are required

---

## 4. Hash Functions

`docs/04_hash_functions.md`

Explains:

* What hashing means
* Why Bloom Filters use multiple hash positions
* Hash collisions
* Hash distribution
* Number of hash functions

The goal is to understand the mechanism without introducing unnecessary hashing complexity.

---

## 5. False Positives

`docs/05_false_positives.md`

Explains the most important limitation of Bloom Filters:

```text
False positives are possible.
False negatives are not.
```

The example code demonstrates this behavior instead of only explaining it theoretically.

---

## 6. Memory and Sizing

`docs/06_memory_and_sizing.md`

Explains how to choose:

* Expected number of elements
* Desired false-positive probability
* Bit-array size
* Number of hash functions

The standard Bloom Filter equations are introduced here.

For expected elements `n` and desired false-positive probability `p`:

```text
m = -(n × ln(p)) / (ln(2)²)
```

Where:

```text
m = number of bits
n = expected number of elements
p = desired false-positive probability
```

The optimal number of hash functions is approximately:

```text
k = (m / n) × ln(2)
```

The goal is not to memorize these formulas, but to understand how capacity, memory, and false-positive probability are related.

---

## 7. Bloom Filter Implementation

`docs/07_bloom_filter_implementation.md`

Walks through the Python implementation.

The public interface is intentionally small:

```python
bloom_filter.add(value)

bloom_filter.might_contain(value)
```

The implementation focuses on the core algorithm instead of building unnecessary abstractions.

---

## 8. Real-World Use Cases

`docs/08_real_world_use_cases.md`

Explores practical applications such as:

* Database lookup reduction
* Cache penetration protection
* URL processing
* Web crawling
* Duplicate detection
* Username or identifier checks
* Large-scale membership checks

Each use case explains **why** a Bloom Filter may be useful rather than simply listing applications.

---

## 9. Bloom Filter vs Alternatives

`docs/09_bloom_filter_vs_alternatives.md`

Compares Bloom Filters with alternatives such as:

* Python `set`
* Database lookup
* Redis Set
* Cuckoo Filter

The objective is to understand the trade-offs.

Bloom Filter is not universally better.

It is useful when its specific trade-off is acceptable.

---

## 10. Production Considerations

`docs/10_production_considerations.md`

Covers practical concerns such as:

* Choosing expected capacity
* Choosing false-positive probability
* Memory sizing
* Capacity planning
* Rebuilding filters
* Multiple application instances
* Persistence
* Filter initialization
* What happens when capacity is exceeded
* When not to use a Bloom Filter

This section intentionally stays focused on the practical concerns that matter when taking the concept into a real application.

---

# Examples

The examples progressively introduce the concept.

## Example 1 — Naive Lookup

```text
examples/01_naive_lookup.py
```

Demonstrates the traditional approach:

```text
Request
   |
   v
Database
   |
   v
Membership check
```

This establishes the problem before introducing Bloom Filters.

Run:

```bash
python examples/01_naive_lookup.py
```

---

## Example 2 — Basic Bloom Filter

```text
examples/02_basic_bloom_filter.py
```

Demonstrates:

* Creating a Bloom Filter
* Adding values
* Checking values
* Understanding `probably present` vs `definitely not present`

Run:

```bash
python examples/02_basic_bloom_filter.py
```

---

## Example 3 — False Positive

```text
examples/03_false_positive.py
```

Demonstrates how a value that was never inserted can still produce a:

```text
probably present
```

result.

This makes the probabilistic nature of Bloom Filters visible through code.

Run:

```bash
python examples/03_false_positive.py
```

---

## Example 4 — Bloom Filter Sizing

```text
examples/04_sizing_bloom_filter.py
```

Demonstrates how expected capacity and desired false-positive probability affect:

* Required memory
* Number of bits
* Number of hash functions

Run:

```bash
python examples/04_sizing_bloom_filter.py
```

---

## Example 5 — Realistic Usage

```text
examples/05_realistic_usage.py
```

Demonstrates the common production pattern:

```text
Request
   |
   v
Bloom Filter
   |
   +------------------+
   |                  |
Definitely NOT       MAYBE
   |                  |
   v                  v
Skip lookup       Check source
```

The example uses a simple simulated data source so the project remains self-contained.

Run:

```bash
python examples/05_realistic_usage.py
```

---

# Core API

The implementation intentionally exposes a small API.

```python
from bloom_filter import BloomFilter

bloom = BloomFilter(
    expected_items=100_000,
    false_positive_rate=0.01,
)

bloom.add("apple")
bloom.add("banana")

print(bloom.might_contain("apple"))
print(bloom.might_contain("grape"))
```

The expected behavior is conceptually:

```text
apple -> True
grape -> False
```

But remember:

```text
True  -> Probably present
False -> Definitely not present
```

---

# Choosing the False-Positive Rate

The false-positive rate is a design decision.

For example:

```text
1%
```

means approximately:

```text
1 out of 100
```

membership checks that are actually absent may be reported as present, under the filter's expected operating conditions.

A smaller false-positive rate requires more memory.

For example:

```text
Higher false-positive rate
        ↓
Less memory

Lower false-positive rate
        ↓
More memory
```

Therefore, the correct value depends on the application.

There is no universally correct false-positive rate.

---

# Bloom Filter Is Not a Source of Truth

This is one of the most important rules when using Bloom Filters.

Do not treat:

```text
Bloom Filter says MAYBE
```

as:

```text
The item definitely exists.
```

Instead:

```text
Bloom Filter
     |
     v
MAYBE
     |
     v
Actual source of truth
     |
     v
Final decision
```

The actual source of truth could be:

* Database
* Cache
* Object store
* External service
* Another authoritative data structure

The Bloom Filter simply helps avoid unnecessary work.

---

# When Bloom Filter Is a Good Fit

A Bloom Filter is a good candidate when:

### 1. The dataset is large

Millions or billions of membership checks can make memory efficiency important.

### 2. Membership checks are frequent

The same type of existence question is asked repeatedly.

### 3. False positives are acceptable

The application can perform a second verification.

### 4. Negative results can avoid expensive work

This is particularly important.

If most values being checked are absent, the Bloom Filter can potentially eliminate many expensive lookups.

### 5. Memory efficiency matters

A Bloom Filter can represent a large set using significantly less memory than storing every complete value.

---

# When Not to Use a Bloom Filter

A Bloom Filter is not automatically the right solution.

Avoid it when:

### Exact membership is required

If you need:

```text
Definitely exists
```

without a second lookup, a Bloom Filter alone is not sufficient.

### The dataset is small

If a simple Python set or database lookup is already fast enough, adding a Bloom Filter may only add complexity.

### You need deletion

A standard Bloom Filter does not support straightforward deletion.

Specialized structures such as **Counting Bloom Filters** can address this, but they introduce additional complexity.

### The data changes frequently

If the set changes heavily and maintaining the filter becomes expensive, another data structure may be more appropriate.

### False positives are unacceptable

If even one false positive can cause an incorrect decision, a standard Bloom Filter may not be appropriate.

---

# Design Trade-Off

The fundamental trade-off can be summarized as:

```text
             Bloom Filter
                  |
       +----------+----------+
       |                     |
   Low memory          False positives
       |                     |
       +----------+----------+
                  |
            Fast filtering
```

You are trading:

```text
Exact membership information
```

for:

```text
Compact probabilistic membership information
```

That trade-off is what makes Bloom Filters powerful.

---

# Complexity

For a Bloom Filter with `k` hash functions:

### Add

```text
O(k)
```

### Membership check

```text
O(k)
```

If `k` is treated as a small constant, these operations are effectively:

```text
O(1)
```

The memory requirement is based primarily on the configured bit-array size rather than the size of the original values.

---

# Key Concepts

By completing this repository, you should understand:

* What a Bloom Filter is
* Why Bloom Filters exist
* How bit arrays work
* How hash functions are used
* Why multiple hash functions are useful
* How insertion works
* How membership checks work
* Why false positives occur
* Why false negatives do not occur in a standard Bloom Filter
* How false-positive probability is controlled
* How memory requirements are calculated
* How to size a Bloom Filter
* When Bloom Filters are useful
* When Bloom Filters are a bad choice
* How Bloom Filters can reduce expensive lookups
* How Bloom Filters fit into a larger application

---

# Running the Project

Clone the repository:

```bash
git clone https://github.com/<your-username>/bloom-filter-python.git
cd bloom-filter-python
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run an example:

```bash
python examples/02_basic_bloom_filter.py
```

Run the tests:

```bash
pytest
```

---

# Project Philosophy

This repository intentionally follows a simple engineering approach:

```text
Understand the problem
        ↓
Understand the trade-off
        ↓
Understand the data structure
        ↓
Implement the smallest useful solution
        ↓
Test its behavior
        ↓
Understand real-world usage
```

The goal is not to build the most complicated Bloom Filter system possible.

The goal is to build a solution that is:

* Easy to understand
* Easy to run
* Easy to modify
* Technically correct
* Practical
* Scalable for appropriate use cases

Complexity should be introduced only when the problem requires it.

---

# What This Repository Does Not Try to Cover

To keep the project focused, the core implementation does not depend on:

* Redis
* Kafka
* Celery
* PostgreSQL
* MySQL
* Docker
* Kubernetes
* Cloud services
* Distributed systems

Those technologies can be useful in real production architectures, but they are not required to understand Bloom Filters.

The core concept should be understandable with:

```text
Python
+
Bit Array
+
Hash Functions
```

That is enough to understand the foundation.

---

# Final Takeaway

A Bloom Filter is not magic.

It is a deliberate engineering trade-off.

Instead of storing complete membership information, we store a compact representation that allows us to answer:

```text
"Is this definitely not present?"
```

very efficiently.

The most important mental model is:

```text
                  Expensive Lookup
                        ^
                        |
                      MAYBE
                        |
Request → Bloom Filter
                        |
                 DEFINITELY NOT
                        |
                        v
                 Skip the lookup
```

The power of a Bloom Filter comes from this simple idea:

> **If we can cheaply prove that something does not exist, we can avoid doing expensive work.**

---

## License

This project is open source and available under the MIT License.
