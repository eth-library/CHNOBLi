import pytest
from src.evaluation import (
    execute_evaluation
)


# -------------------------------------------------
# 1. Test execute_evaluation
# All this function does is call evaluate person which is tested in
# test_evaluation_utils and then it saves a json which is tested in
# evaluation_utils as well.
# -------------------------------------------------
def test_execute_evaluation():
    with pytest.raises(Exception) as excinfo:
        execute_evaluation([None], None, None)
    assert str(excinfo.value) == "no path to ground truth was passed"
