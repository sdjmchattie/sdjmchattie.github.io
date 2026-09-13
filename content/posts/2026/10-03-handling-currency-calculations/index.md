---
date: 2026-10-03
title: "Handling Currency Calculations: Why Floats Break Financial Software"
description: |-
  Discover why floating-point arithmetic is hazardous when currency accuracy is paramount.
  Explore binary float drift, statistical bias in rounding modes, the limits of integer cents, remainder allocation algorithms, and robust database storage patterns.
slug: handling-currency-calculations
image: /images/posts/2026/10-03-handling-currency-calculations.png
tags:
  - Software Pitfalls
  - Python
  - Software Architecture
---

{{< tldr >}}
Standard floating-point numbers cannot represent decimal fractions precisely, causing insidious financial drift and billing errors.
Building reliable financial software requires exact decimal arithmetic, rigorous rounding modes, and robust database types.

- **Never use floats:** Binary floats like `0.1 + 0.2` introduce precision drift that corrupts financial ledgers.
- **Use Decimal types:** Perform monetary arithmetic using Python's `decimal.Decimal` with explicit rounding contexts.
- **Select rounding modes:** Use Banker's Rounding (`ROUND_HALF_EVEN`) to eliminate cumulative statistical bias in large runs.
- **Persist exact quantities:** Store financial balances using database `NUMERIC`/`DECIMAL` types or integer minor units.
{{< /tldr >}}

When building an application, you inevitably reach a screen where money enters the picture.
You need to calculate a 20% VAT rate, split an invoice between team members, or apply a discount code at checkout.
You see a price like `£19.99` with two neat decimal digits and assume a standard floating-point variable will do just fine.

If your software handles financial transactions where accuracy is paramount, this assumption is dangerous.
Floating-point numbers were never designed for commerce, and using them to track money introduces subtle, compounding discrepancies into your ledgers.

In this guide, I examine why binary floating-point numbers fail for currency arithmetic, how standard rounding introduces systematic upward bias, and why the common advice to "just use integer cents" is an incomplete shortcut.
This post forms part of my [Software Pitfalls]({{< ref "/tags/software-pitfalls" >}}) series, following on from [Never Roll Your Own Date Maths]({{< ref "09-26-never-roll-your-own-date-maths" >}}), exploring deceptive traps hidden inside seemingly simple programming tasks.

## The Illusion of Continuous Quantities

Floating-point numbers excel in scientific computing and machine learning, where microscopic variations in the fourteenth decimal place are harmless.
Money does not work like physics; it is a discrete construct governed by strict statutory accounting standards.

In financial accounting, every single penny, cent, or yen must be accounted for exactly.
When balance sheets fail to reconcile by even one penny, automated settlement reconciliations grind to a halt.

## Where Floating-Point Arithmetic Breaks

To understand why standard floats fail for money, look at how modern computers represent numbers in hardware.

### The base-2 representation trap

Most programming languages implement floating-point numbers using the IEEE 754 double-precision standard.
In binary, numbers are stored as sums of powers of two (such as 1/2, 1/4, 1/8, and 1/16).

In base 10, fractions like 1/10 (0.1) are clean and finite.
In base 2, 1/10 is an infinitely repeating fraction, much like 1/3 is in base 10.
Computer memory truncates that sequence after 53 bits, storing a binary approximation rather than an exact tenth.

You can see the immediate consequence in your Python terminal:

```python
>>> 0.1 + 0.2
0.30000000000000004

>>> 0.1 + 0.2 == 0.3
False
```

### Compounding drift in financial ledgers

A stray `0.00000000000000004` looks harmless on an isolated arithmetic expression.
You might assume that wrapping calculations in `round(..., 2)` safely neutralises floating-point imprecision.

Unfortunately, binary representation corrupts calculations long before `round()` executes.
Consider extracting the 20% VAT element from a standard consumer shelf price of £1.11.
Two developers on the same team might write two mathematically equivalent expressions to calculate the tax:

- Developer A calculates gross minus net: `1.11 - (1.11 / 1.2)`
- Developer B uses the statutory VAT fraction: `1.11 / 6`

In pure mathematics, both expressions are identical and evaluate to exactly £0.185.
Now watch what happens when both developers run their code and round to two decimal places:

```python
gross_price = 1.11

# Developer A: gross minus net
vat_a = round(gross_price - (gross_price / 1.2), 2)

# Developer B: statutory 1/6 VAT fraction
vat_b = round(gross_price / 6, 2)

print(f"Developer A: {vat_a:.2f}")
# Developer A: 0.18

print(f"Developer B: {vat_b:.2f}")
# Developer B: 0.19

print(vat_a == vat_b)
# False
```

Even after calling `round()` on both values, their calculations disagree by a full penny.

Because binary floating-point numbers cannot represent these fractions cleanly, `1.11 - (1.11 / 1.2)` evaluates to `0.18499999999999994`, while `1.11 / 6` evaluates to `0.18500000000000003`.
The first value sits fractionally below the 0.185 midpoint and rounds down to `0.18`.
The second sits fractionally above the midpoint and rounds up to `0.19`.

If Developer A built the checkout service and Developer B built the accounting pipeline, your systems will continuously produce reconciling discrepancies across identical transactions.
Explicit rounding cannot save you when the underlying numbers are already corrupted.

## Statistical Bias and Rounding Modes

Once you avoid binary floats, a second challenge appears: choosing the correct rounding mode.
In commercial software, rounding fractional currency carries statutory and financial consequences.

### The statistical flaw in round half up

In primary school maths, you were likely taught the "round half up" rule: if the discarded fraction is 0.5 or greater, round up to the next integer.
Otherwise, round down.

At first glance, this rule appears symmetrical.
Across the ten possible trailing digits (0 through 9), five digits round down (0, 1, 2, 3, 4) and five digits round up (5, 6, 7, 8, 9).

The illusion of symmetry collapses the moment you measure the actual rounding difference: the adjustment applied to each number when rounding.
Look at what happens when you pair each downward rounding adjustment with its upward counterpart:

| Round Down | Round Up |
| :--- | :--- |
| `0.4` (`-0.4`) | `0.6` (`+0.4`) |
| `0.3` (`-0.3`) | `0.7` (`+0.3`) |
| `0.2` (`-0.2`) | `0.8` (`+0.2`) |
| `0.1` (`-0.1`) | `0.9` (`+0.1`) |
| `0.0` (`-0.0`) | `0.5` (`+0.5`) |

The negative and positive adjustments in the first four rows cancel each other out completely.
In the final row, `0.0` has zero rounding difference, leaving `0.5` completely unpartnered.

Rounding `0.5` upward injects an uncompensated `+0.5` across the ten digits, creating an average upward drift of `+0.05` per operation.
Over one million transactions, round half up systematically inflates account balances by roughly 50,000 units of currency.

### Banker's rounding to the rescue

To eliminate this statistical drift, international accounting standards, financial regulators, and the IEEE 754 standard specify [Banker's Rounding](https://en.wikipedia.org/wiki/Rounding#Round_half_to_even), formally known as **Round Half to Even**.

Under Banker's Rounding, when a number falls exactly halfway between two potential values, it rounds towards the nearest *even* number:

```python
# Python's built-in round() implements Banker's Rounding:
round(2.5)  # Evaluates to 2 (rounds down to even)
round(3.5)  # Evaluates to 4 (rounds up to even)
round(4.5)  # Evaluates to 4 (rounds down to even)
```

Because integers alternate between even and odd, `.5` rounds down half the time and up half the time.
The midpoint errors cancel out completely, eliminating statistical bias over large transaction volumes.
This is why Python's built-in `round()` and `decimal` module default to round-half-even behaviour.

Even with Banker's Rounding, single transactions inevitably produce fractional pennies that must be rounded off (such as 20% VAT on £1.99 yielding £0.398, rounded to £0.40).
If discarded fractions are left unmonitored across millions of daily items, they create reconciling discrepancies between transaction audit logs and statutory general ledgers.

## The "Just Store Cents" Fallacy

To avoid floating-point errors, popular programming advice often recommends multiplying every amount by 100 and storing cents as integers.

Payment processors like Stripe expose API amounts as integers in minor units (such as `1000` for £10.00).
However, treating integers as a universal cure-all ignores currency standards and modern pricing models.

First, not all currencies divide into 100 subunits.
Under ISO 4217, zero-decimal currencies like the Japanese Yen (`JPY`) have no minor units, while three-decimal currencies like the Kuwaiti Dinar (`KWD`) divide into 1,000 fils.
Multiplying unconditionally by 100 overcharges Japanese customers a hundredfold and corrupts Kuwaiti accounts.

Second, modern billing frequently operates below a single penny.
Cloud compute, language model tokens, and energy tariffs (such as 24.345p per kilowatt-hour) all demand fractional pence.
Storing only integer minor units prevents modelling high-volume micro-pricing without severe precision loss.

## The Allocation Problem

Rounding errors become acute when you have to divide money.
Division is an operation that almost never results in a neat two-decimal number.

### The disappearing penny

Imagine splitting an invoice of £100.00 equally across three people:

```python
total = 100.00
share = round(total / 3, 2)  # 33.33 each
```

Summing three payments of £33.33 yields £99.99, leaving your ledger short by one penny.
If you round up to £33.34, the sum becomes £100.02, creating an illegal surplus.
You cannot solve division with simple rounding because remainders must be conserved.

### Fowler's allocation algorithm

In [*Analysis Patterns*](https://www.amazon.co.uk/Analysis-Patterns-Reusable-Object-Models/dp/0201895420), Martin Fowler articulated the standard solution: the **Allocation Algorithm**.

Rather than rounding shares independently, the algorithm converts the total to minor units (10,000 pence), allocates integer shares by ratio, and distributes remainder units one by one.
For a £100.00 split three ways, the first recipient receives £33.34, while the remaining two receive £33.33.
No money is created or destroyed, and the ledger balances to the exact penny.

## Implementing the Money Pattern in Python

To protect your codebase from these pitfalls, you should represent currency as a formal Value Object rather than a raw numeric primitive.
The Money pattern encapsulates an exact numerical amount alongside its ISO 4217 currency code.

In Python, the standard library provides the `decimal` module, which offers exact decimal arithmetic and configurable rounding modes.
Here is a lightweight, immutable implementation of the Money pattern using a dataclass with built-in allocation:

```python
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN

# ISO 4217 minor unit exponents (defaults to 2 for GBP, EUR, USD, etc.)
CURRENCY_EXPONENTS = {"JPY": 0, "KWD": 3}


@dataclass(frozen=True)
class Money:
    """An immutable Money value object using exact decimal representation."""

    amount: Decimal
    currency: str = "GBP"

    def __post_init__(self) -> None:
        object.__setattr__(self, "amount", Decimal(str(self.amount)))
        object.__setattr__(self, "currency", self.currency.upper())

    def __repr__(self) -> str:
        exp = CURRENCY_EXPONENTS.get(self.currency, 2)
        return f"{self.currency} {self.amount:.{exp}f}"

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money) or self.currency != other.currency:
            other_curr = getattr(other, "currency", type(other).__name__)
            raise TypeError(f"Cannot add {self.currency} and {other_curr}")
        return Money(self.amount + other.amount, self.currency)

    def allocate(self, ratios: list[int]) -> list["Money"]:
        """Apportions money according to ratios, distributing remainders deterministically."""
        total_weight = sum(ratios)
        if total_weight <= 0:
            raise ValueError("Total ratio weight must be positive")

        factor = Decimal(10) ** CURRENCY_EXPONENTS.get(self.currency, 2)
        minor_units = int((self.amount * factor).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))
        remainder = minor_units
        shares: list[int] = []

        for weight in ratios:
            share = (minor_units * weight) // total_weight
            shares.append(share)
            remainder -= share

        # Distribute leftover minor units one by one to earliest recipients
        for i in range(remainder):
            shares[i] += 1

        return [Money(Decimal(val) / factor, self.currency) for val in shares]
```

With this class in place, you eliminate entire categories of common bugs:

```python
# 1. Currency safety: Prevents adding USD to GBP
gbp_balance = Money("100.00", "GBP")
usd_payment = Money("50.00", "USD")

# Raises TypeError: Cannot add GBP and USD
# total = gbp_balance + usd_payment

# 2. Conservation of money during splits:
invoice = Money("100.00", "GBP")
split_shares = invoice.allocate([1, 1, 1])

print(split_shares)
# Output: [GBP 33.34, GBP 33.33, GBP 33.33]

assert sum(s.amount for s in split_shares) == Decimal("100.00")
```

This design prevents accidental operations between different currencies.
Crucially, allocating across ratios guarantees that the sum of the shares always equals the original whole.

## Database Persistence and API Design

Designing a clean in-memory object model is only half the battle.
You also need to persist monetary values and expose them across API contracts without corrupting precision.

Two primary patterns dominate industry practice:

- **Arbitrary-precision columns (`NUMERIC(19, 4)` / `DECIMAL`):** The standard for PostgreSQL and MySQL. Reserving 19 digits with 4 decimal places natively handles exact arithmetic and fractional rates (such as £0.0025 per API call) directly in SQL queries.
- **Integer minor units (`BIGINT`):** Standard for public JSON APIs (such as Stripe). Storing £100.00 as `10000` minor units eliminates fractional ambiguity during serialisation, preventing clients from inadvertently parsing floats. When adopting this pattern, maintain an ISO 4217 exponent registry (such as 2 for GBP, 0 for JPY, 3 for KWD).

## Wrapping Up

When financial accuracy is paramount, floating-point arithmetic is a liability.
What seems like an innocent shortcut in development can quickly result in customer billing disputes, failed ledger reconciliations, and regulatory compliance headaches.

Whenever you design systems that calculate or store money, keep these core principles in mind:

- Never use binary floating-point types (`float`, `double`) for monetary calculations.
- Use exact decimal primitives (like Python's `Decimal`) configured with Banker's Rounding (`ROUND_HALF_EVEN`).
- Remember that cents are not universal: account for zero-decimal currencies (JPY) and sub-cent pricing models.
- Avoid simple division when splitting money; use an allocation algorithm to distribute remainder pennies deterministically.
- Encapsulate amounts and ISO 4217 codes into immutable Money objects to prevent mixing incompatible currencies.
- Store monetary data in databases as explicit `NUMERIC(19, 4)` columns or integer minor units to preserve exact precision.

Once you've calculated and stored your figures without dropping a single penny, don't stumble at the final hurdle of user presentation.
Always format currency values with their full complement of minor unit digits, ensuring trailing zeros remain visible so that £10.00 never truncates to £10 or £10.0 on an invoice.

Have you ever encountered a rounding discrepancy or currency calculation bug in production?
Take a moment to audit your billing pipelines, and ensure your ledger calculations are built on solid mathematical foundations.
