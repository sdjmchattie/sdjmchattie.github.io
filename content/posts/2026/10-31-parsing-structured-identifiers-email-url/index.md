---
date: 2026-10-31
title: "What's a URL? Please Provide Your Email Address! The Complexity of Parsing Structured Identifiers"
description: |-
  Discover why regular expressions consistently fail to validate email addresses and URLs safely.
  Explore the hidden complexities of RFC 5322, internationalised domains, path traversal sanitisation, and SSRF bypasses.
slug: parsing-structured-identifiers-email-url
image: /images/posts/2026/10-31-parsing-structured-identifiers-email-url.png
tags:
  - Software Pitfalls
  - Python
  - Security
  - Software Architecture
---

{{< tldr >}}
Structured identifiers like email addresses and URLs are not simple text strings; they are full formal grammars governed by decades of layered specifications.
Attempting to validate or sanitise them with one-off regular expressions creates severe security holes, rejects legitimate users, and risks catastrophic performance penalties.

- **Ditch regex for email validation:** Obscure RFC specifications, nested comments, and internationalised [Unicode](https://home.unicode.org/) characters break naive patterns, while catastrophic backtracking triggers [Regular Expression Denial of Service (ReDoS)](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS).
- **Verify deliverability, not grammar:** Use battle-tested parsers like [`email-validator`](https://github.com/JoshData/python-email-validator) to normalise addresses, but rely exclusively on cryptographic confirmation tokens to prove a mailbox actually exists.
- **Enforce path containment with `pathlib`:** Never sanitise directory paths using string replacement or regex; resolve canonical paths with [`pathlib.Path.resolve`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve) and verify strict boundary containment via [`is_relative_to`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.is_relative_to).
- **Defeat SSRF beyond hostname regexes:** Outbound requests must guard against [Server-Side Request Forgery (SSRF)](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery) bypasses using octal, hexadecimal, and dword integer IP representations; parse URLs with [`urllib.parse`](https://docs.python.org/3/library/urllib.parse.html) and check resolved IPs against [`ipaddress`](https://docs.python.org/3/library/ipaddress.html) ranges.
- **Normalise internationalised domains:** Protect against [homograph attacks](https://en.wikipedia.org/wiki/IDN_homograph_attack) and Unicode spoofs by converting domain names to canonical [Punycode](https://en.wikipedia.org/wiki/Punycode) via [`idna`](https://github.com/kjd/idna) ([RFC 5890](https://datatracker.ietf.org/doc/html/rfc5890)).
{{< /tldr >}}

"Please enter a valid email address."
"Please provide a valid website URL."
If you build web applications, APIs, or user interfaces, you have almost certainly written or reviewed code that displays those two demands.

Because every user recognises an email address and interacts with web links daily, developers treat them like straightforward strings.
When the need for validation arises, the default reaction is almost universal: copy a regular expression from Stack Overflow or write a quick twenty-character pattern.

I strongly recommend that you resist that temptation.
Rolling one-off regular expressions and string replacement routines for structured identifiers is one of the most reliable ways to introduce silent bugs and severe vulnerabilities into your software.

This post forms part of my ongoing [Software Pitfalls]({{< ref "/tags/software-pitfalls" >}}) series.
In this guide, I explore why emails and URLs defy simple pattern matching, how naive sanitisation creates security loopholes, and which battle-tested tools you should use instead.

## The Illusion of Simple Strings

Developers reach for regular expressions because structured identifiers appear predictable at first glance.
An email looks like a username followed by an `@` symbol and a domain name.
A web address looks like `https://` followed by a host name and an optional file path.

However, neither of these identifiers is a flat string.
Both are intricate formal grammars shaped by decades of committee drafts, historical backwards compatibility, and global localisation requirements.

When you attempt to enforce a complex grammar using a single regular expression, you invite two failure modes.
You either reject legitimate users whose addresses violate your narrow assumptions, or you admit malicious payloads that bypass your security checks.

## The Email Mirage: Decades of Layered RFCs

Email syntax is defined primarily by [RFC 5322](https://datatracker.ietf.org/doc/html/rfc5322) (which superseded [RFC 2822](https://datatracker.ietf.org/doc/html/rfc2822) and [RFC 822](https://datatracker.ietf.org/doc/html/rfc822)) for message formats, alongside [RFC 5321](https://datatracker.ietf.org/doc/html/rfc5321) for transport envelopes.
Reading these specifications reveals that what developers consider "standard" represents only a tiny slice of legal email syntax.

### Valid syntax that breaks naive regexes

Consider the regular expressions commonly found across GitHub repositories.
Most patterns resemble something like `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`.

While this pattern matches standard corporate accounts, it rejects an enormous variety of perfectly valid addresses.
Here are several examples of syntactically legal email addresses under [RFC 5322](https://datatracker.ietf.org/doc/html/rfc5322):

```text
"john doe"@example.com
user+newsletter.tag@example.co.uk
customer/department=shipping@example.com
!#$%&'*+-/=?^_`{|}~@example.com
john(comment)doe@example.com
admin@[192.168.1.1]
```

The local-part (the portion before the `@`) permits quoted strings containing whitespace, unescaped punctuation, subaddressing tags, and embedded comments in parentheses.
It even permits raw IP literals enclosed in square brackets for the domain portion.

A regular expression capable of parsing the complete [RFC 5322](https://datatracker.ietf.org/doc/html/rfc5322) specification requires recursive parsing for folding whitespace and nested comments.
In fact, a fully RFC-compliant regular expression runs to several thousand characters in length and remains virtually unmaintainable.

### Internationalised addresses and Unicode

Even if you managed to accommodate the intricacies of ASCII email syntax, modern applications operate globally.
The Email Address Internationalization (EAI) framework, defined in [RFC 6530](https://datatracker.ietf.org/doc/html/rfc6530), [RFC 6531](https://datatracker.ietf.org/doc/html/rfc6531), and [RFC 6532](https://datatracker.ietf.org/doc/html/rfc6532), extends email addresses to native [Unicode](https://home.unicode.org/) characters.

Valid email addresses can now include non-Latin scripts across both the local-part and the domain name:

```text
伊昭傑@郵件.商務
用户@例子.广告
андрей@почта.рф
dörte@müller.de
```

If your application checks emails using standard ASCII character classes, you immediately alienate hundreds of millions of international internet users.
Supporting internationalisation requires handling non-ASCII casing rules, NFKC normalisation, and bidirectional text constraints.

### The catastrophic cost of regex backtracking

When developers try to expand naive expressions to handle edge cases, they frequently introduce catastrophic backtracking.
This phenomenon forms the basis of [Regular Expression Denial of Service (ReDoS)](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS).

Consider an expression with nested repetitions, such as `^([a-zA-Z0-9]+.)+@[a-zA-Z0-9]+...`.
When an attacker supplies a long sequence of characters ending with an unexpected symbol, the regex engine explores every combinatorial permutation before rejecting the match.

A single malformed string of fifty characters can stall a Python worker thread or an event loop for several seconds.
In production, submitting a handful of these strings simultaneously exhausts your server's CPU capacity completely.

### Tested solutions for email handling

Rather than assembling custom regular expressions, delegate syntactic parsing to mature libraries.
In Python, the standard library provides [`email.headerregistry.Address`](https://docs.python.org/3/library/email.headerregistry.html#email.headerregistry.Address), while the community standard is [`email-validator`](https://github.com/JoshData/python-email-validator), which powers email validation in [`Pydantic`](https://docs.pydantic.dev/).

Here is how you validate, normalise, and inspect an email address using [`email-validator`](https://github.com/JoshData/python-email-validator):

```python
from email_validator import EmailNotValidError, validate_email


def check_and_normalise_email(raw_email: str) -> str:
    """Validate and normalise an incoming email address."""
    try:
        # Check syntax, normalise Unicode, and resolve domain encoding
        email_info = validate_email(
            raw_email,
            check_deliverability=False,  # Avoid synchronous DNS lookups in hot paths
        )
        # Return the normalised canonical form
        return email_info.normalized
    except EmailNotValidError as exc:
        raise ValueError(f"Invalid email address provided: {exc}") from exc
```

The library automatically handles quoted strings, normalises internationalised domain names to ASCII [Punycode](https://en.wikipedia.org/wiki/Punycode), and rejects ReDoS-inducing structures.

However, remember the most important architectural rule of email handling: **syntax validation is not identity verification**.
A syntactically valid address might not exist, might belong to a different user, or might bounce immediately.
The only definitive way to validate an email address is to send a cryptographically secure, time-limited confirmation token to the mailbox.

## The URL Minefield: Schemes, Traversal, and Parser Differentials

Validating URLs presents an even larger attack surface than email addresses.
URLs are defined by [RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986) and the living [WHATWG URL Standard](https://url.spec.whatwg.org/).
They combine communication schemes, authentication credentials, network hosts, port numbers, hierarchical paths, query parameters, and fragment identifiers.

When developers attempt to validate URLs with regular expressions or clean paths with string manipulation, catastrophic vulnerabilities follow.

### Directory traversal and sanitisation traps

A classic requirement in web development is serving files based on a user-supplied path parameter.
Developers often realise that allowing users to pass `../../etc/passwd` is dangerous, so they implement a quick sanitisation routine:

```python
# DANGEROUS: Do not use naive string replacement for path sanitisation
user_input = request.args.get("file")
clean_path = user_input.replace("../", "")
```

This one-off replacement is completely useless against basic evasion techniques.
If an attacker supplies `....//etc/passwd`, your single-pass `replace` strips the inner `../`, leaving behind a perfectly formed traversal payload.

Attackers also exploit URL encoding (`%2e%2e%2f`), double encoding (`%252e%252e%252f`), and Windows-style backslashes (`..\`).
Regular expressions attempting to match every traversal combination inevitably miss obscure encoding variants.

The battle-tested solution is to avoid string manipulation entirely.
Use Python's [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html) to resolve the canonical filesystem target and verify strict containment using [`is_relative_to`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.is_relative_to):

```python
from pathlib import Path


def resolve_safe_filepath(base_dir: Path, untrusted_filename: str) -> Path:
    """Safely resolve an untrusted filename within a restricted base directory."""
    # Resolve the intended sandbox directory to its absolute canonical path
    sandbox = base_dir.resolve()

    # Construct and resolve the candidate target path
    candidate = (sandbox / untrusted_filename).resolve()

    # Enforce strict boundary containment
    if not candidate.is_relative_to(sandbox):
        raise PermissionError(f"Access denied: Path traversal detected outside {sandbox}")

    return candidate
```

By resolving symlinks and normalising segments through the operating system's filesystem driver, [`pathlib.Path.resolve`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve) defeats all traversal encodings before any file handles are opened.

### SSRF and obfuscated IP representations

When an application accepts a webhook URL or fetches a preview thumbnail from user input, it must prevent [Server-Side Request Forgery (SSRF)](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery).
In an SSRF attack, a remote user coerces your backend into querying internal microservices, loopback interfaces (`127.0.0.1`), or cloud instance metadata endpoints (`169.254.169.254`).

Developers frequently defend against this with a hostname regular expression:

```python
# DANGEROUS: Regex blocklists cannot detect alternative IP encodings
regex = r"^https?://(?!localhost|127\.0\.0\.1|169\.254\.169\.254)"
```

This approach fails because network stacks support numerous alternative representations of IP addresses.
Every one of the following URLs resolves directly to loopback (`127.0.0.1`):

```text
http://2130706433/             # Integer DWORD representation
http://0177.0.0.1/             # Octal format
http://0x7f000001/             # Hexadecimal format
http://0x7f.1/                 # Mixed notation
http://[::ffff:127.0.0.1]/     # IPv4-mapped IPv6 notation
```

Similarly, an attacker targeting the AWS metadata service can submit `http://2852039166/` (the integer dword equivalent of `169.254.169.254`).
Your regex sees a harmless numeric domain and approves the request, while the underlying HTTP client resolves it directly to the cloud credentials endpoint.

To validate outbound target addresses safely, you must decompose the URL using [`urllib.parse.urlsplit`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlsplit), resolve the host via DNS, and inspect the resulting IP using Python's [`ipaddress`](https://docs.python.org/3/library/ipaddress.html) module:

```python
import ipaddress
import socket
from urllib.parse import urlsplit


def validate_outbound_url(target_url: str) -> bool:
    """Ensure an untrusted URL targets only public, routable IP destinations."""
    parsed = urlsplit(target_url)

    # Restrict schemes strictly to secure HTTP
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Unsupported scheme: {parsed.scheme}")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL is missing a valid host")

    # Resolve all IP addresses associated with the hostname
    try:
        resolved_ips = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise ValueError(f"Unable to resolve host: {hostname}") from exc

    for entry in resolved_ips:
        ip_str = entry[4][0]
        ip_obj = ipaddress.ip_address(ip_str)

        # Reject private, loopback, link-local, and reserved networks
        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_reserved
        ):
            raise PermissionError(f"Prohibited destination address: {ip_obj}")

    return True
```

This ensures that regardless of whether the input uses octal numbers, hex digits, or DNS rebinding records, your application verifies the actual IP destination before dispatching requests.

### Internationalised domain names and homograph attacks

Just like email addresses, URLs frequently incorporate [Internationalised Domain Names (IDN)](https://en.wikipedia.org/wiki/Internationalized_domain_name).
Under [RFC 5890](https://datatracker.ietf.org/doc/html/rfc5890), non-ASCII domains are encoded into ASCII-compatible strings using [Punycode](https://en.wikipedia.org/wiki/Punycode), prefixed by `xn--`.

This creates opportunities for [homograph attacks](https://en.wikipedia.org/wiki/IDN_homograph_attack).
An attacker can register a domain where one character is swapped with an identical-looking glyph from another alphabet:

```text
# Latin 'apple.com' vs Cyrillic small letter 'а' (U+0430)
latin_domain = "apple.com"
spoofed_domain = "аpple.com"

# In Punycode, their representations diverge completely:
# latin_domain   -> apple.com
# spoofed_domain -> xn--pple-43d.com
```

If you validate domains with naive string equality or regular expressions, you cannot detect these visual masquerades.
Use Python's standard [`idna`](https://github.com/kjd/idna) codec or the dedicated [`idna`](https://pypi.org/project/idna/) package to transform domains into canonical Punycode before applying blocklists or reputation checks:

```python
import idna


def get_canonical_domain(domain: str) -> str:
    """Convert an internationalised domain to its canonical Punycode representation."""
    try:
        # Converts Unicode domain into lowercase ASCII Punycode
        return idna.encode(domain, uts46=True).decode("ascii")
    except idna.IDNAError as exc:
        raise ValueError(f"Invalid internationalised domain: {exc}") from exc
```

When converted to Punycode, homograph impersonations immediately reveal their `xn--` prefix, allowing your security checks to treat them accordingly.

## Battle-Tested Patterns in Production

When designing systems that handle structured identifiers, replace ad-hoc regexes with established components across your architecture:

| Identifier Type | Naive Anti-Pattern | Security Risk | Production-Grade Pattern |
| :--- | :--- | :--- | :--- |
| **Email Address** | Giant regular expression | ReDoS; false rejections of valid RFC 5322/6530 addresses | [`email-validator`](https://github.com/JoshData/python-email-validator) + cryptographic verification link |
| **File Path** | `path.replace("../", "")` | Directory traversal via nested or encoded dots | [`pathlib.Path.resolve`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve) with [`is_relative_to`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.is_relative_to) |
| **Outbound Webhook** | Hostname regex blocklist | SSRF via octal, hex, or dword integer IP notations | [`urllib.parse`](https://docs.python.org/3/library/urllib.parse.html) + DNS resolution + [`ipaddress`](https://docs.python.org/3/library/ipaddress.html) range filtering |
| **Domain Name** | ASCII regex `[a-z0-9.-]+` | Rejection of valid IDNs; homograph spoofing | Canonical Punycode transformation via [`idna`](https://github.com/kjd/idna) |

## Wrapping Up

Structured identifiers like email addresses, URLs, and file paths look deceptive because we encounter them continuously in plain text.
It is tempting to think that a string you can type into a browser bar or a form field in five seconds can be validated in five minutes with a regular expression.

In reality, these identifiers are dense formal grammars layered with historical concessions, international character sets, and varied encoding formats.
Attempting to validate them with custom regular expressions or string replacements consistently leads to fragile user experiences and critical security vulnerabilities.

I encourage you to adopt a simple rule in your team: never write a one-off regular expression for a problem that already has an RFC and a tested package.
Use [`email-validator`](https://github.com/JoshData/python-email-validator) for email normalisation, [`pathlib`](https://docs.python.org/3/library/pathlib.html) for path containment, and [`urllib.parse`](https://docs.python.org/3/library/urllib.parse.html) with [`ipaddress`](https://docs.python.org/3/library/ipaddress.html) for network safety.

For more deep dives into subtle software bugs and architectural edge cases, explore the rest of my posts under the [Software Pitfalls]({{< ref "/tags/software-pitfalls" >}}) tag.
Until next time, let seasoned parsers do the heavy lifting so you can focus on building features that work reliably.
