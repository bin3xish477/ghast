"""analyzer_test.py: tests for analyzer.py"""
# pylint: disable=missing-function-docstring
from pathlib import Path
import pytest
import yaml

from analyzer.analyzer import Analyzer


@pytest.fixture(name="analyzer")
def analyzer_fixture():
    """Returns instance of Analyzer class as fixture for pytests"""
    return Analyzer()


def test_all_checks(analyzer):
    dir_ = Path("./actions")
    for file_ in dir_.iterdir():
        with open(file_, "r", encoding="utf-8") as action:
            action_dict = yaml.safe_load(action)
            assert analyzer.run_checks(action=action_dict) is True
