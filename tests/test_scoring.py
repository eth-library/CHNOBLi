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


def test_retrieval_order_is_kept_within_a_tier():
    """
    The pipeline ranks by the order candidates came back in, not by score, so
    the scorer must not reorder a tier. Elasticsearch already returns hits
    best-first, which is what makes retrieval order meaningful.
    """
    cands = [
        gnd("first", {"gnd_pref_exact": 18.4}),
        gnd("second", {"gnd_pref_exact": 4.2}),
    ]
    assert CandidateScorer().score(HANS, cands).gids() == ["first", "second"]
    flipped = list(reversed(cands))
    assert CandidateScorer().score(HANS, flipped).gids() == ["second", "first"]


def test_a_later_query_does_not_move_a_candidate():
    """
    A candidate whose score a weaker query raised keeps its place. Sorting on
    the merged score would promote it; the pipeline does not.
    """
    cands = [
        gnd("aaa", {"gnd_pref_exact": 4.2, "wikidata_label_exact": 100.0}),
        gnd("bbb", {"gnd_pref_exact": 18.4}),
    ]
    assert CandidateScorer().score(HANS, cands).gids() == ["aaa", "bbb"]


def test_placing_query_score_is_available_as_a_policy():
    """The coherent alternative: score from the query that set the tier."""
    cands = [
        gnd("aaa", {"gnd_pref_exact": 4.2, "wikidata_label_exact": 100.0}),
        gnd("bbb", {"gnd_pref_exact": 18.4}),
    ]
    policy = ScoringPolicy(es_combine="placing_query")
    result = CandidateScorer(policy).score(HANS, cands)
    assert result.top_tier == ["aaa"]
    assert CandidateScorer().score(HANS, cands).top_tier == ["aaa", "bbb"]


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
def test_max_norm_scales_each_query_to_its_own_top_hit():
    """
    The transform decides the tie, not the order: only the leader's equals (including
    the tie epsilon) stay in the tie set, and the rest keep their retrieval positions.
    """
    cands = [
        gnd("high", {"gnd_pref_exact": 18.4}),
        gnd("mid", {"gnd_pref_exact": 17.9}),
        gnd("low", {"gnd_pref_exact": 4.2}),
    ]
    result = CandidateScorer().score(HANS, cands)
    assert result.gids() == ["high", "mid", "low"]
    assert result.top_tier == ["high", "mid"]


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
    """A tolerance widens the tie to scores that differ only by rounding."""
    cands = [
        gnd("a", {"gnd_pref_exact": 1.0}),
        gnd("b", {"gnd_pref_exact": 1.0 - 1e-12}),
    ]
    policy = ScoringPolicy(tie_epsilon=1e-6)
    assert len(CandidateScorer(policy).score(HANS, cands).top_tier) == 2


# -------------------------------------------------
# name matching
# -------------------------------------------------
def test_variant_name_match_uses_the_surname_first_form():
    cand = gnd("x", {"gnd_variant_fuzzy": 1.0}, variants=("Ebert, Hans J.",))
    assert CandidateScorer().name_matches(HANS, cand) is True


def test_abbreviation_matches_a_longer_forename():
    cand = gnd(
        "x", {"gnd_pref_exact": 1.0}, forename=("Hans", "Jakob"), surname=("Ebert",)
    )
    assert CandidateScorer().name_matches(HANS, cand) is True


def test_wrong_forename_does_not_match():
    cand = gnd("x", {"gnd_pref_exact": 1.0}, forename=("Heinrich",), surname=("Ebert",))
    assert CandidateScorer().name_matches(HANS, cand) is False


def test_forename_order_does_not_affect_matching():
    """Payload names arrive in sets, so comparison must not depend on order."""
    mention = Mention(lastname=("Ebert",), firstnames=("Hans", "Jakob"))
    cand = gnd(
        "x", {"gnd_pref_exact": 1.0}, forename=("Jakob", "Hans"), surname=("Ebert",)
    )
    assert CandidateScorer().name_matches(mention, cand) is True


# -------------------------------------------------
# confidence
# -------------------------------------------------
# Transcribed from the decision tree in prep_person_out, so that an accidental
# edit to confidence_level shows up here rather than on the public site.
CONFIDENCE_CASES = [
    # n_ids, has_full_name, name_match, vd_used, expected
    (0, False, False, False, 5),
    (0, False, False, True, 4),
    (0, True, False, False, 5),
    (0, True, False, True, 4),
    (1, True, True, False, 5),
    (1, True, True, True, 5),
    (1, True, False, False, 4),
    (1, True, False, True, 4),
    (1, False, True, False, 4),
    (1, False, True, True, 4),
    (1, False, False, False, 3),
    (1, False, False, True, 3),
    (2, True, True, True, 4),
    (2, True, False, True, 3),
    (2, True, True, False, 3),
    (2, True, False, False, 3),
    (2, False, True, False, 2),
    (2, False, True, True, 2),
    (2, False, False, True, 2),
    (2, False, False, False, 1),
]


@pytest.mark.parametrize("n_ids,full,match,vd,expected", CONFIDENCE_CASES)
def test_confidence_matches_the_previous_decision_tree(
    n_ids, full, match, vd, expected
):
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


# -------------------------------------------------
# tie_scope — the rule the pipeline's takewhile encodes
# -------------------------------------------------
def test_a_clear_winner_ends_the_tie():
    """A lower score behind the leader settles it; later queries are not read."""
    cands = [
        gnd("A", {"gnd_pref_exact": 1.0}),
        gnd("B", {"gnd_pref_exact": 0.7}),
        gnd("C", {"wikidata_label_exact": 1.0}),
    ]
    result = CandidateScorer().score(HANS, cands)
    assert result.top_tier == ["A"]
    assert result.needs_disambiguation is False


def test_no_clear_winner_lets_the_tie_cross_into_the_next_query():
    """Nothing contradicts the leader, so the next query joins the tie."""
    cands = [
        gnd("A", {"gnd_pref_exact": 1.0}),
        gnd("B", {"gnd_pref_exact": 1.0}),
        gnd("C", {"wikidata_label_exact": 1.0}),
    ]
    assert CandidateScorer().score(HANS, cands).top_tier == ["A", "B", "C"]


def test_a_single_hit_does_not_settle_the_question():
    """
    One hit in the best query leaves nothing to stop the run, so the tie
    crosses. This is the common case, not a corner one: every query normalizes
    its own top hit to 1.0.
    """
    cands = [
        gnd("A", {"gnd_pref_exact": 1.0}),
        gnd("C", {"wikidata_label_exact": 1.0}),
        gnd("D", {"wikidata_label_exact": 0.6}),
    ]
    assert CandidateScorer().score(HANS, cands).top_tier == ["A", "C"]


def test_top_tier_scope_keeps_the_tie_inside_one_tier():
    """The alternative: a lower tier can never join the tie."""
    cands = [
        gnd("A", {"gnd_pref_exact": 1.0}),
        gnd("C", {"wikidata_label_exact": 1.0}),
    ]
    policy = ScoringPolicy(tie_scope="top_tier")
    assert CandidateScorer(policy).score(HANS, cands).top_tier == ["A"]
    assert CandidateScorer().score(HANS, cands).top_tier == ["A", "C"]
