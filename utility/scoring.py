"""
Ranking of knowledge-base candidates for a person mention.

Candidate ranking used to be an emergent property of the order in which the
Elasticsearch queries happened to be issued: results were merged into a plain
dictionary and never sorted, so a candidate's position was decided by whichever
query found it first, and equal scores were compared with ``==`` on floats that
only ever came out equal because each query normalized its own top hit to 1.0.

This module makes that ordering explicit. A candidate is placed in a *tier*
according to what kind of match it is — an exact hit on a GND preferred name
outranks a hit on a variant name, which outranks a Wikidata label, and every
exact match outranks every fuzzy one. The Elasticsearch score only orders
candidates that already share a tier.

The tier table is data, in :class:`ScoringPolicy`, because trying different
orderings is the point. Everything else stays logic: the aim here is to
reproduce the current ranking through a structure that can be reasoned about,
not to add behaviour that does not exist yet.

Nothing here talks to Elasticsearch or reads the global settings.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field

MatchKind = str

#: Tier order matching the sequence the candidate queries are issued in:
#: exactness first, then field, then source.
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


def confidence_level(
    n_ids: int, has_full_name: bool, name_match: bool, vd_used: bool
) -> int:
    """
    Grades how much a linking decision can be trusted, from 1 to 5.

    This is the decision tree that used to sit inside ``prep_person_out``,
    unchanged and in the same shape. Keeping it nested is deliberate: where a
    branch does not consult a fact there is no test for it, so the cases that
    ignore a dimension cannot drift apart from each other. Flattening it into a
    lookup table would turn that guarantee into a convention.

    :param n_ids: How many ids survived.
    :type n_ids: int
    :param has_full_name: Whether the mention had both a firstname and lastname.
    :type has_full_name: bool
    :param name_match: Whether the leading candidate's name confirms the mention.
    :type name_match: bool
    :param vd_used: Whether the vector database decided the ranking.
    :type vd_used: bool
    :return: Confidence from 1 (minimal) to 5 (excellent).
    :rtype: int
    """

    if n_ids == 0:
        # Nothing was linked; the only question is whether the vector database
        # tested that conclusion or never saw it.
        return 4 if vd_used else 5

    if has_full_name:
        if n_ids == 1:
            return 5 if name_match else 4
        if vd_used:
            return 4 if name_match else 3
        return 3

    if n_ids == 1:
        return 4 if name_match else 3
    if name_match:
        return 2
    return 2 if vd_used else 1


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

    ``fields`` holds the converted payload and ``retrieval`` maps every query
    label that returned this candidate to that query's raw Elasticsearch score.
    Both are excluded from hashing: freezing is shallow, a dict field would make
    the generated ``__hash__`` raise, and equality should still compare payloads
    in full. Build each candidate with its own copy of the payload — sharing one
    dictionary between candidates reintroduces the aliasing this type exists to
    prevent.
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
# Whether a candidate's own name confirms the mention. This is the check that
# used to be ``_name_matches``, split into the cases it was testing.
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

    Deliberately small. The defaults reproduce the ranking the pipeline produced
    before scoring was made explicit, so that adopting the scorer is not also a
    silent change in results.
    """

    #: Which kind of match outranks which. The one thing meant to be varied.
    score_priority: dict[MatchKind, int] = Field(
        default_factory=lambda: dict(DEFAULT_SCORE_PRIORITY)
    )

    #: How a raw Elasticsearch score becomes the within-tier tie-breaker.
    #: ``max_norm`` is what the pipeline does today; ``none`` ignores the score
    #: entirely, leaving the tier to decide, which is the baseline for judging
    #: whether the score contributes anything.
    es_transform: Literal["max_norm", "none"] = "max_norm"

    #: Tolerance for calling two within-tier scores equal. Needed because the
    #: previous code compared floats with ``==`` and only got away with it while
    #: every query's top hit was normalized to exactly 1.0.
    tie_epsilon: float = 1e-6


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

    def name_matches(self, mention: Mention, candidate: Candidate) -> bool:
        """
        Whether the candidate's own name confirms the mention.

        :param mention: The mention being linked.
        :type mention: Mention
        :param candidate: Candidate to check.
        :type candidate: Candidate
        :return: True if any of the match cases holds.
        :rtype: bool
        """

        return any(predicate(mention, candidate) for predicate in MATCHERS.values())

    def _components(
        self, candidates: Sequence[Candidate]
    ) -> dict[tuple[str, str], float]:
        """
        Translates raw Elasticsearch scores into comparable numbers.

        A score is only meaningful relative to the query that produced it, so
        the transform is applied per query label.

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

    def score(self, mention: Mention, candidates: Iterable[Candidate]) -> ScoredResult:
        """
        Ranks candidates for one mention.

        :param mention: The mention being linked.
        :type mention: Mention
        :param candidates: Candidates retrieved for it.
        :type candidates: Iterable[Candidate]
        :return: The ranking, and what the vector database should look at.
        :rtype: ScoredResult
        """

        candidates = list(candidates)
        result = ScoredResult()
        if not candidates:
            result.confidence = confidence_level(0, mention.has_full_name, False, False)
            return result

        components = self._components(candidates)
        for cand in candidates:
            tier, label = self.tier(cand)
            result.ranked.append(
                ScoredCandidate(
                    gid=cand.gid,
                    tier=tier,
                    tier_label=label,
                    # The score comes from the query that set the tier: that is
                    # the evidence the placement rests on, and taking the best
                    # across queries would let an unrelated query's normalized
                    # top hit reorder a tier it had no part in.
                    es_component=components.get((cand.gid, label), 0.0),
                )
            )

        # Trailing gid keeps the order total, so a run is reproducible and two
        # policies can be diffed without spurious churn.
        result.ranked.sort(key=lambda c: (c.tier, -c.es_component, c.gid))

        best = result.ranked[0]
        result.top_tier = [
            c.gid
            for c in result.ranked
            if c.tier == best.tier
            and abs(c.es_component - best.es_component) <= self.policy.tie_epsilon
        ]
        result.needs_disambiguation = len(result.top_tier) > 1

        by_gid = {c.gid: c for c in candidates}
        result.confidence = confidence_level(
            len(result.ranked),
            mention.has_full_name,
            self.name_matches(mention, by_gid[best.gid]),
            False,
        )
        return result
