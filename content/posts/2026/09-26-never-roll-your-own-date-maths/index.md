---
date: 2026-09-26
title: "Never Roll Your Own Date Maths: The Deceptive Complexity of Time"
description: |-
  Explore why calculating dates and times from scratch is a classic trap in software engineering.
  Uncover the cascading edge cases of daylight saving time, the famous Excel 1900 leap year bug, leap seconds, and why you must store Unix timestamps on disk.
slug: never-roll-your-own-date-maths
image: /images/posts/2026/09-26-never-roll-your-own-date-maths.png
tags:
  - Code Quality
  - Python
  - Software Architecture
---

At some point in every developer's career, a tempting thought arrives.
You need to add seven days to an appointment, schedule a task for tomorrow morning, or calculate the duration between two events.
You glance at your standard library, see a hefty date module, and think: "A day is just 86,400 seconds. I can write this helper function in ten lines of code."

I strongly advise you to close your text editor and step away from the keyboard.
Rolling your own date and calendar arithmetic is one of the quickest ways to introduce subtle, production-halting bugs into your codebase.

In this guide, I explore the escalating absurdities of date calculations, from daylight saving transitions and phantom leap years to geopolitical timezones and backwards-ticking clocks.
Along the way, you will see why established date libraries exist, why disk storage demands Unix timestamps, and how to keep your systems reliable.

## The Illusion of Simplicity

Date and time arithmetic appears trivial on the surface because human beings track time using neat, regular increments.
A minute has 60 seconds, an hour has 60 minutes, and a day has 24 hours.

Because these units feel like elementary arithmetic, developers often fall into the trap of using raw integer addition.
When you treat time as simple linear math, you ignore centuries of messy human history, orbital mechanics, and political interference.

Every date library you encounter looks bloated until you understand the edge cases it silently handles on your behalf.

## Where Assumptions Break Down

Consider what happens when an optimistic engineer attempts to implement date arithmetic from first principles, building one naive assumption atop another.

### 1 day != 86,400 seconds

Your first attempt at date arithmetic usually starts with scheduling an event for tomorrow at the exact same hour.
The calculation seems obvious: take the current Unix timestamp and add 86,400 seconds (24 hours multiplied by 60 minutes multiplied by 60 seconds).

```python
# The naive approach to finding "tomorrow at the same time"
SECONDS_PER_DAY = 86_400
tomorrow_timestamp = current_timestamp + SECONDS_PER_DAY
```

This code works reliably for months until the final Sunday of March or October arrives.
In regions that observe Daylight Saving Time (DST), days are not always 24 hours long.

When clocks spring forward in the spring, the day has only 23 hours.
When clocks fall back in autumn, the day stretches across 25 hours.

If you add 86,400 seconds across a spring transition, your 09:00 morning standup suddenly shifts to 10:00.
Worse, if your event was scheduled for 02:30 on the morning of a spring transition, that local time does not even exist.
The clock jumps directly from 01:59:59 to 03:00:00, creating an invalid timestamp that crashes downstream processors.

In autumn, the opposite happens: 01:30 occurs twice.
Python's standard `datetime` module includes a dedicated `fold` attribute specifically to differentiate between the first and second occurrence of an ambiguous autumn hour.
A naive integer addition has no awareness of this nuance.

### 1 year != 365 days

You might think: *"OK, so we've handled DST transitions by operating on calendar dates instead of raw seconds, but at least we know that a year is always 365 days, or 366 every four years ... right?"*

Unfortunately, the solar year does not divide neatly into Earth's rotation.
The actual solar cycle lasts roughly 365.2422 days.

To prevent calendars from drifting across the seasons, the Gregorian calendar uses a three-tier rule:
1. A year divisible by 4 is a leap year.
2. However, if that year is also divisible by 100, it is not a leap year.
3. Unless that year is also divisible by 400, in which case it remains a leap year.

This means the year 2000 was a leap year, but 1900 was not, and 2100 will not be.
If your homegrown date code relies solely on `year % 4 == 0`, your calendar will desynchronise every century.

Even more entertaining is how this exact oversight became embedded in the world's most ubiquitous spreadsheet software.
Back in 1983, the groundbreaking spreadsheet programme Lotus 1-2-3 stored dates as serial integers starting with day 1 on 1 January 1900.
However, the developers of Lotus 1-2-3 made an error: they coded 1900 as a leap year, creating a fictitious date for 29 February 1900.

When Microsoft created Excel, Lotus 1-2-3 dominated the PC spreadsheet market.
To ensure full file compatibility with existing Lotus worksheets, Microsoft intentionally replicated the bug.

```text
Excel Serial Date 59:  28 February 1900
Excel Serial Date 60:  29 February 1900  <-- A date that never occurred in history!
Excel Serial Date 61:  01 March 1900
```

To this day, Microsoft Excel still treats 1900 as a leap year.
Every serial date in Excel after 28 February 1900 is offset by one day compared to astronomical reality.

The situation grew even stranger when Microsoft released Excel for the Macintosh.
To avoid the 1900 leap year bug and align with the original Mac OS epoch, Mac Excel adopted the 1904 date system, where day 1 starts on 2 January 1904.
If you ever copy unformatted date serials between older Mac and Windows spreadsheets, your dates will mysteriously jump by four years and one day (exactly 1,462 days).

### 1 month is not a duration

You might think: *"OK, so we've handled Gregorian leap years and Excel's ghost date, but at least we know that 'one month' is a reliable calendar offset ... right?"*

A month is not a duration of time; it is a symbolic calendar coordinate.
A true duration, such as 3,600 seconds or two hours, exists independently of context and can be measured anywhere in the universe.

In contrast, a month has no standalone length.
Does "one month" mean 28, 29, 30, or 31 days?
Does it mean 2,419,200 seconds or 2,678,400 seconds?
You cannot answer that question without knowing the specific starting date and calendar year.

In fact, a week is the largest unit of time that possesses an unambiguous, fixed duration (exactly seven days, or 604,800 seconds).
The moment you step higher into months or years, fixed durations cease to exist.

This design reality explains why Python's standard `timedelta` tops out at `weeks`, deliberately omitting `months` and `years`:

```python
from datetime import timedelta

# A week is the largest unit supported by timedelta:
delta = timedelta(weeks=2, days=3)

# Python rejects this because a month has no fixed duration:
delta = timedelta(months=1)  # TypeError: 'months' is an invalid keyword argument
```

Because a month is a relational coordinate shift rather than a physical duration, calendar arithmetic is neither linear, commutative, nor reversible.
Consider a subscription billing service where an invoice recurs on the final day of each month.

If a user signs up on 31 January, what date should their next invoice arrive?
February has only 28 days (or 29 in a leap year).

If your algorithm clamps the date to 28 February, what happens when you add another month for March?
Does the next invoice run on 28 March or 31 March?
If it runs on 28 March, your customer has permanently lost three days of their billing cycle.

Even worse, calendar arithmetic breaks basic mathematical reversibility:

```python
# Conceptual calendar arithmetic
start_date = "2026-01-31"
plus_one_month = "2026-02-28"  # Clamped to end of month
minus_one_month = "2026-01-28"  # Subtracting one month from 28 Feb
```

By adding one month and then subtracting one month, you did not return to 31 January; you landed on 28 January.
A proper calendar library handles this through explicit policies, such as end-of-month pinning or relative delta calculations.

### Timezones move

You might think: *"OK, so we've handled calendar arithmetic and month clamping, but at least we know that timezones are fixed geographical offsets ... right?"*

Timezones are legal and political declarations rather than scientific coordinates.
Governments change their timezone definitions, offsets, and DST start dates on remarkably short notice.

In December 2011, the island nation of Samoa decided to realign its trading relationships with Australia and New Zealand.
To accomplish this, Samoa jumped west across the International Date Line.
The country went to sleep on Thursday, 29 December 2011, and woke up on Saturday, 31 December 2011.
In Samoa, Friday, 30 December 2011 never occurred.

If your bespoke date engine attempted to calculate payroll for a Samoan employee that week, an unguided daily loop would have failed or double-counted hours.

Other political surprises occur regularly:
- Nepal operates at UTC+05:45, Chatham Islands operates at UTC+12:45, and Newfoundland sits at UTC-03:30.
- In March 2023, the Lebanese government announced a postponement of daylight saving time with only two days of notice, creating a temporary dual-timezone crisis where airlines, telecoms, and citizens operated on conflicting clocks.
- Countries frequently abolish or reinstate DST on months or weeks of notice.

This volatility is why the Internet Assigned Numbers Authority (IANA) maintains the Time Zone Database (commonly referred to as `tzdata` or the Olson database).
Maintained by a global community of volunteers, this database releases multiple emergency updates each year to ensure your servers recognise shifting local laws.

### 1 minute != 60 seconds

You might think: *"OK, so we've handled geopolitics and dynamic timezone databases, but at least we know that a minute is always exactly 60 seconds ... right?"*

Astronomical reality once again disagrees with basic arithmetic.
Earth's rotation is not a precision timepiece; tidal friction from oceans and shifting molten rock in Earth's core cause planetary rotation to fluctuate and gradually slow down.

Meanwhile, the official scientific definition of a second is measured with atomic clocks using the vibrations of caesium-133 atoms.
Because atomic clocks keep perfect time while the Earth wobbles, solar time and atomic time slowly drift apart.

To prevent solar noon from drifting away from 12:00:00, the International Earth Rotation and Reference Systems Service (IERS) introduces occasional leap seconds.
When a leap second is decreed on 30 June or 31 December, an extra second is inserted into the day: `23:59:60`.

```text
23:59:58 UTC
23:59:59 UTC
23:59:60 UTC  <-- The 61st second of the minute
00:00:00 UTC
```

If your home-rolled date validator assumes `0 <= second < 60`, your code rejects this timestamp as corrupt.
In fact, Python's standard `datetime.time` object explicitly enforces a range of `0..59` for seconds, making it impossible to represent `23:59:60` natively.

The real-world fallout from leap seconds has been catastrophic for software.
In 2012 and 2015, leap seconds triggered widespread outages across major platforms including Reddit, Mozilla, Yelp, and Qantas airlines.
Linux servers suffered a notorious kernel deadlock in the `futex` subsystem, spinning CPU cores to 100% utilisation simultaneously across global datacentres.

To prevent these disasters, major cloud providers like Google, AWS, and Cloudflare developed "leap smearing".
Instead of inserting a sudden 61st second, their NTP servers slow down clock ticks by a fraction of a percent across a 24-hour window, gently absorbing the extra second without applications noticing.
The operational headache proved so severe that in 2022, international metrology bodies voted to phase out leap seconds entirely by 2035.

### System time jumps around

You might think: *"OK, so we've handled 61-second minutes and leap smearing, but at least we know that time always moves forward ... right?"*

If you are measuring code performance or calculating job duration, you might be tempted to capture start and end points using the system wall clock:

```python
import time

start_time = time.time()
perform_expensive_task()
elapsed = time.time() - start_time
```

This code contains a critical flaw.
System wall clocks synchronise with external time sources across the internet using the Network Time Protocol (NTP).

If your server's clock drifts ahead and NTP issues a correction, the system clock can jump backwards.
When that occurs during your task, `elapsed` evaluates to a negative number.
If that value is fed into an exponential backoff retry loop or a timeout check, your application can freeze indefinitely.

To measure durations safely, you must always use a monotonic clock:

```python
import time

# Monotonic clocks never jump backwards, regardless of NTP adjustments
start_time = time.monotonic()
perform_expensive_task()
elapsed = time.monotonic() - start_time
```

Python's `time.monotonic()`, JavaScript's `performance.now()`, and Go's `time.Now()` all provide monotonic guarantees designed specifically for duration measurements.

## Timestamps on Disk

When persisting timestamps to a database, disk file, or message queue, developers often store human-readable strings.
This introduces immediate ambiguity because date conventions vary wildly across locales:

```text
04/05/2026
```

In the United Kingdom and Europe, this string represents 4 May 2026.
In the United States, it represents 5 April 2026.

If a server processes these strings under a different locale configuration than the client that produced them, your data suffers silent, catastrophic corruption.
Even standard strings without timezone offsets (such as `"2026-05-04 14:30:00"`) lose their meaning the moment your infrastructure migrates across regions.

To guarantee reliability, follow these foundational storage rules:

- **Store Unix epoch timestamps or strict UTC ISO 8601 strings**: Persist time on disk as integer or floating-point seconds since the Unix epoch (1 January 1970 UTC), or as an explicit ISO 8601 string with a trailing `Z` offset (`2026-05-04T14:30:00Z`).
The `Z` stands for "Zulu time", borrowed from maritime and aviation communication where the zero-meridian UTC offset (`+00:00`) was designated with the letter Z.
Omitting the `Z` creates a "naive" timestamp with no timezone metadata, forcing databases and client browsers to guess the local offset and inviting silent corruption.
- **Convert only at the user boundary**: Treat timezones purely as a presentation-layer concern. Your database and backend pipelines should operate exclusively in UTC, transforming to local wall time only when rendering the interface for a human reader.
- **The future scheduling exception**: There is one important caveat to the UTC rule. If a user schedules an appointment for "09:00 AM in London" a year in advance, do not store that future event as a converted UTC timestamp. If the British government alters DST legislation before that date arrives, your stored UTC timestamp will fire an hour early or late. For future recurring events, store the local wall time alongside the IANA timezone string (`Europe/London`).

## Battle-Tested Libraries

Rather than re-inventing calendar arithmetic, rely on mature libraries that incorporate decades of edge-case handling:

In Python, combine the standard library's `zoneinfo` module (introduced in Python 3.9) with `dateutil.relativedelta`:

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta

# Explicit, timezone-aware datetime
london_tz = ZoneInfo("Europe/London")
meeting_time = datetime(2026, 3, 28, 9, 0, tzinfo=london_tz)

# Calendar addition that preserves 09:00 local time across DST
next_week = meeting_time + relativedelta(weeks=1)

# Month addition that clamps differing month lengths automatically
next_month = meeting_time + relativedelta(months=1)
```

You might wonder how `relativedelta` handles month arithmetic when earlier I explained that a month is not a duration.
The answer lies in how `relativedelta` works: it is not an isolated duration of seconds, but an **anchor-aware calendar transformation rule**.

When you apply `relativedelta(months=1)` to 31 January, it does not add an arbitrary number of days.
Instead, it resolves the target month in the Gregorian calendar, recognises that February has only 28 days (or 29 in a leap year), and automatically clamps the date to the last valid day of that month (`2026-02-28`).
Crucially, when combined with `ZoneInfo`, it preserves the intended 09:00 local wall time across the spring DST transition, automatically shifting the underlying UTC offset from `+00:00` to `+01:00`.

However, notice that even specialised libraries cannot make calendar maths reversible.
If you subtract one month from that resulting date (`datetime(2026, 2, 28) - relativedelta(months=1)`), you will land on 28 January, not 31 January.
The library provides convenient month deltas, but because end-of-month clamping inherently discards information, reversible arithmetic over month deltas remains mathematically impossible.

In modern JavaScript and TypeScript environments, the standard `Temporal` API replaces the legacy `Date` object with immutable, timezone-aware primitives (`Temporal.ZonedDateTime` and `Temporal.PlainDate`).

## The Year 2038 Problem

Even if you follow best practice and store Unix timestamps, there is a legendary elephant in the room: the Year 2038 problem, often dubbed the "Epochalypse".

Historically, Unix systems represented timestamps as signed 32-bit integers counting seconds since 1 January 1970 UTC.
A signed 32-bit integer maxes out at a value of 2,147,483,647.
At precisely 03:14:07 UTC on Tuesday, 19 January 2038, that counter runs out of positive numbers.

One second later, the integer overflows into the negatives, snapping clocks backwards to 20:45:52 UTC on 13 December 1901.
Any software reliant on 32-bit signed timestamps will suddenly believe that the current moment occurred over a century ago.

With only twelve years remaining until the 2038 boundary, software engineering faces an impending audit.
The theoretical fix is straightforward: migrate timestamp storage to 64-bit integers.
A 64-bit integer will not overflow for roughly 292 billion years, easily outlasting the solar system.

Most modern 64-bit operating systems and programming languages already use 64-bit integers for timestamps by default.
The true danger over the next twelve years lurks in legacy infrastructure: 32-bit embedded systems, industrial controllers, automotive microcontrollers, and older database schemas where timestamps were created as 32-bit `INT` columns instead of `BIGINT`.
Preparing for 2038 requires auditing database migrations, inspecting binary network protocols, and replacing ageing hardware before the epoch counter rolls over.

## Wrapping Up

Date and time arithmetic remains one of software engineering's greatest deceptive traps.
What begins as simple multiplication quickly entangles your software with astronomical physics, centuries of calendar reform, political decrees, and spreadsheet legacy bugs.

Whenever you feel the temptation to write custom date helpers, remember these principles:

- Never assume a day has 86,400 seconds; daylight saving transitions make days variable in length.
- Never assume a minute always has 60 seconds; astronomical leap seconds can insert a 61st second (or require cloud leap smearing).
- Store timestamps on disk as Unix epoch seconds or unambiguous UTC strings, never as locale-dependent text.
- Ensure your timestamp columns use 64-bit integers so your data survives the Year 2038 rollover.
- Use monotonic clocks for performance benchmarking and elapsed intervals to guard against NTP time reversals.
- Lean on battle-tested libraries like Python's `zoneinfo` and `dateutil` to navigate real-world calendar quirks.

Have you ever encountered a memorable date or timezone outage in production?
Take a look at your existing time-handling code, and make sure your systems are protected from the traps of calendar maths.
