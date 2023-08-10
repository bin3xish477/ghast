"""analyzer.py contains all the INFOic related to analyzing GitHub Actions"""

from re import search, DOTALL
from pathlib import Path
from colors import Colors

import analyzer.regex


class Analyzer:
    """Analyzer contains all the checks that will run
    against a specified GitHub Action parsed into a Python
    dictionary.
    """

    def __init__(
        self,
        ignore_checks: list,
        ignore_warnings: bool = False,
        verbose: bool = False,
    ) -> None:
        self.ignore_warnings = ignore_warnings
        self.ignore_checks = ignore_checks or []
        self.verbose = verbose
        self.checks = {
            "_check_for_3p_actions_without_hash": {"level": "FAIL"},
            "_check_for_allow_unsecure_commands": {"level": "FAIL"},
            "_check_for_cache_action": {"level": "WARN"},
            "_check_for_upload_download_artifact_action": {"level": "WARN"},
            "_check_for_dangerous_write_permissions": {"level": "FAIL"},
            "_check_for_inline_script": {"level": "WARN"},
            "_check_for_pull_request_target": {"level": "FAIL"},
            "_check_for_script_injection": {"level": "FAIL"},
            "_check_for_self_hosted_runners": {"level": "WARN"},
            "_check_for_aws_configure_credentials_non_oidc": {"level": "WARN"},
            "_check_for_create_or_approve_pull_request": {"level": "FAIL"},
            "_check_for_remote_script": {"level": "WARN"},
            "_check_for_non_github_managed_actions": {"level": "WARN"},
        }
        self.auxiliary_checks = [
            "_check_for_missing_codeowners_file",
            "_check_for_missing_security_md_file",
        ]
        self.action = {}
        self.jobs = {}

        self._run_aux_checks()

    def _print_failed_check_msg(self, check: str, level: str):
        color = None
        if level == "FAIL":
            color = Colors.RED
        elif level == "WARN":
            color = Colors.LIGHT_GREEN
        print(
            f"{color}{level}{Colors.END} {Colors.YELLOW}{check[1:]}{Colors.END}",
        )

    def _action_has_required_elements(self) -> bool:
        passed = True
        # NOTE: a check for "permissions" is not done here because it is not required
        if not all(key in self.action for key in ["name", "on", "jobs"]):
            passed = False
        for job in self.jobs.keys():
            if "steps" not in self.jobs[job]:
                passed = False
                break
        return passed

    def _check_for_3p_actions_without_hash(self) -> bool:
        passed = True
        for job in self.jobs.keys():
            for step in self.jobs[job]["steps"]:
                if "uses" in step:
                    uses = step["uses"]
                    if search(analyzer.regex.ACTION_WITH_VERSION, uses):
                        if self.verbose:
                            print(
                                f"{Colors.LIGHT_GRAY}INFO{Colors.END} step using action('{uses}') with version number instead of a SHA hash"
                            )
                        if passed:
                            passed = False
        return passed

    def _check_for_inline_script(self) -> bool:
        passed = True
        for job in self.jobs.keys():
            steps = self.jobs[job]["steps"]
            for step in steps:
                if "run" in step:
                    if self.verbose:
                        # NOTE: name is not required according to GitHub Docs: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#name
                        if 'name' in step:
                            print(
                                f"{Colors.LIGHT_GRAY}INFO{Colors.END} found inline script in job('{job}').step('{step['name']}')"
                            )
                        else:
                            print(f"{Colors.LIGHT_GRAY}INFO{Colors.END} found step with inline script in job('{job}')")
                    passed = False
        return passed

    def _check_for_script_injection(self) -> bool:
        passed = True
        for job in self.jobs.keys():
            steps = self.jobs[job]["steps"]
            for step in steps:
                if "run" in step:
                    script = step["run"]
                    variable = search(analyzer.regex.DANGEROUS_GITHUB_CONTEXT_VARIABLE, script)
                    if variable:
                        if self.verbose:
                            print(
                                f"{Colors.LIGHT_GRAY}INFO{Colors.END} dangerous variable('{variable.group()}') in inline script"
                            )
                        passed = False
        return passed

    def _check_for_allow_unsecure_commands(self) -> bool:
        passed = True
        for job in self.jobs.keys():
            steps = self.jobs[job]["steps"]
            for step in steps:
                if "env" in step and "ACTIONS_ALLOW_UNSECURE_COMMANDS" in step["env"]:
                    if self.verbose:
                        if "name" in step:
                            print(
                                f"{Colors.LIGHT_GRAY}INFO{Colors.END} step('{step['name']}') contains dangerous ACTIONS_ALLOW_UNSECURE_COMMANDS environment variable"
                            )
                        else:
                            print(
                                f"{Colors.LIGHT_GRAY}INFO{Colors.END} step contains dangerous ACTIONS_ALLOW_UNSECURE_COMMANDS environment variable"
                            )
                    if passed:
                        passed = False
        return passed

    def _check_for_pull_request_target(self) -> bool:
        passed = True
        event_triggers = self.action["on"]
        if type(event_triggers) in (list, dict):
            if "pull_request_target" in event_triggers:
                passed = False
        elif isinstance(event_triggers, str):
            if event_triggers == "pull_request_target":
                passed = False
        return passed

    def _check_for_remote_script(self) -> bool:
        passed = True
        for job in self.jobs.keys():
            steps = self.jobs[job]["steps"]
            for step in steps:
                if "run" in step:
                    script = step["run"]
                    variable = search(analyzer.regex.POTENTIAL_REMOTE_SCRIPT, script)
                    if variable:
                        if self.verbose:
                            print(
                                f"{Colors.LIGHT_GRAY}INFO{Colors.END} remote script('{variable.group()}') found in inline script"
                            )
                        passed = False
        return passed

    def _check_for_cache_action(self) -> bool:
        passed = True
        for job in self.jobs.keys():
            steps = self.jobs[job]["steps"]
            for step in steps:
                if "uses" in step:
                    action = search(analyzer.regex.CACHE_ACTION, step["uses"])
                    if action:
                        if self.verbose:
                            print(
                                f"{Colors.LIGHT_GRAY}INFO{Colors.END} job('{job}') is using cache action('{action.group()}')"
                            )
                        passed = False
        return passed

    def _check_for_upload_download_artifact_action(self) -> bool:
        passed = True
        for job in self.jobs.keys():
            steps = self.jobs[job]["steps"]
            for step in steps:
                if "uses" in step:
                    action = search(analyzer.regex.UPLOAD_DOWNLOAD_ARTIFACTS_ACTION, step["uses"])
                    if action:
                        if self.verbose:
                            print(
                                f"{Colors.LIGHT_GRAY}INFO{Colors.END} job('{job}') is using upload|download artifact action('{action.group()}')"
                            )
                        passed = False
        return passed

    def _check_for_dangerous_write_permissions(self) -> bool:
        passed = True
        dangerous_scopes = ["contents", "deployments", "packages", "actions"]

        if "permissions" in self.action:
            permissions = self.action["permissions"]
            # check for write to all scopes
            if permissions == "write-all":
                passed = False
                return passed
            for scope in dangerous_scopes:
                if scope in permissions and permissions[scope] == "write":
                    passed = False
                    return passed

        for job in self.jobs.keys():
            if "permissions" in self.jobs[job]:
                permissions = self.jobs[job]["permissions"]
                if permissions == "write-all":
                    passed = False
                    if self.verbose:
                        print(f"{Colors.LIGHT_GRAY}INFO{Colors.END} job('{job}') contains 'write-all' permissions")
                for scope in dangerous_scopes:
                    if scope in permissions and permissions[scope] == "write":
                        if self.verbose:
                            print(
                                f"{Colors.LIGHT_GRAY}INFO{Colors.END} write permissions set for dangerous scope('{scope}')"
                            )
                        passed = False
                        return passed
        return passed

    def _check_for_self_hosted_runners(self) -> bool:
        passed = True
        # NOTE: ***** default runners as of 7/17/23 *****
        default_runners = [
            "windows-latest",
            "windows-2022",
            "windows-2019",
            "ubuntu-latest",
            "ubuntu-22.04",
            "ubuntu-20.04",
            "macos-13",
            "macos-13-xl",
            "macos-latest",
            "macos-12",
            "macos-latest-xl",
            "macos-12-xl",
            "macos-11",
        ]
        for job in self.jobs.keys():
            # TODO: Add verbosity to print which self-hosted runners were found.
            if "strategy" in self.jobs[job] and "matrix" in self.jobs[job]["strategy"]:
                matrix = self.jobs[job]["strategy"]["matrix"]
                if "runner" in matrix:
                    if isinstance(matrix["runner"], list):
                        if any(runner not in default_runners for runner in matrix["runner"]):
                            passed = False
                            break
            if "runs-on" in self.jobs[job]:
                runs_on = self.jobs[job]["runs-on"]
                type_of_runs_on = type(runs_on)
                if type_of_runs_on == list:
                    if any(runner not in default_runners for runner in runs_on):
                        passed = False
                        return passed
                elif type_of_runs_on == dict:
                    if "group" in runs_on:
                        if runs_on["group"] not in default_runners:
                            passed = False
                            break
                elif type_of_runs_on == str:
                    if runs_on not in default_runners:
                        passed = False
                        break
        return passed

    def _check_for_aws_configure_credentials_non_oidc(self) -> bool:
        passed = True
        # NOTE: if these are specifed in the configure-aws-credentials action
        # then the action will not use GitHub's OIDC provider
        # see this: https://github.com/aws-actions/configure-aws-credentials#assuming-a-role
        non_oidc_inputs = [
            "aws-access-key-id",
            "web-identity-token-file",
        ]
        for job in self.jobs.keys():
            steps = self.jobs[job]["steps"]
            for step in steps:
                if "uses" in step:
                    action = search(analyzer.regex.CONFIGURE_AWS_CREDS_ACTION, step["uses"])
                    if action:
                        if any(input in non_oidc_inputs for input in step["with"]):
                            if self.verbose:
                                if "name" in step:
                                    print(
                                        f"{Colors.LIGHT_GRAY}INFO{Colors.END} found step('{step['name']}') not using OIDC with `configure-aws-credentials`"
                                    )
                                else:
                                    print(
                                        f"{Colors.LIGHT_GRAY}INFO{Colors.END} found step not using OIDC with `configure-aws-credentials`"
                                    )
                        if passed:
                            passed = False
        return passed

    def _check_for_create_or_approve_pull_request(self) -> bool:
        passed = True

        def __print_msg(job: str, step: dict):
            if self.verbose:
                if "name" in step:
                    print(
                        f"{Colors.LIGHT_GRAY}INFO{Colors.END} job('{job}') has a step('{step['name']}') that creates or approves a pull request"
                    )
                else:
                    print(
                        f"{Colors.LIGHT_GRAY}INFO{Colors.END} job('{job}') has a step that creates or approves a pull request"
                    )

        for job in self.jobs:
            steps = self.jobs[job]["steps"]
            for step in steps:
                if "run" in step:
                    script = step["run"]
                    match = search(analyzer.regex.GH_CLI_PR_CREATE_APPROVE, script, flags=DOTALL) or search(
                        analyzer.regex.CURL_CREATE_APPROVE_PR, script, flags=DOTALL
                    )
                    if match:
                        __print_msg(job, step)
                        passed = False
                if "uses" in step:
                    action = search(analyzer.regex.GITHUB_SCRIPT_ACTION, step["uses"])
                    if action:
                        if "script" in step["with"]:
                            script = step["with"]["script"]
                            match = search(analyzer.regex.GITHUB_SCRIPT_CREATE_APPROVE_PR, script, flags=DOTALL)
                            if match:
                                __print_msg(job, step)
                                passed = False
        return passed

    def _check_for_non_github_managed_actions(self) -> bool:
        passed = True
        for job in self.jobs:
            for step in self.jobs[job]["steps"]:
                if "uses" in step:
                    action = step["uses"].strip()
                    if not search(analyzer.regex.GITHUB_MANAGED_ACTION, action):
                        if self.verbose:
                            print(
                                f"{Colors.LIGHT_GRAY}INFO{Colors.END} using non GitHub-managed action('{action}') - make sure its safe to use!"
                            )
                        passed = False
        return passed

    # ==================================================================
    # ======================== Auxiliary Checks ========================
    # ==================================================================

    def _check_for_missing_codeowners_file(self) -> None:
        if not Path(".github/workflows/CODEOWNERS").exists():
            print(
                f"{Colors.LIGHT_BLUE}AUXI{Colors.END} missing CODEOWNERS file"
                " which can provide additional protections for your workflow files."
            )
        else:
            if self.verbose:
                print(f"{Colors.LIGHT_BLUE}AUXI{Colors.END} found CODEOWNERS file!")

    def _check_for_missing_security_md_file(self) -> None:
        security_md = 'SECURITY.md'
        if not Path(security_md).exists() or not Path(security_md.lower()).exists():
            print(
                f"{Colors.LIGHT_BLUE}AUXI{Colors.END} missing SECURITY.md file"
                " which is crucial for researchers looking to report a finding."
            )
        else:
            if self.verbose:
                print(f"{Colors.LIGHT_BLUE}AUXI{Colors.END} found SECURITY.md file!")

    def _run_aux_checks(self) -> None:
        """Runs auxiliary checks which are checks for security-related
        configurations/properties/mechanisms that contribute to more secure
        GitHub Actions workflows.
        """
        # TODO:
        # - Add check for missing dockerignore/gitignore file with missing sensitive file based on programming language detected
        for check in self.auxiliary_checks:
            Analyzer.__dict__[check](self)

    def get_checks(self) -> list:
        """Returns list containing available checks.

        Returns:
            list: list() of available checks.
        """
        return [*self.checks.keys()]

    def run_checks(self, action: dict) -> bool:
        """Run checks against a parsed Action YAML file as dict.

        Args:
            action (dict): the dict containing the parsed Action YAML file data.

        Returns:
            bool: True, if all checks passed, False, if any check fails.
        """
        self.action = action
        self.jobs = self.action["jobs"]

        passed_all_checks = True
        fail_checks = []
        if self._action_has_required_elements():
            for check in self.checks:
                if self.ignore_warnings:
                    if self.checks[check]["level"] == "WARN":
                        continue
                if check[1:] in self.ignore_checks:
                    continue
                if not Analyzer.__dict__[check](self):
                    fail_checks.append(check)
                    if passed_all_checks:
                        passed_all_checks = False
            for check in fail_checks:
                self._print_failed_check_msg(check, self.checks[check]["level"])
        return passed_all_checks
