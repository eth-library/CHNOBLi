"""
Lookup-table checks applied to one person span after tagging.

The detail model has no title label, so offices, courtesy titles and
company suffixes land in the name slots. These rules move the obvious
cases out of the name, or drop the span, before the name is queried.
"""

import re
import unicodedata
from dataclasses import dataclass, field

_HYPHEN_INITIALS = re.compile(r"^([A-Za-zÄÖÜäöü])-([A-Za-zÄÖÜäöü])\.?$")
_GENITIVE_S = re.compile(r"^(.+[a-zäöüéèàáâêëïîôùû])S$")

# Folded forms. Lookup uses normalize(), which strips accents.
TITLES = frozenset(
    {
        "herr",
        "herrn",
        "frau",
        "fraulein",
        "graf",
        "grafen",
        "grafin",
        "freiherr",
        "freyherr",
        "baron",
        "comte",
        "comtesse",
        "marquis",
        "prince",
        "princesse",
        "herzog",
        "lord",
        "marchese",
        "monsieur",
        "monfieur",
        "messieurs",
        "meflieurs",
        "madame",
        "abbe",
        "labbe",
        "hr",
        "hrn",
        "hru",
        "hm",
        "mr",
        "mme",
        "mrs",
        "dr",
        "prof",
        "m",
        "mu",
    }
)

OFFICES = frozenset(
    {
        "pfarrer",
        "pfr",
        "pf",
        "pasteur",
        "pafteur",
        "pfarrherr",
        "pfarherr",
        "diakon",
        "prediger",
        "hauptmann",
        "hnupkmann",
        "baillif",
        "ballif",
        "seigneur",
        "landvogt",
        "sekretar",
        "secretaire",
        "capitaine",
        "lieutenant",
        "major",
        "obrist",
        "prasident",
        "prefident",
        "abt",
        "doktor",
        "docteur",
        "dodeur",
        "professor",
        "professeur",
        "negt",
        "negociant",
        "rathsmeister",
        "rathsmeifier",
        "zunftmeister",
        "oberstzunftmeister",
        "oberstzunftmeifter",
        "generalkommissar",
    }
)

LEGAL_FORMS = frozenset(
    {
        "ag",
        "gmbh",
        "mbh",
        "sarl",
        "sa",
        "kg",
        "ohg",
        "eg",
        "ev",
        "se",
        "ltd",
        "inc",
        "plc",
        "llc",
        "nv",
        "bv",
        "spa",
        "sas",
    }
)

# Occupation-slot tokens that are given-name abbreviations, not offices.
GIVEN_ABBR = frozenset({"joh", "ioh", "lud", "sam", "sig", "jac", "jak"})

# Used only to split a token that is exactly two of these glued together.
GIVEN_NAMES = frozenset(
    {
        "gottlieb",
        "ludwig",
        "johann",
        "johannes",
        "friedrich",
        "wilhelm",
        "heinrich",
        "karl",
        "carl",
        "georg",
        "george",
        "jean",
        "louis",
        "pierre",
        "hans",
        "ulrich",
        "samuel",
        "jakob",
        "jacob",
        "michael",
        "michel",
        "ernst",
        "david",
        "albert",
        "albrecht",
        "rudolf",
        "nikolaus",
        "nicolaus",
        "emanuel",
        "bernhard",
        "vincenz",
        "christoph",
        "sigmund",
        "theophil",
        "theophile",
        "anton",
        "peter",
        "charles",
        "henri",
        "henry",
        "franz",
        "francois",
        "daniel",
        "abraham",
        "elias",
        "elie",
        "xavier",
        "joseph",
        "alexander",
        "alexandre",
        "benjamin",
        "imbert",
        "victor",
        "viktor",
    }
)

_NAME_ROLES = frozenset({"LN", "FN", "AB"})
_GIVEN_BY_LENGTH = sorted(GIVEN_NAMES, key=len, reverse=True)


@dataclass
class Part:
    """One token of a person span, plus the tag subtype it should be stored as."""

    surface: str
    role: str
    payload: object = field(default=None, compare=False)


def normalize(token: str) -> str:
    """Lowercase, fold accents, map long s, and strip punctuation."""
    text = token.strip().lower().replace("ſ", "s")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return "".join(ch for ch in text if ch.isalnum())


def _with_period(surface: str) -> str:
    surface = surface.strip()
    if surface.endswith("."):
        return surface
    return surface + "."


def _is_legal(token: str) -> bool:
    return normalize(token) in LEGAL_FORMS


def _letter_run_is_legal(tokens: list[str]) -> bool:
    letters = []
    for token in tokens[:4]:
        folded = normalize(token)
        if len(folded) == 1 and folded.isalpha():
            letters.append(folded)
        else:
            break
    return len(letters) >= 2 and "".join(letters) in LEGAL_FORMS


def is_organisation(parts: list[Part], following: list[str]) -> bool:
    """
    A span is a company when it ends in a legal form, or the following
    tokens (outside the span) are one.
    """
    surfaces = [part.surface for part in parts]
    if surfaces and _is_legal(surfaces[-1]):
        return True
    tail = []
    for surface in reversed(surfaces):
        folded = normalize(surface)
        if len(folded) == 1 and folded.isalpha():
            tail.append(folded)
        else:
            break
    tail.reverse()
    if len(tail) >= 2 and "".join(tail) in LEGAL_FORMS:
        return True
    if following and _is_legal(following[0]):
        return True
    if _letter_run_is_legal(following):
        return True
    return False


def _split_glued_given_name(surface: str) -> tuple[str, str] | None:
    folded = normalize(surface)
    if folded in GIVEN_NAMES or len(folded) < 8:
        return None
    for prefix in _GIVEN_BY_LENGTH:
        if len(prefix) < 4 or not folded.startswith(prefix):
            continue
        suffix = folded[len(prefix) :]
        if len(suffix) >= 4 and suffix in GIVEN_NAMES:
            # Keep the original casing boundary by slicing the raw token
            # at the prefix length. The token is one alphabetic word.
            cut = len(prefix)
            return surface[:cut], surface[cut:]
    return None


def sanitize_parts(parts: list[Part], following: list[str] | None = None) -> list[Part] | None:
    """
    Rewrite one person span.

    :return: The kept tokens, or None when the span is a company or no
        name token remains.
    """
    following = following or []
    if not parts:
        return None
    if is_organisation(parts, following):
        return None

    rewritten: list[Part] = []
    for part in parts:
        folded = normalize(part.surface)
        role = part.role
        surface = part.surface
        if role in _NAME_ROLES and folded in TITLES:
            role = "TL"
        elif role in _NAME_ROLES and folded in OFFICES:
            role = "OC"
        elif part.role == "OC" and folded in GIVEN_ABBR:
            role = "AB"
            surface = _with_period(surface)
        rewritten.append(Part(surface, role, part.payload))

    index = 0
    while index < len(rewritten) - 1:
        particle = normalize(rewritten[index].surface)
        if rewritten[index].role in _NAME_ROLES and particle in {"le", "la"}:
            if rewritten[index + 1].role in {"TL", "OC"}:
                del rewritten[index]
                continue
        index += 1

    lastname_indexes = [i for i, part in enumerate(rewritten) if part.role == "LN"]
    zu_at = None
    for position, part_index in enumerate(lastname_indexes):
        if normalize(rewritten[part_index].surface) == "zu":
            zu_at = position
            break
    if zu_at is not None:
        for part_index in lastname_indexes[zu_at:]:
            rewritten[part_index].role = "AN"

    expanded: list[Part] = []
    for part in rewritten:
        match = _HYPHEN_INITIALS.match(part.surface.strip())
        if part.role in _NAME_ROLES and match:
            for letter in match.groups():
                expanded.append(Part(_with_period(letter.upper()), "AB", part.payload))
            continue
        if part.role in {"LN", "FN"}:
            genitive = _GENITIVE_S.match(part.surface)
            if genitive:
                part = Part(genitive.group(1), part.role, part.payload)
        if part.role == "FN":
            glued = _split_glued_given_name(part.surface)
            if glued:
                expanded.append(Part(glued[0], "FN", part.payload))
                expanded.append(Part(glued[1], "FN", part.payload))
                continue
        if part.role == "AB":
            part = Part(_with_period(part.surface), "AB", part.payload)
        expanded.append(part)

    # Hyphen splits run after the first title pass, so "M-B." becomes "M." "B."
    # and the new "M." has to be checked again.
    expanded = [
        Part(part.surface, "TL", part.payload)
        if part.role in _NAME_ROLES and normalize(part.surface) in TITLES
        else part
        for part in expanded
    ]

    if not any(part.role in _NAME_ROLES for part in expanded):
        return None
    return expanded


def apply_to_name_fields(record: dict) -> bool:
    """
    Apply the span rules to an aggregated person record.

    ``lastname`` is a string. ``firstname``, ``abbr_firstname``,
    ``profession``, ``titles`` and ``address`` are lists. ``other`` is
    left untouched.

    :return: True when a name token remains and the record can be linked.
    """
    parts: list[Part] = []
    for word in (record.get("lastname") or "").split():
        parts.append(Part(word, "LN"))
    for word in record.get("firstname") or []:
        for piece in str(word).split():
            parts.append(Part(piece, "FN"))
    for word in record.get("abbr_firstname") or []:
        parts.append(Part(str(word), "AB"))
    for word in record.get("profession") or []:
        parts.append(Part(str(word), "OC"))
    for word in record.get("titles") or []:
        parts.append(Part(str(word), "TL"))
    for word in record.get("address") or []:
        parts.append(Part(str(word), "AN"))

    cleaned = sanitize_parts(parts)
    buckets = {
        "LN": [],
        "FN": [],
        "AB": [],
        "OC": [],
        "TL": [],
        "AN": [],
    }
    if cleaned:
        for part in cleaned:
            if part.role in buckets and part.surface:
                buckets[part.role].append(part.surface)
    record["lastname"] = " ".join(buckets["LN"])
    record["firstname"] = buckets["FN"]
    record["abbr_firstname"] = buckets["AB"]
    record["profession"] = buckets["OC"]
    record["titles"] = buckets["TL"]
    record["address"] = buckets["AN"]
    return bool(buckets["LN"] or buckets["FN"] or buckets["AB"])
