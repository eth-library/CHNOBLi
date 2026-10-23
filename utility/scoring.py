"""
Ranking of knowledge-base candidates for a person mention.

A candidate is placed in a *tier* according to what kind of match it is. An
exact hit on a GND preferred name outranks a hit on a variant name, which
outranks a Wikidata label, and every exact match outranks every fuzzy one. A
candidate lands in the best tier any query that returned it justifies, and the
Elasticsearch score only orders candidates that already share a tier.

The tier table is data, in :class:`ScoringPolicy`, because trying different
orderings is the point. Everything else stays logic. Every default reproduces
the ranking the linking stage produces, so an alternative scheme is a change of
policy rather than a rewrite.

Nothing here talks to Elasticsearch or reads the global settings.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from itertools import takewhile
from typing import Literal

from pydantic import BaseModel, Field

MatchKind = str

#: Tier order matching the sequence the candidate queries are issued in:
#: exactness first, then field, then source.
#:
#: A mention with abbreviated forenames usually has no full forenames, or the
#: two do not overlap, so the abbreviation branch and the full-name branch are
#: mutually exclusive and never contribute to the same mention. The
#: abbreviation-only branch therefore reuses the preferred-name tiers (1 and 5)
#: with the abbreviations as query text, and needs no tiers of its own.
DEFAULT_SCORE_PRIORITY: dict[MatchKind, int] = {
    "gnd_pref_exact": 1,
    "gnd_pref_abbr_exact": 2,
    "gnd_variant_exact": 3,
    "wikidata_label_exact": 4,
    "gnd_pref_fuzzy": 5,
    "gnd_pref_abbr_fuzzy": 6,
    "gnd_variant_fuzzy": 7,
    "wikidata_label_fuzzy": 8,
}


def _leading_close_scores(scores: list[float], tolerance: float) -> list[float]:
    if not scores:
        return []

    best = scores[0]
    return scores[:1] + list(
        takewhile(lambda score: abs(best - score) <= tolerance, scores[1:])
    )


def _name_matches(person: dict) -> bool:
    """
    If the first of the candidates (they're ordered by score) have a matching
    name, we return True, else False
    """
    first_cand_firstname = " ".join(person["candidates"][0].get("prefForename", ""))
    first_cand_lastname = " ".join(person["candidates"][0].get("prefSurname", ""))
    first_cand_varname = person["candidates"][0].get("varName", None)
    joined_fname = " ".join(person["firstname"])
    joined_abbr_fname = " ".join(person["abbr_firstname"])
    if person["firstname"] and person["lastname"]:
        if (
            (
                first_cand_firstname == joined_fname
                and first_cand_lastname == person["lastname"]
            )
            or (
                first_cand_firstname
                == (joined_fname + joined_abbr_fname).replace("  ", " ").strip()
                and first_cand_lastname == person["lastname"]
            )
            or (
                first_cand_varname
                and (
                    (person["lastname"] + ", " + joined_fname in first_cand_varname)
                    or (
                        person["lastname"]
                        + ", "
                        + (joined_fname + joined_abbr_fname).replace("  ", " ").strip()
                        in first_cand_varname
                    )
                )
            )
        ):
            return True
    elif (
        person["abbr_firstname"]
        and person["lastname"]
        and (
            (
                first_cand_firstname.startswith(joined_abbr_fname.replace(".", ""))
                and first_cand_lastname == person["lastname"]
            )
            or (
                first_cand_varname
                and person["lastname"] + ", " + joined_abbr_fname in first_cand_varname
            )
        )
    ):
        return True
    return False


def confidence_level(person: dict) -> (int, str):
    """
    Grades how much a linking decision can be trusted, from 0 to 5.

    The tree stays nested rather than flattened into a lookup table: where a
    branch does not consult a fact there is no test for it, so every case that
    ignores a dimension is bound to agree with the others instead of agreeing
    by convention.

    :param person: Person whose candidates to define the confidence for.
    :type person: dict
    :return: Confidence for the frontend, on the pipeline's scale:
        5 excellent, 4 very good, 3 good, 2 medium, 1 minimal, 0 experimental,
        and which case it was.
    :rtype: (int, str)
    """

    vd_used = False
    has_full_name = bool(person["firstname"]) and bool(person["lastname"])
    # Guarded: the grade for an unlinkable person does not consult the name,
    # and _name_matches reads a leading candidate that is not there.
    name_match = len(person["gnd_ids"]) > 0 and _name_matches(person)

    # create gnd_ids list for website / confidence scoring
    if person.get("gnd_ids_VD_dist"):
        vd_used = True
        website_scores = _leading_close_scores(person["gnd_ids_VD_dist"], 0.009)
        person["website_gnd_ids_VD_dist"] = website_scores
        person["website_gnd_ids"] = person["gnd_ids"][: len(website_scores)]
    elif person.get("gnd_ids_ES_sim"):
        website_scores = _leading_close_scores(person["gnd_ids_ES_sim"], 0.05)
        person["website_gnd_ids_ES_sim"] = website_scores
        person["website_gnd_ids"] = person["gnd_ids"][: len(website_scores)]
    else:
        person["website_gnd_ids"] = person["gnd_ids"]

    n_ids = len(person["website_gnd_ids"])

    if n_ids == 0:
        if has_full_name:
            return (4, "111") if vd_used else (5, "110")
        return (0, "011") if vd_used else (0, "010")

    if has_full_name:
        if n_ids == 1:
            if vd_used:
                return (5, "1111") if name_match else (4, "1110")
            return (4, "1101") if name_match else (4, "1100")

        if vd_used:
            return (4, "1011") if name_match else (3, "1010")
        return (3, "1001") if name_match else (2, "1000")

    if n_ids == 1:
        if vd_used:
            return (3, "0111") if name_match else (3, "0110")
        return (3, "0101") if name_match else (3, "0100")

    if vd_used:
        return (2, "0011") if name_match else (2, "0010")
    return (2, "0001") if name_match else (1, "0000")


def _norm(word: str) -> str:
    """
    Normalizes a name token for comparison.

    :param word: Token to normalize.
    :type word: str
    :return: Case-folded, composed token without surrounding punctuation.
    :rtype: str
    """

    word = unicodedata.normalize("NFC", word).strip()
    return word.strip(".,;:").casefold()


def _tokens(values: Iterable[str]) -> tuple[str, ...]:
    """
    Normalizes and sorts name parts, so that comparison does not depend on the
    order they happened to be stored in.

    :param values: Name parts, possibly multi-word.
    :type values: Iterable[str]
    :return: Sorted tuple of normalized single-word tokens.
    :rtype: tuple[str, ...]
    """

    out = []
    for value in values or ():
        for part in str(value).split():
            token = _norm(part)
            if token:
                out.append(token)
    return tuple(sorted(out))


@dataclass(frozen=True)
class Mention:
    """
    A normalized person mention, as the aggregation stage produced it.

    Frozen so that it cannot be altered halfway through scoring, and built from
    tuples so it stays hashable.
    """

    lastname: tuple[str, ...] = ()
    firstnames: tuple[str, ...] = ()
    abbr_firstnames: tuple[str, ...] = ()
    year: str = ""

    @property
    def has_full_name(self) -> bool:
        """Whether both a firstname and a lastname are present."""

        return bool(self.firstnames) and bool(self.lastname)


@dataclass(frozen=True)
class Candidate:
    """
    One knowledge-base entry returned for a mention.

    One entry, one GND id. A Wikidata entry sometimes carries several GND ids
    and is registered under each of them, which breaks a good deal of the
    surrounding logic and cannot be fixed on our end: the duplicates sit in the
    knowledge base itself.

    ``fields`` holds the converted payload and ``retrieval`` maps every query
    label that returned this candidate to that query's raw Elasticsearch score.
    Both are excluded from hashing: freezing is shallow, so a dict field would
    make the generated ``__hash__`` raise, while equality should still compare
    payloads in full. Build each candidate with its own copy of the payload;
    sharing one dictionary between candidates reintroduces the aliasing this
    type exists to prevent.
    """

    gid: str
    source: str = "gnd"
    fields: Mapping = field(default_factory=dict, hash=False)
    retrieval: Mapping[str, float] = field(default_factory=dict, hash=False)

    def pref_forename(self) -> tuple[str, ...]:
        """Normalized tokens of the candidate's preferred forename."""

        return _tokens(self.fields.get("prefForename", ()))

    def pref_surname(self) -> tuple[str, ...]:
        """Normalized tokens of the candidate's preferred surname."""

        return _tokens(self.fields.get("prefSurname", ()))

    def variant_names(self) -> tuple[str, ...]:
        """Normalized variant name strings."""

        return tuple(_norm(v) for v in self.fields.get("varName", ()) or ())


@dataclass(frozen=True)
class ScoredCandidate:
    """A candidate together with the numbers that placed it."""

    gid: str
    tier: int
    tier_label: str
    es_component: float


@dataclass
class ScoredResult:
    """
    The outcome of scoring one mention.

    Not frozen: it is assembled field by field, and unlike the inputs it is
    never shared.
    """

    ranked: list[ScoredCandidate] = field(default_factory=list)

    #: The candidates the retrieval scores could not separate. When several of
    #: the leading ids share the same score, all of them are taken and re-ranked
    #: by the vector database rather than one being picked arbitrarily.
    top_tier: list[str] = field(default_factory=list)
    needs_disambiguation: bool = False
    confidence: int = 5

    def gids(self, limit: int | None = None) -> list[str]:
        """
        The ranked ids, best first.

        :param limit: Truncate to this many, or None for all.
        :type limit: int | None
        :return: List of GND ids.
        :rtype: list[str]
        """

        out = [c.gid for c in self.ranked]
        return out if limit is None else out[:limit]


# --------------------------------------------------------------------------
# Whether a candidate's own name confirms the mention, one predicate per case
# the check accepts.
# --------------------------------------------------------------------------


def _abbrevs_compatible(abbrevs: Sequence[str], forenames: Sequence[str]) -> bool:
    """
    Whether every abbreviation is the initial of some forename token.

    :param abbrevs: Normalized abbreviation tokens, e.g. ``("j",)``.
    :type abbrevs: Sequence[str]
    :param forenames: Normalized forename tokens of the candidate.
    :type forenames: Sequence[str]
    :return: True if each abbreviation is accounted for.
    :rtype: bool
    """

    if not abbrevs:
        return True
    remaining = list(forenames)
    for abbr in abbrevs:
        hit = next((f for f in remaining if f.startswith(abbr)), None)
        if hit is None:
            return False
        remaining.remove(hit)
    return True


def match_gnd_pref_exact(mention: Mention, candidate: Candidate) -> bool:
    """Preferred forename and surname equal the mention's full name."""

    if candidate.source != "gnd" or not mention.firstnames:
        return False
    return candidate.pref_forename() == _tokens(
        mention.firstnames
    ) and candidate.pref_surname() == _tokens(mention.lastname)


def match_gnd_pref_abbr_exact(mention: Mention, candidate: Candidate) -> bool:
    """Surname matches and the forenames account for the abbreviations."""

    if candidate.source != "gnd":
        return False
    if candidate.pref_surname() != _tokens(mention.lastname):
        return False
    forenames = candidate.pref_forename()
    if not forenames:
        return False
    given = _tokens(mention.firstnames)
    if given and not set(given).issubset(forenames):
        return False
    return _abbrevs_compatible(_tokens(mention.abbr_firstnames), forenames)


def match_gnd_variant_exact(mention: Mention, candidate: Candidate) -> bool:
    """A variant name matches the mention in GND's surname-first form."""

    if candidate.source != "gnd":
        return False
    surname = " ".join(_tokens(mention.lastname))
    given = " ".join(_tokens(mention.firstnames) + _tokens(mention.abbr_firstnames))
    if not surname or not given:
        return False
    wanted = f"{surname}, {given}"
    return any(wanted in variant for variant in candidate.variant_names())


def match_wikidata_label_exact(mention: Mention, candidate: Candidate) -> bool:
    """A Wikidata label resolves to the mention's full name."""

    if candidate.source != "wikidata":
        return False
    return candidate.pref_forename() == _tokens(
        mention.firstnames
    ) and candidate.pref_surname() == _tokens(mention.lastname)


#: The cases in which a candidate's own name confirms the mention.
MATCHERS: dict[MatchKind, Callable[[Mention, Candidate], bool]] = {
    "gnd_pref_exact": match_gnd_pref_exact,
    "gnd_pref_abbr_exact": match_gnd_pref_abbr_exact,
    "gnd_variant_exact": match_gnd_variant_exact,
    "wikidata_label_exact": match_wikidata_label_exact,
}


class ScoringPolicy(BaseModel):
    """
    The ranking, as data.

    Deliberately small. Every default reproduces the ranking the linking stage
    produces, so adopting the scorer does not also change results.
    """

    #: Which kind of match outranks which. The one thing meant to be varied.
    score_priority: dict[MatchKind, int] = Field(
        default_factory=lambda: dict(DEFAULT_SCORE_PRIORITY)
    )

    #: How a raw Elasticsearch score becomes the within-tier tie-breaker.
    #: ``max_norm`` divides every score by the top score of the query that
    #: produced it, as the retrieval helpers do. ``none`` drops the score
    #: entirely and leaves the tier to decide, which is the baseline for
    #: judging whether the score contributes anything.
    es_transform: Literal["max_norm", "none"] = "max_norm"

    #: Which of a candidate's query scores it is compared on. ``max`` takes the
    #: best score any query gave it, even though each of those was normalized
    #: against a different query's top hit. ``placing_query`` takes the score
    #: from the query that set the candidate's tier, so the number it is
    #: compared on is the evidence its placement rests on. That reading is the
    #: more coherent one but it moves candidates, so ``max`` stays the default.
    es_combine: Literal["max", "placing_query"] = "max"

    #: How far the tie at the top reaches. ``prefix`` walks the ranking from the
    #: front while candidates keep matching the leader's score and **does not
    #: stop at a tier boundary**, so a query settles the mention only if the
    #: queries before it left no clear winner. ``top_tier`` stops at the
    #: leader's tier, so a lower-tier candidate can never join the tie.
    tie_scope: Literal["prefix", "top_tier"] = "prefix"

    #: Tolerance for calling two scores equal. Zero compares them exactly, as
    #: the linking stage does: the scores that meet at the top are equal only
    #: because each query normalizes its own top hit to exactly 1.0, so they
    #: coincide bit for bit rather than approximately. A small tolerance such as
    #: 1e-6 admits scores that merely came close, which widens ties and sends
    #: more mentions to the vector database.
    tie_epsilon: float = 0.04


class CandidateScorer:
    """Turns retrieved candidates into a ranking."""

    def __init__(self, policy: ScoringPolicy | None = None) -> None:
        """
        :param policy: Policy to score with, or None for the defaults.
        :type policy: ScoringPolicy | None
        """

        self.policy = policy or ScoringPolicy()

    def tier(self, candidate: Candidate) -> tuple[int, str]:
        """
        The best tier justified by the queries that returned this candidate.

        Every query that found the candidate is evidence about it, so the tier
        is the best of them. While the queries are issued one after another this
        is the same as "the first query that returned it"; expressed as a
        minimum it stays correct once they are sent together.

        :param candidate: Candidate to place.
        :type candidate: Candidate
        :return: Its tier and the label that justified it.
        :rtype: tuple[int, str]
        :raises ValueError: If no label is known to the policy.
        """

        best: tuple[int, str] | None = None
        for label in candidate.retrieval:
            rank = self.policy.score_priority.get(label)
            if rank is None:
                continue
            if best is None or rank < best[0] or (rank == best[0] and label < best[1]):
                best = (rank, label)
        if best is None:
            raise ValueError(
                f"Candidate {candidate.gid} carries no query label known to the "
                f"policy (has {sorted(candidate.retrieval)})."
            )
        return best

    def _components(
        self, candidates: Sequence[Candidate]
    ) -> dict[tuple[str, str], float]:
        """
        Translates raw Elasticsearch scores into comparable numbers.

        A score is only meaningful relative to the query that produced it, so
        the transform is applied per query label. This is the "scale them to 1"
        step the retrieval helpers perform today, and its purpose is to make
        scores from **different indexes** comparable: a GND hit and a Wikidata
        hit are scored by different fields against different corpora, so their
        raw values cannot be compared directly.

        :param candidates: Candidates being scored.
        :type candidates: Sequence[Candidate]
        :return: Mapping of (gid, label) to the transformed value.
        :rtype: dict[tuple[str, str], float]
        """

        if self.policy.es_transform == "none":
            return {}

        by_label: dict[str, list[tuple[str, float]]] = {}
        for cand in candidates:
            for label, raw in cand.retrieval.items():
                by_label.setdefault(label, []).append((cand.gid, float(raw or 0.0)))

        out: dict[tuple[str, str], float] = {}
        for label, entries in by_label.items():
            top = max((raw for _, raw in entries), default=0.0)
            for gid, raw in entries:
                out[(gid, label)] = raw / top if top else 0.0
        return out

    def score(
        self, person: dict, candidates: Iterable[Candidate], year: str
    ) -> ScoredResult:
        """
        Ranks candidates for one person.

        :param person: The person being linked.
        :type person: dict
        :param candidates: Candidates retrieved for it.
        :type candidates: Iterable[Candidate]
        :param year: Publication year of the magazine in which this person was mentioned.
        :type year: str
        :return: The ranking, and what the vector database should look at.
        :rtype: ScoredResult
        """
        candidates = list(candidates)
        result = ScoredResult()
        if not candidates:
            return result

        components = self._components(candidates)
        for cand in candidates:
            tier, label = self.tier(cand)
            if self.policy.es_combine == "placing_query":
                component = components.get((cand.gid, label), 0.0)
            else:
                component = max(
                    (components.get((cand.gid, lab), 0.0) for lab in cand.retrieval),
                    default=0.0,
                )
            result.ranked.append(
                ScoredCandidate(
                    gid=cand.gid,
                    tier=tier,
                    tier_label=label,
                    es_component=component,
                )
            )

        # Tier only, and a stable sort, so candidates keep the order they were
        # retrieved in within a tier. Sorting on the score as well would lift a
        # candidate that a later query scored higher above one an earlier query
        # placed first; the score settles the tie below, not the position.
        result.ranked.sort(key=lambda c: c.tier)

        best = result.ranked[0]
        if self.policy.tie_scope == "top_tier":
            result.top_tier = [
                c.gid
                for c in result.ranked
                if c.tier == best.tier
                and abs(c.es_component - best.es_component) <= self.policy.tie_epsilon
            ]
        else:
            # Walk from the front while the leader's score keeps being matched,
            # crossing tiers: the next query counts only when the current one
            # produced no clear winner.
            result.top_tier = [
                c.gid
                for c in takewhile(
                    lambda c: (
                        abs(c.es_component - best.es_component)
                        <= self.policy.tie_epsilon
                    ),
                    result.ranked,
                )
            ]
        result.needs_disambiguation = len(result.top_tier) > 1

        return result
