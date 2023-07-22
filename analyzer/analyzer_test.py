"""analyzer_test.py: tests for analyzer.py"""
# pylint: disable=missing-function-docstring
import pytest
import yaml

from analyzer.analyzer import Analyzer


@pytest.fixture(name="analyzer")
def analyzer_fixture():
    """Returns instance of Analyzer class as fixture for pytests"""
    return Analyzer()


def test_check_for_3p_actions_without_hash(analyzer) -> None:
    with open("actions/action-using-configure-aws-creds-non-oidc-auth.yml", "r", encoding="utf-8") as action:
        action_dict = yaml.safe_load(action)
        assert analyzer.run_checks(action=action_dict) is True


def test_check_for_script_injection(analyzer) -> None:
    with open("actions/action-with-dangerous-gh-context-variables.yml", "r", encoding="utf-8") as action:
        action_dict = yaml.safe_load(action)
        assert analyzer.run_checks(action=action_dict) is True


def test_check_for_unsecure_commands(analyzer) -> None:
    with open("actions/action-with-unsecure-command-env-var.yml", "r", encoding="utf-8") as action:
        action_dict = yaml.safe_load(action)
        assert analyzer.run_checks(action=action_dict) is True


def test_check_for_pull_request_target(analyzer) -> None:
    with open("actions/action-with-pull-request-target.yml", "r", encoding="utf-8") as action:
        action_dict = yaml.safe_load(action)
        assert analyzer.run_checks(action=action_dict) is True


def test_check_for_inline_script(analyzer) -> None:
    with open("actions/action-with-inline-script.yml", "r", encoding="utf-8") as action:
        action_dict = yaml.safe_load(action)
        assert analyzer.run_checks(action=action_dict) is True


def test_check_for_cache_action_usage(analyzer) -> None:
    with open("actions/action-using-github-cache.yml", "r", encoding="utf-8") as action:
        action_dict = yaml.safe_load(action)
        assert analyzer.run_checks(action=action_dict) is True


def test_check_for_self_hosted_runners(analyzer) -> None:
    with open("actions/action-using-self-hosted-runners.yml", "r", encoding="utf-8") as action:
        action_dict = yaml.safe_load(action)
        assert analyzer.run_checks(action=action_dict) is True

    with open("actions/action-using-self-hosted-runner-referenced-by-group.yml", "r", encoding="utf-8") as action:
        action_dict = yaml.safe_load(action)
        assert analyzer.run_checks(action=action_dict) is True


def test_check_for_dangerous_write_permissions(analyzer) -> None:
    with open("actions/action-with-write-permissions-all-jobs.yml", "r", encoding="utf-8") as action:
        action_dict = yaml.safe_load(action)
        assert analyzer.run_checks(action=action_dict) is True

    with open("actions/action-with-write-permissions-one-job.yml", "r", encoding="utf-8") as action:
        action_dict = yaml.safe_load(action)
        assert analyzer.run_checks(action=action_dict) is True

    with open("actions/action-with-write-all-permissions.yml", "r", encoding="utf-8") as action:
        action_dict = yaml.safe_load(action)
        assert analyzer.run_checks(action=action_dict) is True
