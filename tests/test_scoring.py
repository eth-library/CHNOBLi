"""Tests for the candidate scorer."""

from dataclasses import FrozenInstanceError

import pytest

from utility.scoring import (
    Candidate,
    CandidateScorer,
    Mention,
    ScoringPolicy,
    confidence_level,
)


def gnd(gid, retrieval, forename=(), surname=(), variants=()):
    """Builds a GND candidate with its own payload copy."""
    return Candidate(
        gid=gid,
        source="gnd",
        fields={
            "prefForename": set(forename),
            "prefSurname": set(surname),
            "varName": set(variants),
        },
        retrieval=dict(retrieval),
    )


def wikidata(gid, retrieval, forename=(), surname=()):
    return Candidate(
        gid=gid,
        source="wikidata",
        fields={"prefForename": set(forename), "prefSurname": set(surname)},
        retrieval=dict(retrieval),
    )


HANS = Mention(
    lastname=("Ebert",), firstnames=("Hans",), abbr_firstnames=("J.",), year="1931"
)


# -------------------------------------------------
# Ranking is by tier, not by the order candidates arrived in
# -------------------------------------------------
def test_ranks_by_tier_not_insertion_order():
    """A wikidata hit listed first must not outrank an exact GND hit."""
    cands = [
        wikidata("55512", {"wikidata_label_exact": 30.0}),
        gnd("118527673", {"gnd_pref_exact": 4.0}),
    ]
    assert CandidateScorer().score(HANS, cands).gids() == ["118527673", "55512"]


def test_tier_is_the_best_label_not_the_first():
    """A candidate found by several queries keeps its strongest evidence."""
    cand = gnd("118527673", {"gnd_pref_fuzzy": 9.0, "gnd_pref_exact": 4.0})
    assert CandidateScorer().tier(cand) == (1, "gnd_pref_exact")


def test_unknown_query_label_is_rejected():
    """A label the policy does not know is a bug, not a candidate to guess at."""
    with pytest.raises(ValueError, match="no query label"):
        CandidateScorer().tier(gnd("x", {"something_else": 1.0}))


def test_ties_spanning_queries_are_collected():
    """
    Top hits of two different queries are both candidates for disambiguation.

    The previous implementation stopped at the first query's second hit and
    silently dropped equally-scored candidates found by later queries.
    """
    cands = [
        gnd("111", {"gnd_pref_exact": 18.0}),
        gnd("222", {"gnd_pref_exact": 18.0}),
        gnd("333", {"gnd_pref_exact": 2.0}),
    ]
    result = CandidateScorer().score(HANS, cands)
    assert sorted(result.top_tier) == ["111", "222"]
    assert result.needs_disambiguation is True


def test_score_from_the_tier_defining_query_only():
    """A high score borrowed from a weaker query must not reorder a tier."""
    cands = [
        gnd("aaa", {"gnd_pref_exact": 4.2, "wikidata_label_exact": 100.0}),
        gnd("bbb", {"gnd_pref_exact": 18.4}),
    ]
    assert CandidateScorer().score(HANS, cands).gids() == ["bbb", "aaa"]


def test_order_is_total_and_deterministic():
    """Identical tier and score fall back to the id, so runs are reproducible."""
    cands = [
        gnd("999", {"gnd_pref_exact": 5.0}),
        gnd("111", {"gnd_pref_exact": 5.0}),
    ]
    first = CandidateScorer().score(HANS, cands).gids()
    second = CandidateScorer().score(HANS, list(reversed(cands))).gids()
    assert first == second == ["111", "999"]


def test_score_priority_can_be_reordered():
    """The tier table is the thing that is meant to be varied."""
    cands = [
        gnd("pref", {"gnd_pref_exact": 5.0}),
        gnd("variant", {"gnd_variant_exact": 5.0}),
    ]
    assert CandidateScorer().score(HANS, cands).gids() == ["pref", "variant"]
    flipped = ScoringPolicy(
        score_priority={"gnd_variant_exact": 1, "gnd_pref_exact": 2}
    )
    assert CandidateScorer(flipped).score(HANS, cands).gids() == ["variant", "pref"]


# -------------------------------------------------
# es_transform
# -------------------------------------------------
def test_max_norm_orders_within_a_tier_by_score():
    cands = [
        gnd("low", {"gnd_pref_exact": 4.2}),
        gnd("high", {"gnd_pref_exact": 18.4}),
        gnd("mid", {"gnd_pref_exact": 17.9}),
    ]
    assert CandidateScorer().score(HANS, cands).gids() == ["high", "mid", "low"]


def test_transform_none_leaves_the_tier_to_decide():
    """Without the score, everything in a tier is tied and goes on to the VD."""
    cands = [
        gnd("low", {"gnd_pref_exact": 4.2}),
        gnd("high", {"gnd_pref_exact": 18.4}),
    ]
    result = CandidateScorer(ScoringPolicy(es_transform="none")).score(HANS, cands)
    assert sorted(result.top_tier) == ["high", "low"]
    assert result.needs_disambiguation is True


def test_tie_epsilon_absorbs_float_noise():
    """Scores that differ only by rounding must count as tied."""
    cands = [
        gnd("a", {"gnd_pref_exact": 1.0}),
        gnd("b", {"gnd_pref_exact": 1.0 - 1e-12}),
    ]
    assert len(CandidateScorer().score(HANS, cands).top_tier) == 2


# -------------------------------------------------
# name matching
# -------------------------------------------------
def test_variant_name_match_uses_the_surname_first_form():
    cand = gnd("x", {"gnd_variant_fuzzy": 1.0}, variants=("Ebert, Hans J.",))
    assert CandidateScorer().name_matches(HANS, cand) is True


def test_abbreviation_matches_a_longer_forename():
    cand = gnd("x", {"gnd_pref_exact": 1.0}, forename=("Hans", "Jakob"),
               surname=("Ebert",))
    assert CandidateScorer().name_matches(HANS, cand) is True


def test_wrong_forename_does_not_match():
    cand = gnd("x", {"gnd_pref_exact": 1.0}, forename=("Heinrich",), surname=("Ebert",))
    assert CandidateScorer().name_matches(HANS, cand) is False


def test_forename_order_does_not_affect_matching():
    """Payload names arrive in sets, so comparison must not depend on order."""
    mention = Mention(lastname=("Ebert",), firstnames=("Hans", "Jakob"))
    cand = gnd("x", {"gnd_pref_exact": 1.0}, forename=("Jakob", "Hans"),
               surname=("Ebert",))
    assert CandidateScorer().name_matches(mention, cand) is True


# -------------------------------------------------
# confidence
# -------------------------------------------------
# Transcribed from the decision tree in prep_person_out, so that an accidental
# edit to confidence_level shows up here rather than on the public site.
CONFIDENCE_CASES = [
    # n_ids, has_full_name, name_match, vd_used, expected
    (0, False, False, False, 5), (0, False, False, True, 4),
    (0, True, False, False, 5),  (0, True, False, True, 4),
    (1, True, True, False, 5),   (1, True, True, True, 5),
    (1, True, False, False, 4),  (1, True, False, True, 4),
    (1, False, True, False, 4),  (1, False, True, True, 4),
    (1, False, False, False, 3), (1, False, False, True, 3),
    (2, True, True, True, 4),    (2, True, False, True, 3),
    (2, True, True, False, 3),   (2, True, False, False, 3),
    (2, False, True, False, 2),  (2, False, True, True, 2),
    (2, False, False, True, 2),  (2, False, False, False, 1),
]


@pytest.mark.parametrize("n_ids,full,match,vd,expected", CONFIDENCE_CASES)
def test_confidence_matches_the_previous_decision_tree(n_ids, full, match, vd, expected):
    assert confidence_level(n_ids, full, match, vd) == expected


def test_confidence_of_an_unlinkable_mention():
    result = CandidateScorer().score(HANS, [])
    assert result.confidence == 5
    assert result.gids() == []


# -------------------------------------------------
# the value types
# -------------------------------------------------
def test_mention_is_hashable_and_immutable():
    mention = Mention(lastname=("Ebert",), firstnames=("Hans",))
    assert {mention: 1}[mention] == 1
    with pytest.raises(FrozenInstanceError):
        mention.lastname = ("Other",)  # type: ignore[misc]


def test_candidate_hashes_without_its_payload_but_compares_with_it():
    a = gnd("111", {"gnd_pref_exact": 1.0}, forename=("Hans",))
    b = gnd("111", {"gnd_pref_exact": 1.0}, forename=("Heinrich",))
    assert hash(a) == hash(b)
    assert a != b
