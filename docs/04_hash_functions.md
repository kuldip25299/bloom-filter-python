# Hash Functions in a Bloom Filter

Hash functions are one of the most important parts of a Bloom Filter.

The bit array provides the storage, but hash functions decide **which bits represent each value**.

If the hash positions are poorly distributed, the Bloom Filter can become less effective because too many values will map to the same positions.

This document explains:

* What a hash function does
* Why Bloom Filters need multiple hash positions
* How hash values are converted into bit positions
* Deterministic hashing
* Hash distribution
* Hash collisions
* How to generate multiple positions efficiently
* The hashing strategy used in this repository
* Common implementation mistakes

---

# 1. What Is a Hash Function?

A hash function takes an input value and converts it into a number.

Conceptually:

```text
"apple"
   |
   v
Hash Function
   |
   v
123456789
```

For a different value:

```text
"banana"
   |
   v
Hash Function
   |
   v
987654321
```

The exact number is not important by itself.

The important property is that the hash function gives us a deterministic way to map a value to a location.

---

# 2. Why Does a Bloom Filter Need Hash Functions?

Our Bloom Filter has a fixed number of bits.

For example:

```text
10 bits

Index:
0 1 2 3 4 5 6 7 8 9
```

But our input could be anything:

```text
apple
banana
customer-12345
https://example.com/product/123
transaction-98765
```

We cannot directly use those values as array indexes.

Hash functions solve this problem.

For example:

```text
"apple"
    |
    v
hash -> 123456
    |
    v
123456 % 10
    |
    v
6
```

Now we can use:

```text
bit[6]
```

So the general process is:

```text
Value
  ↓
Hash Function
  ↓
Large Integer
  ↓
Map into Bit Array
  ↓
Bit Position
```

---

# 3. Mapping a Hash to the Bit Array

Suppose the Bloom Filter has:

```text
m = 10 bits
```

and our hash function produces:

```text
hash("apple") = 123456
```

We need a position between:

```text
0 and 9
```

A common approach is:

```text
position = hash_value % m
```

Therefore:

```text
123456 % 10 = 6
```

So:

```text
bit[6] = 1
```

The modulo operation converts a potentially very large hash value into a valid position inside the bit array.

---

# 4. Why One Hash Function Is Not Enough

A Bloom Filter normally uses multiple hash positions for each value.

Suppose we have only one:

```text
hash("apple") -> 6
```

Then the Bloom Filter only records:

```text
bit[6] = 1
```

That gives us very little information.

Instead, we want something like:

```text
"apple"

hash 1 -> 2
hash 2 -> 6
hash 3 -> 8
```

Now the value is represented by:

```text
{2, 6, 8}
```

The Bloom Filter sets all three bits:

```text
bit[2] = 1
bit[6] = 1
bit[8] = 1
```

This combination gives the Bloom Filter more information to work with.

---

# 5. Multiple Hash Functions

The traditional explanation is that a Bloom Filter uses `k` independent hash functions.

For example:

```text
h1(value)
h2(value)
h3(value)
```

For `"apple"`:

```text
h1("apple") -> 2
h2("apple") -> 6
h3("apple") -> 8
```

The insertion process becomes:

```text
for each hash function:
    calculate position
    set bit to 1
```

Conceptually:

```text
apple
  |
  +---- h1 ----> 2
  |
  +---- h2 ----> 6
  |
  +---- h3 ----> 8
```

Then:

```text
bit[2] = 1
bit[6] = 1
bit[8] = 1
```

---

# 6. Do We Actually Need Completely Independent Hash Functions?

Not necessarily.

A practical implementation does not have to maintain several completely separate hashing algorithms.

Generating multiple independent cryptographic or high-quality hashes can be more expensive than necessary.

Instead, we can use a technique called **double hashing**.

The idea is to calculate two base hash values and derive multiple positions from them.

Conceptually:

```text
h1 = hash1(value)
h2 = hash2(value)
```

Then:

```text
position_0 = h1
position_1 = h1 + h2
position_2 = h1 + 2*h2
position_3 = h1 + 3*h2
...
```

Each position is then mapped into the Bloom Filter:

```text
position_i % m
```

This allows us to generate multiple positions without calculating a completely separate hash function every time.

---

# 7. Double Hashing

The general formula is:

```text
position_i = (h1 + i * h2) % m
```

where:

```text
h1 = first hash value
h2 = second hash value
i  = 0, 1, 2, ..., k-1
m  = number of bits
```

Suppose:

```text
h1 = 17
h2 = 31
m = 10
```

and we want:

```text
k = 4
```

Then:

```text
i = 0

(17 + 0 * 31) % 10
= 7
```

Next:

```text
i = 1

(17 + 1 * 31) % 10
= 8
```

Next:

```text
i = 2

(17 + 2 * 31) % 10
= 9
```

Next:

```text
i = 3

(17 + 3 * 31) % 10
= 0
```

So our four positions are:

```text
7, 8, 9, 0
```

The Bloom Filter can set:

```text
bit[7] = 1
bit[8] = 1
bit[9] = 1
bit[0] = 1
```

---

# 8. Why Determinism Matters

The hashing process must be deterministic.

If we insert:

```text
apple
```

and get:

```text
2, 6, 8
```

then checking `"apple"` later must produce:

```text
2, 6, 8
```

again.

Otherwise the Bloom Filter cannot work.

The process must therefore behave like:

```text
Same Input
    |
    v
Same Hashing Strategy
    |
    v
Same Positions
```

For example:

```text
apple -> 2, 6, 8
apple -> 2, 6, 8
apple -> 2, 6, 8
```

Every time.

---

# 9. Why Python's Built-In hash() Needs Care

Python provides a built-in:

```python
hash()
```

It is convenient:

```python
hash("apple")
```

However, Python's built-in hash behavior is not ideal when we need a Bloom Filter whose bit representation must remain stable across separate Python processes or persisted instances.

Python intentionally uses hash randomization for certain built-in types.

That means you should not assume that:

```python
hash("apple")
```

will produce the same integer across independent Python processes.

For an in-memory Bloom Filter that is created and consumed within the same process, this may not matter.

But for a reusable implementation, especially one that may eventually be serialized or shared between processes, relying directly on Python's built-in `hash()` is a poor design choice.

A more predictable approach is to use a deterministic hashing algorithm.

---

# 10. Using hashlib

Python's standard library provides deterministic hashing through:

```python
import hashlib
```

For example:

```python
hashlib.sha256(b"apple")
```

produces a deterministic digest.

Conceptually:

```text
"apple"
   |
   v
SHA-256
   |
   v
fixed-length digest
```

The digest can then be converted into an integer.

For example:

```python
digest = hashlib.sha256(b"apple").digest()
value = int.from_bytes(digest, "big")
```

Now:

```text
digest
  ↓
integer
  ↓
bit position
```

This gives us a deterministic foundation for generating Bloom Filter positions.

---

# 11. Why Use hashlib Instead of a Cryptographic Hash for Security?

A Bloom Filter does not normally need cryptographic security.

We are using the hash function primarily for:

* deterministic output
* good distribution
* repeatability
* converting arbitrary values into positions

We are **not** using the hash to protect a password or authenticate data.

Therefore, the goal is not:

> Find the strongest cryptographic hash possible.

The goal is:

> Generate stable and reasonably well-distributed hash values efficiently.

For a simple educational implementation, using Python's standard `hashlib` functionality gives us a clear and dependency-free approach.

---

# 12. Generating Two Base Hashes

A practical implementation can generate two deterministic hash values from the input.

For example:

```text
h1 = hash_function_1(value)
h2 = hash_function_2(value)
```

Then use double hashing:

```text
position_i = (h1 + i * h2) % m
```

If:

```text
k = 3
```

we generate:

```text
position_0
position_1
position_2
```

This means we do not need to run three completely separate hashing algorithms.

---

# 13. Example With a Realistic Bloom Filter

Suppose our Bloom Filter has:

```text
m = 100 bits
k = 4
```

For:

```text
"customer-123"
```

suppose the two base hashes are:

```text
h1 = 123456
h2 = 789012
```

We generate:

```text
position_0 = (123456 + 0 * 789012) % 100
position_1 = (123456 + 1 * 789012) % 100
position_2 = (123456 + 2 * 789012) % 100
position_3 = (123456 + 3 * 789012) % 100
```

The result is four valid bit positions.

The Bloom Filter then sets those four bits.

The exact positions are not important for understanding the concept.

The important architecture is:

```text
Value
  |
  +---- Hash 1 ----+
  |                |
  +---- Hash 2 ----+
                   |
                   v
             Double Hashing
                   |
                   v
        Multiple Bit Positions
```

---

# 14. Why Good Distribution Matters

Suppose we have 1,000 bits.

Ideally, values should spread across the available positions.

For example:

```text
value A -> 10
value B -> 527
value C -> 83
value D -> 901
value E -> 311
```

This spreads writes throughout the bit array.

But imagine a poor hashing strategy that frequently produces:

```text
10
10
11
10
12
10
11
```

A large number of values would concentrate in a small part of the array.

The result would be:

```text
Some bits become 1 very quickly
Other bits remain 0
```

This causes unnecessary overlap and can increase false positives.

Therefore:

> Good hash distribution is important because the Bloom Filter's accuracy depends on how the bits are populated.

---

# 15. Hash Collisions Are Not Automatically a Bug

Different values can produce the same hash position.

For example:

```text
apple  -> bit 15
orange -> bit 15
```

This is a collision.

But collisions are expected because we are mapping an enormous input space into a finite number of bits.

There might be:

```text
millions or billions of possible values
```

but only:

```text
millions of bit positions
```

Eventually, different values will share positions.

The Bloom Filter is specifically designed around this behavior.

The problem is not that collisions exist.

The problem is whether the collision rate becomes high enough to make the filter ineffective.

---

# 16. Hashing Does Not Store the Original Value

This is worth repeating because it is easy to misunderstand.

Suppose we insert:

```text
customer-123
```

The Bloom Filter does not store:

```text
customer-123
```

It stores only the resulting bit positions.

For example:

```text
customer-123
      |
      v
  hash values
      |
      v
  12, 87, 103
      |
      v
set those bits
```

Later, we cannot reverse:

```text
12, 87, 103
```

into:

```text
customer-123
```

The Bloom Filter is therefore a membership structure, not a storage structure.

---

# 17. Hashing During Insertion

The insertion process looks like this:

```text
                INSERT
                   |
                   v
                 Value
                   |
             +-----+-----+
             |           |
             v           v
           Hash 1      Hash 2
             |           |
             +-----+-----+
                   |
                   v
             Generate k positions
                   |
                   v
          position % bit_array_size
                   |
                   v
             Set bits to 1
```

For example:

```text
apple
  |
  v
h1 = ...
h2 = ...
  |
  v
positions = [3, 18, 42]
  |
  v
bit[3]  = 1
bit[18] = 1
bit[42] = 1
```

---

# 18. Hashing During Lookup

Lookup must use the exact same process.

```text
                LOOKUP
                   |
                   v
                 Value
                   |
             +-----+-----+
             |           |
             v           v
           Hash 1      Hash 2
             |           |
             +-----+-----+
                   |
                   v
             Generate k positions
                   |
                   v
          position % bit_array_size
                   |
                   v
             Check all bits
```

For example:

```text
apple
  |
  v
h1 = ...
h2 = ...
  |
  v
positions = [3, 18, 42]
  |
  v
check:

bit[3]
bit[18]
bit[42]
```

If any is zero:

```text
Definitely not present
```

If all are one:

```text
Probably present
```

---

# 19. The Hashing Process Must Match Exactly

This is a common implementation mistake.

Suppose insertion uses:

```text
k = 3
m = 1000
```

and generates positions using:

```text
(h1 + i * h2) % m
```

Lookup must use exactly the same:

```text
k
m
h1
h2
formula
input encoding
```

If insertion uses:

```text
UTF-8 bytes
```

but lookup uses a different encoding, the hash values can change.

If insertion uses:

```text
SHA-256
```

but lookup uses:

```text
MD5
```

the positions change.

If insertion uses:

```text
k = 3
```

but lookup uses:

```text
k = 4
```

the membership logic changes.

Therefore:

> A Bloom Filter's hashing configuration is part of the data structure's state.

---

# 20. Input Encoding Matters

Hash functions normally operate on bytes.

A string such as:

```text
"apple"
```

must therefore be converted into bytes.

A common encoding is:

```python
"apple".encode("utf-8")
```

which produces bytes representing the string.

Conceptually:

```text
"apple"
   |
   v
UTF-8 encoding
   |
   v
bytes
   |
   v
hash function
```

For a simple Python implementation, UTF-8 is a practical default.

---

# 21. Should We Use Random Hashing?

For a standard Bloom Filter, the answer is generally no for the core membership calculation.

Suppose insertion randomly chooses positions:

```text
apple -> 2, 7, 9
```

but lookup later randomly chooses:

```text
apple -> 1, 4, 8
```

The lookup would fail even though the value was inserted.

Therefore, the hashing process must be deterministic.

Randomness can be used in some advanced hashing designs or parameter selection, but the actual mapping from a value to its Bloom Filter positions must be reproducible.

---

# 22. Number of Hash Functions

The number of hash functions is commonly represented as:

```text
k
```

For example:

```text
k = 3
```

means every inserted value affects three positions.

Increasing `k` means:

```text
More positions checked
More bits set per value
More CPU work
```

Decreasing `k` means:

```text
Fewer positions checked
Fewer bits set per value
Less CPU work
```

There is therefore a trade-off.

The correct value of `k` depends on:

* number of expected items
* bit-array size
* target false-positive rate

The mathematical relationship between these parameters will be covered in:

```text
06_memory_and_sizing.md
```

For now, the important point is:

> `k` is a configuration parameter, not an arbitrary number that should change between insertion and lookup.

---

# 23. Hash Functions and False Positives

Hashing directly affects false positives.

Suppose many values map to the same small group of bits:

```text
10
10
11
10
11
12
10
```

Those bits become saturated quickly.

Then a new value may find all of its required bits already set:

```text
bit[10] = 1
bit[11] = 1
bit[12] = 1
```

The Bloom Filter returns:

```text
Probably present
```

even when the value was never inserted.

A well-sized Bloom Filter with appropriate hashing spreads the values more effectively.

This does not eliminate false positives.

It controls how frequently they occur.

The detailed behavior and measurement of false positives will be covered in:

```text
05_false_positives.md
```

---

# 24. A Simple Mental Model for Hashing

Think of the hash functions as a routing mechanism.

Suppose the Bloom Filter contains:

```text
1000 bits
```

The hash functions answer:

> "Which few positions should represent this value?"

For example:

```text
customer-123
       |
       v
    hashing
       |
       v
  103, 421, 872
```

The Bloom Filter then uses:

```text
103
421
872
```

as the representation of that value.

Another value:

```text
customer-456
       |
       v
    hashing
       |
       v
  84, 421, 912
```

Notice that both values use:

```text
421
```

Again, this is normal.

The Bloom Filter only cares about whether the required bits are set.

---

# 25. What the Core Implementation Will Do

This repository intentionally keeps the implementation simple.

The Bloom Filter will conceptually have:

```text
bit_array_size
number_of_hashes
bit_array
```

and hashing logic that can:

```text
generate_positions(value)
```

The rest of the implementation can build on that.

Conceptually:

```python
positions = generate_positions(value)

for position in positions:
    bit_array[position] = 1
```

For lookup:

```python
positions = generate_positions(value)

for position in positions:
    if bit_array[position] == 0:
        return False

return True
```

The implementation details will come later.

The important thing is that the hashing logic is isolated and predictable.

---

# 26. Common Hashing Mistakes

## Mistake 1: Using Random Positions

Bad approach:

```text
Insert -> random positions
Lookup -> different random positions
```

This breaks membership checks.

Positions must be deterministic.

---

## Mistake 2: Changing the Hash Configuration

If a Bloom Filter was created with:

```text
m = 10,000
k = 4
```

and lookup uses:

```text
m = 20,000
k = 5
```

the generated positions will be different.

The filter configuration must remain consistent.

---

## Mistake 3: Using Different Input Encoding

For example:

```text
Insertion -> UTF-8
Lookup    -> different encoding
```

This can produce different hash values.

Use the same encoding strategy consistently.

---

## Mistake 4: Assuming Hash Values Must Be Unique

They do not.

Multiple values can map to the same positions.

Collisions are part of the design.

---

## Mistake 5: Treating the Hash as the Stored Data

The Bloom Filter does not store:

```text
hash -> original value
```

It only stores:

```text
bit positions -> 1
```

It cannot reconstruct the original value.

---

# 27. Hashing in the Overall Bloom Filter

We can now see how hashing fits into the complete architecture:

```text
                    VALUE
                      |
                      v
               +--------------+
               | Hashing      |
               | Strategy     |
               +--------------+
                      |
                      v
              Multiple positions
                      |
                      v
               +--------------+
               | Bit Array     |
               +--------------+
                      |
                      v
               Set / Check bits
```

The responsibilities are separated:

### Hashing

Answers:

> Which positions represent this value?

### Bit array

Stores:

> Which positions have already been activated?

### Bloom Filter logic

Answers:

> Are all positions required by this value already active?

Together they produce the Bloom Filter's membership behavior.

---

# 28. Key Takeaways

The important concepts from this document are:

1. A hash function converts a value into a deterministic numeric representation.
2. The hash value is mapped into the Bloom Filter's bit array.
3. A Bloom Filter uses multiple bit positions for each value.
4. Multiple positions provide more useful membership information than a single position.
5. Double hashing can efficiently generate multiple positions from two base hashes.
6. The hashing process must be deterministic.
7. Insertion and lookup must use exactly the same hashing strategy.
8. Good hash distribution helps spread values across the bit array.
9. Hash collisions and bit-position overlap are expected.
10. Hashing does not store or preserve the original value.
11. The number of hash functions is represented by `k`.
12. The bit-array size and `k` influence false-positive behavior.
13. Python's built-in `hash()` should not be assumed to provide stable values across independent processes.
14. A deterministic hashing approach such as `hashlib` is more appropriate for a reusable implementation.

The core idea can be reduced to:

```text
Value
  ↓
Deterministic Hashing
  ↓
Multiple Bit Positions
  ↓
Set / Check Bits
  ↓
Bloom Filter Membership Result
```

---

# 29. What Comes Next?

We now understand:

```text
Business Problem
       ↓
Why Bloom Filter
       ↓
Bit Array
       ↓
Hash Functions
```

The next important question is:

> If Bloom Filters can say "probably present", how often can they be wrong?

That leads directly to **false positives**.

The next document:

```text
05_false_positives.md
```

will explain:

* What a false positive is
* How false positives happen
* Why false negatives do not happen in a standard Bloom Filter
* How bit overlap creates false positives
* How saturation affects accuracy
* How to measure false-positive rates
* Why false positives are acceptable in many system-design use cases
* The trade-off between memory usage and accuracy
