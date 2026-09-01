"""
Go-compatible Semantic Versioning (SemVer) comparison in Python.

This module replicates the precise parsing and comparison behavior of Go's
official `golang.org/x/mod/semver` package, including the mandatory 'v' prefix,
shorthand versions (e.g. "v1", "v1.2"), pre-release precedence, and the
complete ignoring of build metadata (including "+incompatible").
"""

from typing import Tuple, Optional


class ParsedVersion:
    """Holds components of a successfully parsed Go semantic version."""

    def __init__(
        self,
        major: str = "",
        minor: str = "",
        patch: str = "",
        short: str = "",
        prerelease: str = "",
        build: str = "",
    ):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.short = short
        self.prerelease = prerelease
        self.build = build


def is_ident_char(c: str) -> bool:
    """Checks if character is allowed in a SemVer identifier."""
    return ("A" <= c <= "Z") or ("a" <= c <= "z") or ("0" <= c <= "9") or (c == "-")


def is_bad_num(v: str) -> bool:
    """Checks if a string is a numeric identifier with invalid leading zeros."""
    i = 0
    while i < len(v) and "0" <= v[i] <= "9":
        i += 1
    return i == len(v) and i > 1 and v[0] == "0"


def parse_int(v: str) -> Tuple[str, str, bool]:
    """Parses a decimal integer with no leading zeros (except single '0')."""
    if not v:
        return "", "", False
    if v[0] < "0" or "9" < v[0]:
        return "", "", False
    i = 1
    while i < len(v) and "0" <= v[i] <= "9":
        i += 1
    if v[0] == "0" and i != 1:
        return "", "", False
    return v[:i], v[i:], True


def parse_prerelease(v: str) -> Tuple[str, str, bool]:
    """Parses pre-release section starting with '-'."""
    if not v or v[0] != "-":
        return "", "", False
    i = 1
    start = 1
    while i < len(v) and v[i] != "+":
        if not is_ident_char(v[i]) and v[i] != ".":
            return "", "", False
        if v[i] == ".":
            if start == i or is_bad_num(v[start:i]):
                return "", "", False
            start = i + 1
        i += 1
    if start == i or is_bad_num(v[start:i]):
        return "", "", False
    return v[:i], v[i:], True


def parse_build(v: str) -> Tuple[str, str, bool]:
    """Parses build metadata section starting with '+'."""
    if not v or v[0] != "+":
        return "", "", False
    i = 1
    start = 1
    while i < len(v):
        if not is_ident_char(v[i]) and v[i] != ".":
            return "", "", False
        if v[i] == ".":
            if start == i:
                return "", "", False
            start = i + 1
        i += 1
    if start == i:
        return "", "", False
    return v[:i], v[i:], True


def parse(v: str) -> Tuple[Optional[ParsedVersion], bool]:
    """Parses a version string into a ParsedVersion according to Go's semver rules."""
    if not v or v[0] != "v":
        return None, False

    major, rest, ok = parse_int(v[1:])
    if not ok:
        return None, False

    if rest == "":
        return (
            ParsedVersion(
                major=major,
                minor="0",
                patch="0",
                short=".0.0",
            ),
            True,
        )

    if rest[0] != ".":
        return None, False

    minor, rest, ok = parse_int(rest[1:])
    if not ok:
        return None, False

    if rest == "":
        return (
            ParsedVersion(
                major=major,
                minor=minor,
                patch="0",
                short=".0",
            ),
            True,
        )

    if rest[0] != ".":
        return None, False

    patch, rest, ok = parse_int(rest[1:])
    if not ok:
        return None, False

    prerelease = ""
    build = ""

    if len(rest) > 0 and rest[0] == "-":
        prerelease, rest, ok = parse_prerelease(rest)
        if not ok:
            return None, False

    if len(rest) > 0 and rest[0] == "+":
        build, rest, ok = parse_build(rest)
        if not ok:
            return None, False

    if rest != "":
        return None, False

    return (
        ParsedVersion(
            major=major,
            minor=minor,
            patch=patch,
            prerelease=prerelease,
            build=build,
        ),
        True,
    )


def is_valid(v: str) -> bool:
    """Reports whether v is a valid semantic version string under Go's rules."""
    _, ok = parse(v)
    return ok


def canonical(v: str) -> str:
    """Returns the canonical formatting of the semantic version v."""
    p, ok = parse(v)
    if not ok:
        return ""
    if p.build != "":
        return v[: len(v) - len(p.build)]
    if p.short != "":
        return v + p.short
    return v


def compare_int(x: str, y: str) -> int:
    """Compares two numeric strings without converting to integers directly."""
    if x == y:
        return 0
    if len(x) < len(y):
        return -1
    if len(x) > len(y):
        return 1
    if x < y:
        return -1
    return 1


def next_ident(x: str) -> Tuple[str, str]:
    """Retrieves next identifier from pre-release string."""
    i = 0
    while i < len(x) and x[i] != ".":
        i += 1
    return x[:i], x[i:]


def is_num(v: str) -> bool:
    """Checks if identifier string consists solely of digits."""
    i = 0
    while i < len(v) and "0" <= v[i] <= "9":
        i += 1
    return i == len(v)


def compare_prerelease(x: str, y: str) -> int:
    """Compares two pre-release strings according to SemVer rules."""
    if x == y:
        return 0
    if x == "":
        return 1
    if y == "":
        return -1

    while x != "" and y != "":
        x = x[1:]  # skip '-' or '.'
        y = y[1:]  # skip '-' or '.'
        dx, x = next_ident(x)
        dy, y = next_ident(y)
        if dx != dy:
            ix = is_num(dx)
            iy = is_num(dy)
            if ix != iy:
                if ix:
                    return -1
                else:
                    return 1
            if ix:
                if len(dx) < len(dy):
                    return -1
                if len(dx) > len(dy):
                    return 1
            if dx < dy:
                return -1
            else:
                return 1

    if x == "":
        return -1
    else:
        return 1


def compare(v1: str, v2: str) -> int:
    """
    Compares two Go module version strings according to semantic version precedence.

    Returns:
       -1 if v1 is older than v2
        0 if v1 is equal to v2
        1 if v1 is newer than v2
       -4 if the first version is invalid (and second is valid)
       -8 if the second version is invalid (and first is valid)
      -12 if both versions are invalid
    """
    pv, ok1 = parse(v1)
    pw, ok2 = parse(v2)

    if not ok1 and not ok2:
        return -12
    if not ok1:
        return -4
    if not ok2:
        return -8

    # Compare major version
    c = compare_int(pv.major, pw.major)
    if c != 0:
        return c

    # Compare minor version
    c = compare_int(pv.minor, pw.minor)
    if c != 0:
        return c

    # Compare patch version
    c = compare_int(pv.patch, pw.patch)
    if c != 0:
        return c

    # Compare pre-release version
    return compare_prerelease(pv.prerelease, pw.prerelease)
