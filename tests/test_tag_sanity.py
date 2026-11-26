from src.postprocess import initialize_found_entry, process_page
from src.tag_sanity import Part, apply_to_name_fields, sanitize_parts


def _names(parts):
    return [(part.role, part.surface) for part in parts]


def test_title_leaves_the_name():
    parts = sanitize_parts(
        [Part("Herr", "LN"), Part("Johann", "FN"), Part("Müller", "LN")]
    )
    assert _names(parts) == [("TL", "Herr"), ("FN", "Johann"), ("LN", "Müller")]


def test_monsieur_initial_leaves_real_initials():
    parts = sanitize_parts(
        [Part("Koch", "LN"), Part("M.", "AB"), Part("J.", "AB"), Part("H.", "AB")]
    )
    assert _names(parts) == [
        ("LN", "Koch"),
        ("TL", "M."),
        ("AB", "J."),
        ("AB", "H."),
    ]


def test_office_and_leading_article_leave_the_surname():
    assert _names(sanitize_parts([Part("Eldin", "LN"), Part("Pafteur", "LN")])) == [
        ("LN", "Eldin"),
        ("OC", "Pafteur"),
    ]
    assert _names(
        sanitize_parts([Part("le", "LN"), Part("Pafteur", "LN"), Part("Haller", "LN")])
    ) == [("OC", "Pafteur"), ("LN", "Haller")]


def test_estate_phrase_moves_to_address_and_von_stays():
    assert _names(
        sanitize_parts(
            [
                Part("von", "LN"),
                Part("Grassenried", "LN"),
                Part("zu", "LN"),
                Part("Carrouge", "LN"),
            ]
        )
    ) == [
        ("LN", "von"),
        ("LN", "Grassenried"),
        ("AN", "zu"),
        ("AN", "Carrouge"),
    ]
    assert _names(
        sanitize_parts([Part("von", "LN"), Part("Graffenried", "LN")])
    ) == [("LN", "von"), ("LN", "Graffenried")]
    assert sanitize_parts([Part("zu", "LN"), Part("Kirchberg", "LN")]) is None


def test_hyphenated_initials_genitive_s_and_glued_forenames():
    assert _names(sanitize_parts([Part("Gruner", "LN"), Part("G-S.", "AB")])) == [
        ("LN", "Gruner"),
        ("AB", "G."),
        ("AB", "S."),
    ]
    assert _names(
        sanitize_parts(
            [
                Part("Tfcharner", "LN"),
                Part("M-B.", "AB"),
                Part("M.", "AB"),
                Part("B.", "AB"),
            ]
        )
    ) == [
        ("LN", "Tfcharner"),
        ("TL", "M."),
        ("AB", "B."),
        ("TL", "M."),
        ("AB", "B."),
    ]
    assert _names(sanitize_parts([Part("MniszechS", "LN"), Part("Michael", "FN")])) == [
        ("LN", "Mniszech"),
        ("FN", "Michael"),
    ]
    assert _names(sanitize_parts([Part("Gottliebludwig", "FN"), Part("Effinger", "LN")])) == [
        ("FN", "Gottlieb"),
        ("FN", "ludwig"),
        ("LN", "Effinger"),
    ]


def test_occupation_abbreviation_becomes_an_initial():
    assert _names(sanitize_parts([Part("Gruner", "LN"), Part("Sig.", "OC")])) == [
        ("LN", "Gruner"),
        ("AB", "Sig."),
    ]


def test_false_friends_stay_names():
    assert _names(sanitize_parts([Part("Herrmann", "LN")])) == [("LN", "Herrmann")]
    assert _names(sanitize_parts([Part("Sauter", "LN"), Part("Anna", "FN")])) == [
        ("LN", "Sauter"),
        ("FN", "Anna"),
    ]


def test_company_suffix_drops_the_span():
    assert (
        sanitize_parts(
            [Part("Hans", "FN"), Part("Müller", "LN"), Part("AG", "LN")]
        )
        is None
    )
    assert sanitize_parts([Part("Credit", "LN"), Part("Suisse", "LN")], ["GmbH"]) is None
    assert (
        sanitize_parts([Part("Maison", "LN"), Part("Dupraz", "LN")], ["S.", "A."])
        is None
    )


def test_apply_to_aggregated_record():
    record = {
        "lastname": "Koch de Thoune",
        "firstname": ["Marquis"],
        "abbr_firstname": ["M.", "J.", "H."],
        "profession": ["Sig."],
        "titles": [],
        "address": [],
    }
    # "de Thoune" stays: only a "zu" phrase is an estate.
    assert apply_to_name_fields(record) is True
    assert record["lastname"] == "Koch de Thoune"
    assert record["firstname"] == []
    assert record["abbr_firstname"] == ["J.", "H.", "Sig."]
    assert record["titles"] == ["Marquis", "M."]


def test_process_page_rewrites_titles_and_drops_companies():
    page = "page1.txt"
    sentences = [
        [
            {"tag": "B-PER-LN", "token": "Herr", "coord": (0, 4)},
            {"tag": "I-PER-FN", "token": "Johann", "coord": (5, 11)},
            {"tag": "I-PER-LN", "token": "Müller", "coord": (12, 18)},
        ],
        [
            {"tag": "B-PER-FN", "token": "Hans", "coord": (0, 4)},
            {"tag": "I-PER-LN", "token": "Müller", "coord": (5, 11)},
            {"tag": "O", "token": "AG", "coord": (12, 14)},
        ],
    ]
    entitylist = []
    process_page(page, sentences, entitylist, [], {page: ("pid", [], "1")}, 1)
    assert len(entitylist) == 1
    info = entitylist[0]["info"]
    assert info["titles"] == ["Herr"]
    assert info["firstnames"] == ["Johann"]
    assert info["lastnames"] == ["Müller"]
    assert initialize_found_entry()["info"].keys() == info.keys()
