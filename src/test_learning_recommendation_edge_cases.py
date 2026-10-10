"""Edge-case tests for GradPath learning recommendations."""

import pandas as pd

from gradpath.learning_recommendations import recommend_learning_actions
from test_learning_recommendations import make_gap


def expect_value_error(function, message):
    try:
        function()
    except ValueError:
        return
    raise AssertionError(message)


# Test 1: A NaN priority score should not break recommendation sorting.
gap = make_gap(priority=float("nan"))
results = recommend_learning_actions([gap], "Data Scientist")
assert isinstance(results, list)
print("1. NaN priority score handled: PASS")


# Test 2: A missing market rank should not break sorting.
gap = make_gap(rank=float("nan"))
results = recommend_learning_actions([gap], "Data Scientist")
assert isinstance(results, list)
print("2. Missing market rank handled: PASS")


# Test 3: Invalid priority text should be rejected clearly.
gap = make_gap(priority="not-a-number")
expect_value_error(
    lambda: recommend_learning_actions([gap], "Data Scientist"),
    "Invalid priority score should raise ValueError.",
)
print("3. Invalid priority rejected: PASS")


# Test 4: String booleans should not be silently interpreted as true.
gap = make_gap(status="insufficient_evidence", incomplete="False")
results = recommend_learning_actions([gap], "Data Scientist")
assert results[0]["extraction_incomplete"] is False
print("4. String boolean handled correctly: PASS")


# Test 5: Invalid resource difficulty labels should be rejected.
resources = pd.read_csv(
    "data/resources/learning_resources.csv", dtype=str
)
resources.loc[resources.index[0], "difficulty"] = "super-easy"
expect_value_error(
    lambda: recommend_learning_actions(
        [make_gap()], "Data Scientist", resources=resources
    ),
    "Invalid difficulty should raise ValueError.",
)
print("5. Invalid resource difficulty rejected: PASS")


# Test 6: Invalid resource types should be rejected.
resources = pd.read_csv(
    "data/resources/learning_resources.csv", dtype=str
)
resources.loc[resources.index[0], "resource_type"] = "video-ish"
expect_value_error(
    lambda: recommend_learning_actions(
        [make_gap()], "Data Scientist", resources=resources
    ),
    "Invalid resource type should raise ValueError.",
)
print("6. Invalid resource type rejected: PASS")


print("All edge-case tests passed.")
