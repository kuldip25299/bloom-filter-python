# How a Bloom Filter Works

A Bloom Filter looks simple from the outside:

> Give it a value, and it tells you whether the value is **definitely not present** or **probably present**.

But to understand why this works, we need to understand what is happening internally.

A standard Bloom Filter is built from two main components:

1. A **bit array**
2. Multiple **hash functions**

The combination of these two components allows a Bloom Filter to store membership information using very little memory.

---

## 1. The Basic Structure

A Bloom Filter can be visualized as a fixed-size array of bits.

For example, suppose we create a Bloom Filter with 10 bits:

```text
Index:  0 1 2 3 4 5 6 7 8 9
        -----------------------
Bits:   0 0 0 0 0 0 0 0 0 0
```

Initially, every bit is `0`.

When we add a value to the Bloom Filter, the value is passed through multiple hash functions.

Each hash function produces a position in the bit array.

Those positions are changed from `0` to `1`.

For example:

```text
Before:

Index:  0 1 2 3 4 5 6 7 8 9
        -----------------------
Bits:   0 0 0 0 0 0 0 0 0 0


Add "apple"

Hash functions produce:

h1("apple") -> 2
h2("apple") -> 5
h3("apple") -> 8


After:

Index:  0 1 2 3 4 5 6 7 8 9
        -----------------------
Bits:   0 0 1 0 0 1 0 0 1 0
```

The Bloom Filter does **not** store the string `"apple"`.

It only records that certain positions in the bit array have been set.

That is one of the reasons Bloom Filters can use significantly less memory than storing the complete values.

---

# 2. Why Use Bits?

A normal Python `set` stores the actual values.

For example:

```python
users = {
    "alice",
    "bob",
    "charlie",
    "david"
}
```

The set needs to retain information about each complete value.

A Bloom Filter takes a different approach.

It does not need to remember:

```text
alice
bob
charlie
david
```

Instead, it only needs to remember which bits have been turned on.

For example:

```text
0001011000100101...
```

Each position contains only:

```text
0
```

or:

```text
1
```

This makes the underlying storage extremely compact.

The trade-off is important:

> A Bloom Filter saves memory by giving up exact membership information.

It remembers enough information to prove that something is **not present**, but not enough information to prove that something is **definitely present**.

---

# 3. Understanding the Bit Array

The bit array is the core storage structure of a Bloom Filter.

Suppose we have:

```text
m = 16 bits
```

The initial state is:

```text
Index:

 0  1  2  3  4  5  6  7
 -------------------------
 0  0  0  0  0  0  0  0

 8  9 10 11 12 13 14 15
 -------------------------
 0  0  0  0  0  0  0  0
```

Each bit represents a possible position.

A value is mapped to one or more of these positions using hash functions.

For example:

```text
"apple"

hash 1 -> 3
hash 2 -> 7
hash 3 -> 12
```

The Bloom Filter changes:

```text
bit[3]  = 1
bit[7]  = 1
bit[12] = 1
```

The array becomes:

```text
Index:

 0  1  2  3  4  5  6  7
 -------------------------
 0  0  0  1  0  0  0  1

 8  9 10 11 12 13 14 15
 -------------------------
 0  0  0  0  1  0  0  0
```

The Bloom Filter now contains the membership information for `"apple"`.

But it does not contain `"apple"` itself.

---

# 4. Why Do We Need Hash Functions?

The Bloom Filter needs a deterministic way to map an arbitrary value to positions in the bit array.

This is the job of hash functions.

A hash function takes an input such as:

```text
apple
```

and produces a number.

Conceptually:

```text
hash("apple") -> 123456789
```

The Bloom Filter then converts that number into a valid bit-array position.

For example:

```text
position = hash("apple") % 16
```

If the result is:

```text
3
```

then:

```text
bit[3] = 1
```

A Bloom Filter normally uses multiple hash positions for each value.

Conceptually:

```text
apple
  |
  +---- hash 1 ----> position 3
  |
  +---- hash 2 ----> position 7
  |
  +---- hash 3 ----> position 12
```

Therefore, one value sets multiple bits.

---

# 5. Why Multiple Hash Functions?

Using multiple hash positions is one of the most important ideas behind a Bloom Filter.

Suppose we used only one hash position.

For example:

```text
apple -> bit 3
```

Then:

```text
banana -> bit 3
```

could easily create ambiguity.

We would have very little information about the value.

With multiple positions:

```text
apple

hash 1 -> 3
hash 2 -> 7
hash 3 -> 12
```

we record a combination:

```text
3, 7, 12
```

Another value might produce:

```text
banana

hash 1 -> 2
hash 2 -> 7
hash 3 -> 14
```

The Bloom Filter now contains:

```text
apple  -> 3, 7, 12
banana -> 2, 7, 14
```

Notice that both values use bit `7`.

That is completely normal.

The important point is that each value is represented by a combination of bit positions.

---

# 6. Adding an Item

Let's walk through insertion step by step.

Suppose our Bloom Filter has:

```text
10 bits
3 hash functions
```

Initial state:

```text
Index:  0 1 2 3 4 5 6 7 8 9
Bits:   0 0 0 0 0 0 0 0 0 0
```

We add:

```text
"apple"
```

Assume the three hash functions produce:

```text
hash1("apple") -> 2
hash2("apple") -> 5
hash3("apple") -> 8
```

We set those bits:

```text
bit[2] = 1
bit[5] = 1
bit[8] = 1
```

Result:

```text
Index:  0 1 2 3 4 5 6 7 8 9
Bits:   0 0 1 0 0 1 0 0 1 0
```

That is all the Bloom Filter needs to do during insertion.

Conceptually:

```text
for each hash function:
    calculate position
    set that bit to 1
```

---

# 7. Adding Another Item

Now add:

```text
"banana"
```

Assume:

```text
hash1("banana") -> 1
hash2("banana") -> 5
hash3("banana") -> 7
```

Before insertion:

```text
Index:  0 1 2 3 4 5 6 7 8 9
Bits:   0 0 1 0 0 1 0 0 1 0
```

Set positions:

```text
1
5
7
```

After insertion:

```text
Index:  0 1 2 3 4 5 6 7 8 9
Bits:   0 1 1 0 0 1 0 1 1 0
```

Notice something important:

```text
bit[5]
```

was already `1`.

Adding another value does not change it.

It remains:

```text
1
```

This means multiple values can share the same bit.

The Bloom Filter does not keep track of which value originally set that bit.

---

# 8. Bit Collisions Are Normal

As more values are added, more values will map to the same bit positions.

For example:

```text
apple  -> 2, 5, 8
banana -> 1, 5, 7
orange -> 2, 4, 8
```

Several values share positions.

The resulting array might look like:

```text
Index:  0 1 2 3 4 5 6 7 8 9
Bits:   0 1 1 0 1 1 0 1 1 0
```

This is expected behavior.

A Bloom Filter is intentionally designed to allow this kind of overlap.

The important consequence is:

> Once a bit becomes `1`, the Bloom Filter cannot tell which item caused it to become `1`.

That loss of information is what eventually makes false positives possible.

The details of false positives will be covered separately in `05_false_positives.md`.

---

# 9. Checking Whether an Item Exists

Insertion is only half of the Bloom Filter.

The more important operation is membership checking.

Suppose we want to check:

```text
"apple"
```

We run the same hash functions:

```text
hash1("apple") -> 2
hash2("apple") -> 5
hash3("apple") -> 8
```

Now we inspect:

```text
bit[2]
bit[5]
bit[8]
```

Suppose the current Bloom Filter is:

```text
Index:  0 1 2 3 4 5 6 7 8 9
Bits:   0 1 1 0 1 1 0 1 1 0
```

We get:

```text
bit[2] = 1
bit[5] = 1
bit[8] = 1
```

All required bits are `1`.

Therefore, the Bloom Filter says:

```text
Probably present
```

It does **not** say:

```text
Definitely present
```

This distinction is fundamental.

---

# 10. What Happens If One Bit Is Zero?

Now suppose we check:

```text
"grape"
```

Assume its hash functions produce:

```text
hash1("grape") -> 2
hash2("grape") -> 4
hash3("grape") -> 6
```

Our current Bloom Filter is:

```text
Index:  0 1 2 3 4 5 6 7 8 9
Bits:   0 1 1 0 1 1 0 1 1 0
```

Check the required positions:

```text
bit[2] = 1
bit[4] = 1
bit[6] = 0
```

One of the required bits is `0`.

Therefore:

```text
"grape" is definitely not present
```

Why can we be certain?

Because adding `"grape"` would have set:

```text
bit[6] = 1
```

If the bit is still `0`, then `"grape"` could not have been inserted into this Bloom Filter.

This gives us the most important rule:

> **If any required bit is `0`, the value is definitely not present.**

---

# 11. The Core Membership Rule

The entire membership-checking logic can be summarized as:

```text
Calculate all hash positions
            |
            v
      Check each bit
            |
      +-----+-----+
      |           |
    Any 0       All 1
      |           |
      v           v
Definitely     Probably
not present    present
```

In logical terms:

```text
ANY required bit = 0
        |
        v
Definitely not present
```

Whereas:

```text
ALL required bits = 1
        |
        v
Probably present
```

This is the fundamental behavior of a standard Bloom Filter.

---

# 12. Why Can't We Say "Definitely Present"?

This is where Bloom Filters differ from exact data structures such as Python `set`.

Suppose the Bloom Filter contains:

```text
apple
banana
orange
```

After several insertions, many bits may be set to `1`.

Now suppose `"grape"` was never inserted.

It is still possible that the hash functions for `"grape"` point to positions that are already `1` because other values set them.

For example:

```text
apple  -> 2, 5, 8
banana -> 1, 5, 7
orange -> 2, 4, 8
```

Now `"grape"` might produce:

```text
grape -> 2, 4, 8
```

Those bits are all already `1`.

The Bloom Filter sees:

```text
2 -> 1
4 -> 1
8 -> 1
```

So it must return:

```text
Probably present
```

even though `"grape"` was never inserted.

This is a **false positive**.

The important point is that the Bloom Filter is not making a random guess.

The answer is a direct consequence of information that has been compressed into the bit array.

---

# 13. Insertion and Lookup Use the Same Hashing Process

One critical requirement is that insertion and lookup must use the same hashing strategy.

When inserting:

```text
apple
```

we calculate:

```text
hash1 -> position A
hash2 -> position B
hash3 -> position C
```

and set those bits.

Later, when checking `"apple"`, we must calculate the same positions:

```text
hash1 -> position A
hash2 -> position B
hash3 -> position C
```

Then we check those bits.

Conceptually:

```text
INSERT

"apple"
   |
   +--> hash1 --> bit 2 = 1
   +--> hash2 --> bit 5 = 1
   +--> hash3 --> bit 8 = 1


LOOKUP

"apple"
   |
   +--> hash1 --> bit 2
   +--> hash2 --> bit 5
   +--> hash3 --> bit 8
                  |
                  v
             check bits
```

If the hashing strategy changes between insertion and lookup, the Bloom Filter will no longer behave correctly.

---

# 14. A Complete Small Example

Let's put everything together.

Suppose we have:

```text
Bit array size = 12
Number of hash functions = 3
```

Initial state:

```text
Index:
0 1 2 3 4 5 6 7 8 9 10 11

Bits:
0 0 0 0 0 0 0 0 0 0  0  0
```

## Add "cat"

Assume:

```text
cat -> 2, 5, 9
```

Set:

```text
bit[2] = 1
bit[5] = 1
bit[9] = 1
```

State:

```text
0 0 1 0 0 1 0 0 0 1 0 0
```

---

## Add "dog"

Assume:

```text
dog -> 1, 5, 8
```

State becomes:

```text
0 1 1 0 0 1 0 0 1 1 0 0
```

Notice:

```text
bit[5]
```

was already `1`.

---

## Check "cat"

Hashes:

```text
cat -> 2, 5, 9
```

Bits:

```text
bit[2] = 1
bit[5] = 1
bit[9] = 1
```

All are `1`.

Result:

```text
Probably present
```

---

## Check "bird"

Assume:

```text
bird -> 2, 6, 9
```

Bits:

```text
bit[2] = 1
bit[6] = 0
bit[9] = 1
```

One bit is `0`.

Result:

```text
Definitely not present
```

---

## Check "fish"

Assume:

```text
fish -> 1, 5, 8
```

All three bits are `1`.

Result:

```text
Probably present
```

But perhaps `"fish"` was never added.

This is a possible false positive.

---

# 15. The Important Mental Model

A useful way to think about a Bloom Filter is as a **one-way information filter**.

When adding a value:

```text
Value
  |
  v
Hash functions
  |
  v
Bit positions
  |
  v
Set bits to 1
```

The Bloom Filter remembers:

```text
Some bits associated with this value are now ON.
```

It does not remember:

```text
This exact value owns these bits.
```

That distinction is critical.

Because the Bloom Filter only records bits, it loses the relationship between:

```text
value -> exact stored record
```

This is why it cannot provide exact membership confirmation.

---

# 16. Why Bits Never Go Back to Zero

In a standard Bloom Filter, insertion only performs:

```text
0 -> 1
```

It does not normally perform:

```text
1 -> 0
```

Suppose:

```text
bit[5] = 1
```

because `"apple"` uses it.

Later, `"banana"` also uses bit `5`.

The bit remains:

```text
1
```

If we simply changed it back to:

```text
0
```

when `"apple"` was removed, we could accidentally break `"banana"`.

We would not know whether another value was still depending on that bit.

This is why standard Bloom Filters do not support straightforward deletion.

More advanced structures, such as **Counting Bloom Filters**, can support deletion by storing counters instead of simple bits.

That is outside the scope of the basic implementation in this repository.

---

# 17. Hash Collisions vs Bit Overlap

There are two concepts that are useful to distinguish.

### Hash collision

A hash function can produce the same hash output for two different values.

For example:

```text
hash("apple")  -> 123
hash("orange") -> 123
```

This is a hash collision.

### Bit-position overlap

Even when hash outputs are different, they can map to the same bit position after reducing them to the Bloom Filter size.

For example:

```text
hash result A -> 123
hash result B -> 135
```

With a bit array of size `10`:

```text
123 % 10 = 3
135 % 10 = 5
```

These do not overlap.

But if:

```text
hash result A -> 123
hash result B -> 133
```

then:

```text
123 % 10 = 3
133 % 10 = 3
```

Both values use:

```text
bit[3]
```

This kind of overlap is normal and is an expected part of Bloom Filter behavior.

---

# 18. Why the Bit Array Size Matters

Suppose we have only:

```text
10 bits
```

but insert:

```text
1,000,000 values
```

Eventually, most or all bits will become:

```text
1
```

If almost every bit is already `1`, then almost every new lookup will find all of its required positions set.

The Bloom Filter will therefore return:

```text
Probably present
```

very frequently.

At that point, it stops being useful for filtering negative lookups.

This gives us an important system-design principle:

> A Bloom Filter needs an appropriate relationship between the number of stored items, bit-array size, and number of hash functions.

Memory sizing and choosing these parameters will be covered in:

```text
06_memory_and_sizing.md
```

We do not need the mathematical formulas yet.

The important idea for now is:

```text
More items
    +
Too few bits
    =
More overlap
    =
More false positives
```

---

# 19. Time Complexity Intuition

Suppose the Bloom Filter uses:

```text
k hash functions
```

For insertion, we calculate:

```text
k hash positions
```

and set:

```text
k bits
```

For lookup, we calculate:

```text
k hash positions
```

and check:

```text
k bits
```

So the amount of work is primarily related to the number of hash functions.

Conceptually:

```text
Insert  -> O(k)
Lookup  -> O(k)
```

Since `k` is normally a relatively small fixed number, Bloom Filter operations are effectively constant-time for a configured filter.

The important scalability advantage is not only CPU time.

The larger benefit can be:

> A very cheap in-memory operation can prevent a much more expensive downstream operation.

---

# 20. Bloom Filter Data Flow

The complete process can now be represented as:

```text
                    INSERT
                       |
                       v
                    Value
                       |
                       v
               Hash Functions
                       |
             +---------+---------+
             |         |         |
             v         v         v
           Bit A     Bit B     Bit C
             |         |         |
             +---------+---------+
                       |
                       v
                Set bits to 1
```

For lookup:

```text
                    LOOKUP
                       |
                       v
                    Value
                       |
                       v
               Hash Functions
                       |
             +---------+---------+
             |         |         |
             v         v         v
           Bit A     Bit B     Bit C
             |         |         |
             +---------+---------+
                       |
                       v
                 Check all bits
                       |
              +--------+--------+
              |                 |
           Any bit 0         All bits 1
              |                 |
              v                 v
       Definitely NOT       Probably YES
```

This is essentially the entire Bloom Filter algorithm.

---

# 21. The Key Insight

The most important thing to understand is that a Bloom Filter is **not storing values**.

It is storing a compressed representation of membership.

For every inserted value:

```text
value
  ↓
hashes
  ↓
bit positions
  ↓
set bits
```

For every lookup:

```text
value
  ↓
same hashes
  ↓
same bit positions
  ↓
check bits
```

Then:

```text
Any required bit is 0
        ↓
Definitely not present
```

or:

```text
All required bits are 1
        ↓
Probably present
```

That simple rule is the foundation of the entire data structure.

---

# 22. What We Have Learned

At this point, we can describe a standard Bloom Filter using a few simple statements:

1. It uses a fixed-size **bit array**.
2. Initially, every bit is `0`.
3. Each value is processed by multiple **hash functions**.
4. Each hash produces a position in the bit array.
5. Adding a value sets those positions to `1`.
6. A lookup calculates the same positions.
7. If any required bit is `0`, the value is **definitely not present**.
8. If all required bits are `1`, the value is **probably present**.
9. Multiple values can share the same bits.
10. Shared bits can produce **false positives**.
11. A standard Bloom Filter does not produce false negatives as long as it is used correctly.
12. The bit array does not store the original values.
13. Standard Bloom Filters are not designed for straightforward deletion.

The central idea can therefore be summarized as:

> **A Bloom Filter uses a small amount of memory to remember enough information to quickly prove that many values are not present.**

---

# 23. What Comes Next?

We now understand the core mechanism:

```text
Bit Array
    +
Hash Functions
    +
Set Bits
    +
Check Bits
```

The next question is:

> How do we choose and generate the hash positions reliably?

Different hashing strategies can affect implementation, distribution, performance, and false-positive behavior.

The next document:

```text
04_hash_functions.md
```

will go deeper into hash functions, deterministic hashing, generating multiple positions, and the approach used by this repository's implementation.
