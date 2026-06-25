import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from make_review_batches import make_batches, REVIEW_TYPES


def arts(n_product, n_snippet, n_other):
    out = []
    i = 0
    for _ in range(n_product):
        out.append({"id": f"p{i}", "type": "product"}); i += 1
    for _ in range(n_snippet):
        out.append({"id": f"s{i}", "type": "snippet"}); i += 1
    for _ in range(n_other):
        out.append({"id": f"o{i}", "type": "operational"}); i += 1
    return out


def test_only_product_and_snippet_selected():
    targets, batches = make_batches(arts(5, 3, 10), batch_size=10)
    assert len(targets) == 8
    assert all(a["type"] in REVIEW_TYPES for a in targets)


def test_every_target_lands_in_exactly_one_batch():
    a = arts(17, 4, 7)
    targets, batches = make_batches(a, batch_size=10)
    flat = [art["id"] for b in batches for art in b]
    assert len(flat) == len(targets) == 21
    assert len(set(flat)) == 21  # no dupes, no drops -> full coverage


def test_batch_sizing():
    _, batches = make_batches(arts(25, 0, 0), batch_size=10)
    assert [len(b) for b in batches] == [10, 10, 5]


def test_empty_when_no_reviewable_types():
    targets, batches = make_batches(arts(0, 0, 12), batch_size=10)
    assert targets == [] and batches == []
