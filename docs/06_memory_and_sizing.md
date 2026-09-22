# Bloom Filter Memory and Sizing

A Bloom Filter is only useful when it is sized correctly.

The main design questions are:

1. How many items will the Bloom Filter store?
2. How much memory should it use?
3. What false-positive rate is acceptable?
4. How many hash functions should it use?
5. What happens if the number of items grows beyond the original expectation?

These parameters are connected.

Changing one can affect the others.

The goal is not to make the Bloom Filter as large as possible.

The goal is to choose enough memory and the right number of hash functions to achieve an acceptable false-positive rate without wasting resources.

---

# 1. The Three Main Parameters

A Bloom Filter is primarily controlled by three parameters.

## Number of expected items

Usually represented as:

```text
n
```

This is the number of values we expect to insert.

For example:

```text
n = 1,000,000
```

means we expect approximately one million items.

---

## Number of bits

Usually represented as:

```text
m
```

This is the total number of bits in the Bloom Filter.

For example:

```text
m = 10,000,000 bits
```

This is approximately:

```text
1.25 MB
```

because:

```text
8 bits = 1 byte
```

---

## Number of hash functions

Usually represented as:

```text
k
```

This determines how many positions each value maps to.

For example:

```text
k = 7
```

means each value sets and checks seven bit positions.

---

# 2. False-Positive Rate

The target false-positive probability is usually represented as:

```text
p
```

For example:

```text
p = 0.01
```

means:

```text
1%
```

Another example:

```text
p = 0.001
```

means:

```text
0.1%
```

Or:

```text
p = 0.0001
```

means:

```text
0.01%
```

A smaller `p` means we want fewer false positives.

But achieving a smaller false-positive rate generally requires more memory.

This is the central sizing trade-off.

---

# 3. The Main Relationship

The four important parameters are:

```text
n = expected number of items
m = number of bits
k = number of hash functions
p = target false-positive probability
```

They are connected.

Conceptually:

```text
More items
    ↓
More bits required
    ↓
More memory
```

And:

```text
Lower false-positive target
    ↓
More bits per item
    ↓
More memory
```

The number of hash functions also needs to be chosen appropriately.

---

# 4. Bits Per Item

One of the easiest ways to reason about Bloom Filter memory is **bits per item**.

Suppose:

```text
n = 1,000,000 items
m = 10,000,000 bits
```

Then:

```text
bits per item = m / n
```

Therefore:

```text
10,000,000 / 1,000,000
= 10 bits per item
```

So the Bloom Filter uses:

```text
10 bits per item
```

This is often more useful than looking at the total bit count alone.

---

# 5. Converting Bits to Memory

Remember:

```text
8 bits = 1 byte
```

Therefore:

```text
m bits / 8 = bytes
```

For example:

```text
10,000,000 bits / 8
= 1,250,000 bytes
```

Approximately:

```text
1.25 MB
```

So:

```text
1 million items
10 bits per item
```

requires approximately:

```text
1.25 MB
```

for the raw bit array.

This is one of the major advantages of a Bloom Filter.

A million complete strings could require substantially more memory than a million bits.

---

# 6. The Memory Formula

If we know:

```text
n = number of items
b = bits per item
```

then:

```text
m = n × b
```

For example:

```text
n = 5,000,000
b = 10
```

Then:

```text
m = 5,000,000 × 10
  = 50,000,000 bits
```

Convert to bytes:

```text
50,000,000 / 8
= 6,250,000 bytes
```

Approximately:

```text
6.25 MB
```

This gives a quick practical estimate.

The more precise approach is to start from the desired false-positive rate and calculate the required number of bits.

---

# 7. Formula for Required Number of Bits

For a standard Bloom Filter, the approximate number of bits required is:

```text
m = -(n × ln(p)) / (ln(2)²)
```

Where:

```text
m = number of bits
n = expected number of inserted items
p = desired false-positive probability
```

The formula looks complicated at first:

```text
m = -(n × ln(p)) / (ln(2)²)
```

But the important thing is understanding what it means.

If:

```text
n
```

increases, the required memory increases.

If:

```text
p
```

becomes smaller, the required memory increases.

---

# 8. Example: 1 Million Items and 1% False Positives

Suppose we need:

```text
n = 1,000,000
p = 0.01
```

The formula is:

```text
m = -(n × ln(p)) / (ln(2)²)
```

Substituting:

```text
m = -(1,000,000 × ln(0.01)) / (ln(2)²)
```

The result is approximately:

```text
m ≈ 9,585,059 bits
```

Convert to bytes:

```text
9,585,059 / 8
≈ 1,198,132 bytes
```

Approximately:

```text
1.2 MB
```

So roughly:

```text
1 million items
1% false-positive target
≈ 9.6 bits per item
≈ 1.2 MB
```

This is a useful practical reference point.

---

# 9. Formula for the Optimal Number of Hash Functions

Once we know the required number of bits, we can estimate the optimal number of hash functions using:

```text
k = (m / n) × ln(2)
```

Where:

```text
k = number of hash functions
m = number of bits
n = number of expected items
```

For the previous example:

```text
m / n ≈ 9.585
```

Therefore:

```text
k ≈ 9.585 × ln(2)
```

which is approximately:

```text
k ≈ 6.64
```

Since we need a practical integer:

```text
k ≈ 7
```

So a reasonable configuration is approximately:

```text
1,000,000 items
≈ 9.6 million bits
7 hash functions
≈ 1.2 MB
≈ 1% target false-positive rate
```

The exact implementation may round the bit-array size and configuration values.

---

# 10. Why There Is an Optimal Number of Hash Functions

It may seem logical that:

> More hash functions should always make the Bloom Filter more accurate.

That is not true.

Each hash function sets another bit.

If we use too few hash functions:

```text
Too few bits set per item
        ↓
Less information
        ↓
Higher chance of overlap
        ↓
More false positives
```

If we use too many:

```text
Too many bits set per item
        ↓
Bit array fills quickly
        ↓
More saturation
        ↓
False positives increase
```

There is therefore an optimal range.

Conceptually:

```text
False-positive rate
        ^
        |
        | \       /
        |  \     /
        |   \___/
        |
        +------------------> Number of hash functions
                  ^
               optimal
```

The exact optimal value depends on:

```text
m
n
```

---

# 11. Bits Per Item Is a Useful Shortcut

Instead of always thinking in terms of total memory, we can think:

```text
bits per item
```

For example:

```text
5 bits/item
8 bits/item
10 bits/item
12 bits/item
15 bits/item
```

More bits per item generally means:

```text
More memory
    ↓
Lower false-positive rate
```

Fewer bits per item means:

```text
Less memory
    ↓
Higher false-positive rate
```

This makes Bloom Filter sizing easier to reason about.

---

# 12. Example Configurations

Consider a system expecting:

```text
1,000,000 items
```

We can think about several possible configurations.

### Around 5 bits per item

```text
Memory ≈ 625 KB
```

This saves memory but allows a higher false-positive rate.

---

### Around 10 bits per item

```text
Memory ≈ 1.25 MB
```

This provides a lower false-positive rate.

---

### Around 15 bits per item

```text
Memory ≈ 1.875 MB
```

This provides an even lower false-positive target.

The exact false-positive probabilities depend on the number of hash functions and the actual configuration.

The important system-design principle is:

> More memory can be deliberately exchanged for fewer false positives.

---

# 13. Example: Different Accuracy Requirements

Suppose a system needs to filter:

```text
10 million IDs
```

Consider three requirements.

### Requirement A

```text
False-positive target: 5%
```

The Bloom Filter can use relatively little memory.

---

### Requirement B

```text
False-positive target: 1%
```

More bits per item are required.

---

### Requirement C

```text
False-positive target: 0.01%
```

Significantly more memory is required.

The relationship is not linear.

Reducing the false-positive target substantially can require noticeably more bits per item.

This is why the target should come from the application's actual requirements rather than simply choosing the smallest possible probability.

---

# 14. Why Not Always Choose an Extremely Small False-Positive Rate?

Suppose a system has:

```text
1 million items
```

and a database lookup costs very little.

Choosing:

```text
p = 0.000001
```

may provide very little practical benefit while consuming additional memory.

If:

```text
p = 1%
```

already reduces database traffic enough, spending much more memory to reach:

```text
0.0001%
```

may not be worthwhile.

This is a system-design trade-off.

The right question is:

> How expensive is a false positive compared with the memory required to reduce it?

---

# 15. The Cost of a False Positive

Suppose a false positive causes:

```text
one database lookup
```

and the database is highly available and inexpensive to query.

Then a small false-positive rate may be acceptable.

But suppose a false positive causes:

```text
expensive external API call
```

or:

```text
expensive computation
```

or:

```text
large network transfer
```

Then reducing false positives may have more value.

Therefore:

```text
Value of reducing false positives
        depends on
Cost of downstream work
```

This is more important than simply trying to minimize the mathematical probability.

---

# 16. Expected Number of Extra Lookups

Suppose we have:

```text
10 million negative requests
```

and the Bloom Filter has:

```text
1% false-positive rate
```

Approximately:

```text
10,000,000 × 0.01
= 100,000
```

negative requests could still pass through the Bloom Filter.

That means approximately:

```text
100,000
```

extra exact lookups could occur.

If each lookup is expensive, that may matter.

If the lookup is cheap, it may not.

This is why sizing should be based on workload, not only on a percentage.

---

# 17. A More Useful Production Calculation

Imagine:

```text
Requests per day = 100 million
Negative requests = 80 million
False-positive rate = 1%
```

Potential false-positive lookups:

```text
80,000,000 × 0.01
= 800,000
```

So even a 1% false-positive rate can translate into a significant number of extra operations at large scale.

But compare that with the work avoided.

Without the Bloom Filter:

```text
80 million negative requests
        ↓
80 million expensive lookups
```

With a 1% false-positive rate:

```text
80 million negative requests
        ↓
Bloom Filter
        ↓
~800,000 may continue
```

The exact observed numbers depend on workload and filter behavior, but the order-of-magnitude reasoning demonstrates why a probabilistic filter can still provide substantial value.

---

# 18. The Most Important Sizing Inputs

Before creating a Bloom Filter, we should know:

```text
1. Expected number of items
2. Target false-positive rate
3. Cost of a downstream lookup
4. Available memory
5. Expected query volume
6. Whether the number of items will grow
```

For example:

```text
Expected items:
10,000,000

Target false-positive rate:
1%

Available memory:
50 MB

Downstream operation:
Database lookup
```

These inputs give us enough information to design the filter.

---

# 19. What If the Number of Items Grows?

This is an important production concern.

Suppose we create a filter for:

```text
1 million items
```

but the dataset grows to:

```text
10 million items
```

The original sizing assumptions are no longer valid.

The Bloom Filter will become more saturated.

Therefore:

```text
Original capacity
        ↓
More insertions
        ↓
More bits set
        ↓
Higher false-positive rate
```

A Bloom Filter does not automatically grow like a Python set.

The bit array has a fixed size.

---

# 20. Standard Bloom Filter Is Not Dynamically Resizable

Suppose:

```text
m = 10 million bits
```

Once created, the standard Bloom Filter has those:

```text
10 million bits
```

It does not automatically become:

```text
20 million bits
```

when more data arrives.

This means the expected capacity should be considered when designing the filter.

If the dataset can grow significantly, the architecture needs a strategy.

Possible approaches include:

* Create a larger filter from the beginning
* Build a new filter and migrate
* Use multiple Bloom Filters
* Use a scalable Bloom Filter design

The core repository intentionally focuses on the standard Bloom Filter rather than implementing a dynamic multi-filter architecture.

---

# 21. Multiple Bloom Filters

One practical approach for growing datasets is to maintain multiple filters.

For example:

```text id="u4p7u7"
Filter 1
1M items

Filter 2
1M items

Filter 3
1M items
```

When a new capacity boundary is reached:

```text id="1z6zms"
Create another filter
```

Lookup can check:

```text id="6b4n3c"
Filter 1
Filter 2
Filter 3
```

This allows the system to grow without modifying an existing bit array.

However, there is a trade-off:

```text
More filters
    ↓
More lookup work
```

This is a useful production technique, but it is beyond the scope of the core implementation in this repository.

---

# 22. Memory Sizing Example

Let's work through a practical example.

Suppose:

```text
Expected items = 5,000,000
Target false-positive rate = 1%
```

Using:

```text
m = -(n × ln(p)) / (ln(2)²)
```

we get approximately:

```text
m ≈ 47,925,292 bits
```

Convert to bytes:

```text
47,925,292 / 8
≈ 5,990,662 bytes
```

Approximately:

```text
5.99 MB
```

Bits per item:

```text
47,925,292 / 5,000,000
≈ 9.59 bits/item
```

Optimal hash count:

```text
k = (m / n) × ln(2)
```

which gives approximately:

```text
k ≈ 6.64
```

So a practical configuration is approximately:

```text
Expected items:       5,000,000
Bits:                 ~47.9 million
Memory:               ~6 MB
Hash functions:       ~7
Target FP rate:       ~1%
```

This demonstrates how the mathematical parameters translate into actual implementation values.

---

# 23. Rounding in Real Implementations

Mathematical formulas often produce values such as:

```text
m = 47,925,292.4
```

But an implementation needs an integer number of bits.

Therefore, we need to round appropriately.

Similarly:

```text
k = 6.64
```

must become an integer:

```text
k = 7
```

The implementation should ensure:

```text
bit_array_size >= required_size
```

rather than accidentally rounding downward and providing less capacity than intended.

The repository implementation will handle these calculations programmatically.

---

# 24. Memory Overhead in Real Python

The mathematical calculation describes the **raw bit-array requirement**.

Actual Python memory usage depends on how the bit array is represented.

For example, storing each bit as a Python integer:

```python
bits = [0, 0, 0, 0, ...]
```

is extremely inefficient compared with storing actual packed bits.

A Python list contains object references and has substantial overhead.

Therefore, a production-quality memory-efficient implementation should not assume:

```text
1 Python integer = 1 bit
```

The repository's implementation should use a compact representation appropriate for the educational goal.

The theoretical sizing formulas still describe the number of logical bits required.

---

# 25. Logical Bits vs Physical Memory

This distinction is important.

Suppose the calculation says:

```text
10 million bits
```

That means the Bloom Filter logically needs:

```text
10,000,000 binary positions
```

The ideal raw storage is:

```text
10,000,000 / 8
= 1.25 MB
```

But actual memory may be somewhat different depending on:

* Data structure used
* Language runtime
* Object overhead
* Alignment
* Serialization format

Therefore:

> Bloom Filter sizing formulas describe the logical bit requirement, while actual application memory usage depends on the implementation.

---

# 26. Why a Python Set Can Be Much Larger

Consider:

```text
1 million IDs
```

A Python set stores:

```text
Actual values
+
Hash-table metadata
+
Object references
+
Object overhead
```

A Bloom Filter only stores:

```text
Bits
```

For example:

```text id="u4v4hy"
1 million items
10 bits/item
```

requires roughly:

```text id="3d0b9u"
10 million bits
≈ 1.25 MB
```

The equivalent Python set may require substantially more memory depending on:

* String length
* Python object overhead
* Hash-table capacity
* Runtime implementation

This is one of the strongest reasons to use Bloom Filters when exact membership storage is too expensive.

---

# 27. Memory Is Not the Only Resource

Sizing should not focus only on RAM.

Increasing `k` means:

```text
More hash calculations
More bit checks
```

Increasing `m` means:

```text
More memory
```

Therefore:

```text
Memory
+
CPU
+
Latency
+
False-positive rate
```

must all be considered.

For example, a Bloom Filter with an extremely large `k` might reduce false positives under some configurations but increase CPU cost unnecessarily.

Good system design balances the resources instead of optimizing one metric blindly.

---

# 28. Sizing Based on Business Cost

A practical way to approach sizing is:

### Step 1

Estimate:

```text
How many values will be inserted?
```

### Step 2

Estimate:

```text
How many negative lookups will occur?
```

### Step 3

Determine:

```text
How expensive is an unnecessary lookup?
```

### Step 4

Choose:

```text
Acceptable false-positive rate
```

### Step 5

Calculate:

```text
Required bits
```

### Step 6

Calculate:

```text
Optimal number of hash functions
```

### Step 7

Check:

```text
Actual memory and CPU budget
```

This makes Bloom Filter sizing a system-design decision rather than a purely mathematical exercise.

---

# 29. Example Decision

Suppose:

```text
Expected items:
10 million

Negative requests:
50 million/day

Downstream lookup:
Database query

Memory available:
100 MB
```

We might consider a target such as:

```text
1% false-positive rate
```

Then calculate the required memory.

If the result is comfortably below:

```text
100 MB
```

the design may fit the memory budget.

We can then estimate the potential number of false-positive lookups:

```text
50 million × 1%
= 500,000
```

Now ask:

```text
Is 500,000 extra database lookups acceptable?
```

If yes, the configuration may be reasonable.

If no, we may choose a lower target false-positive rate and spend more memory.

This is the kind of reasoning that matters in production system design.

---

# 30. The Most Important Trade-Off

The Bloom Filter sizing problem can be summarized as:

```text
                 MORE MEMORY
                     |
                     v
              More bits/item
                     |
                     v
              Less bit overlap
                     |
                     v
          Lower false-positive rate
```

But:

```text
More hash functions
        |
        v
More CPU work
        |
        v
Potentially better filtering
```

until the optimal point is reached.

And:

```text
More inserted items
        |
        v
More saturation
        |
        v
Higher false-positive rate
```

This gives us three major system-design levers:

```text
Memory
Hash count
Capacity
```

---

# 31. What Happens If We Underestimate Capacity?

Suppose we expect:

```text
1 million items
```

but actual usage becomes:

```text
5 million items
```

The Bloom Filter may still technically work.

However:

```text
Bit saturation increases
        ↓
False positives increase
        ↓
Fewer requests are filtered
        ↓
More downstream work
```

Therefore, underestimating capacity is not necessarily an immediate correctness failure.

It is primarily a **performance and efficiency problem**.

This distinction is important.

---

# 32. What Happens If We Overestimate Capacity?

Now suppose we expect:

```text
10 million items
```

but actually insert:

```text
500,000 items
```

The Bloom Filter will have a lot of unused capacity.

This means:

```text
More memory allocated than necessary
```

but the filter can still have a very low false-positive rate.

So overestimating capacity usually trades:

```text
More memory
```

for:

```text
Lower saturation
```

The decision depends on memory availability and expected future growth.

---

# 33. Practical Configuration Guidelines

There is no universal configuration, but the following thought process is useful.

For a small application:

```text
Small dataset
+
Cheap lookup
```

A Bloom Filter may not be necessary at all.

For a large system:

```text
Millions of membership checks
+
Expensive downstream lookup
+
Large number of negative requests
```

A Bloom Filter becomes more attractive.

Then choose:

```text
Expected capacity
+
Acceptable false-positive rate
```

and derive:

```text
Bit-array size
+
Hash count
```

---

# 34. Common Sizing Mistakes

## Mistake 1: Choosing a random bit-array size

Example:

```text
m = 1,000,000
```

without considering:

```text
Number of items
False-positive target
```

This makes the configuration difficult to reason about.

---

## Mistake 2: Ignoring future growth

Designing for:

```text
1 million items
```

when the dataset will quickly reach:

```text
10 million
```

can cause high saturation.

---

## Mistake 3: Using too many hash functions

More hashes mean more CPU work.

There is an optimal value.

More is not automatically better.

---

## Mistake 4: Optimizing only for memory

Using extremely few bits can save RAM but create too many false positives.

That can cause the downstream system to perform almost as much work as before.

---

## Mistake 5: Optimizing only for false positives

A very low target may require significantly more memory than the workload actually needs.

The target should come from the business and system requirements.

---

# 35. Sizing Formula Summary

For a standard Bloom Filter:

### Required bits

```text
m = -(n × ln(p)) / (ln(2)²)
```

### Optimal number of hash functions

```text
k = (m / n) × ln(2)
```

### Bits per item

```text
bits_per_item = m / n
```

### Bytes

```text
bytes = m / 8
```

Where:

```text
n = expected number of items
m = number of bits
k = number of hash functions
p = target false-positive probability
```

These formulas provide the mathematical foundation for the sizing implementation.

---

# 36. A Simple Reference Table

For intuition, approximate memory requirements for a 1 million-item Bloom Filter are:

| Target false-positive rate | Approx. bits/item | Approx. memory |
| -------------------------- | ----------------: | -------------: |
| 10%                        |               4.8 |         0.6 MB |
| 5%                         |               6.2 |         0.8 MB |
| 1%                         |               9.6 |         1.2 MB |
| 0.1%                       |              14.4 |         1.8 MB |
| 0.01%                      |              19.2 |         2.4 MB |

These are approximate values for the raw bit array.

Actual application memory can differ depending on the implementation.

The important pattern is:

```text
Lower false-positive target
        ↓
More bits per item
        ↓
More memory
```

---

# 37. Sizing Is a Capacity Contract

A useful production mindset is to treat Bloom Filter sizing as a kind of capacity contract.

For example:

```text
Expected capacity:
10 million items

Target false-positive rate:
1%

Memory budget:
~12 MB
```

The system is effectively saying:

> "This filter is designed around approximately 10 million items and this accuracy target."

If the workload changes significantly, the Bloom Filter configuration should be reconsidered.

This is similar to capacity planning for:

* caches
* connection pools
* queues
* database indexes
* worker pools

The data structure is part of the system's capacity model.

---

# 38. The Core Insight

The Bloom Filter's main advantage comes from using a very small amount of memory to represent a large number of membership possibilities.

But that compression has a cost.

```text
More compression
       ↓
Less memory
       ↓
More overlap
       ↓
More false positives
```

Or:

```text
More memory
       ↓
More bits per item
       ↓
Less overlap
       ↓
Fewer false positives
```

The system designer chooses where to sit on this curve.

There is no universally correct point.

---

# 39. What This Repository Will Use

The repository will keep the implementation configurable rather than hard-coding one specific production configuration.

The Bloom Filter will conceptually accept:

```text
expected number of items
+
target false-positive rate
```

and derive appropriate:

```text
bit-array size
+
number of hash functions
```

This makes the implementation easier to reuse.

For example, the same class could be configured for:

```text
100,000 items
1% false-positive rate
```

or:

```text
10,000,000 items
0.1% false-positive rate
```

without changing the core algorithm.

---

# 40. What We Have Learned

At this point, we can connect the mathematical model to the system-design problem.

A Bloom Filter needs us to think about:

```text
How many items?
        +
How much memory?
        +
How much uncertainty is acceptable?
```

These determine:

```text
Bit-array size
        +
Number of hash functions
```

And those determine the resulting false-positive behavior.

The key relationship is:

```text
                    Bloom Filter
                         |
            +------------+------------+
            |                         |
       Memory budget             Accuracy target
            |                         |
            +------------+------------+
                         |
                         v
                  Filter parameters
                         |
              +----------+----------+
              |                     |
              v                     v
         Bit-array size         Hash count
```

---

# 41. Key Takeaways

The most important points are:

1. `n` represents the expected number of inserted items.
2. `m` represents the total number of bits.
3. `k` represents the number of hash functions.
4. `p` represents the target false-positive probability.
5. More items require more memory for the same accuracy.
6. Lower false-positive targets require more bits per item.
7. `m = -(n × ln(p)) / (ln(2)²)` gives the approximate required bit count.
8. `k = (m / n) × ln(2)` gives the approximate optimal number of hash functions.
9. Bits per item is a useful way to reason about Bloom Filter memory.
10. The raw bit-array memory is approximately `m / 8` bytes.
11. The actual runtime memory depends on how the bit array is implemented.
12. More hash functions are not automatically better.
13. Underestimating capacity can increase saturation and false positives.
14. Overestimating capacity primarily wastes memory.
15. False-positive rate should be chosen based on the cost of downstream work.
16. Bloom Filter sizing is a capacity-planning decision.
17. The standard Bloom Filter has a fixed-size bit array and does not automatically grow.
18. If the dataset grows significantly, the architecture may need resizing or multiple filters.
19. The core implementation should calculate configuration parameters rather than relying on arbitrary values.

The central system-design lesson is:

> **Bloom Filter sizing is about choosing the right balance between memory, CPU, capacity, and false-positive rate for the workload.**

---

# 42. What Comes Next?

We now understand the complete theory behind the Bloom Filter:

```text
Business Problem
      ↓
Why Bloom Filter
      ↓
Bit Array
      ↓
Hash Functions
      ↓
False Positives
      ↓
Memory & Sizing
```

We are now ready to move from theory into implementation.

The next document:

```text
07_bloom_filter_implementation.md
```

will explain how to turn these concepts into a clean Python implementation.

It will cover:

* Class design
* Bit-array representation
* Configuration
* Hash generation
* `add()`
* `might_contain()`
* Parameter validation
* Error handling
* Complexity
* Design decisions
* A complete implementation walkthrough

The goal will be to keep the implementation small enough to understand while still reflecting the important production concepts covered in the previous documents.
