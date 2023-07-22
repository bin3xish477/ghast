"""analyzer.py contains all the INFOic related to analyzing GitHub Actions"""
from colors import Colors
from re import match


class Analyzer:
    """Analyzer contains all the checks that will run
    against a specified GitHub Action parsed into a Python
    dictionary.
    """

    def __init__(self, verbose: bool = False, ignore_warnings: bool = False) -> None:
        self.verbose = verbose
        self.ignore_warnings = ignore_warnings
        self.checks = {
            "_check_for_3p_actions_without_hash": {"level": "FAIL"},
            "_check_for_allow_unsecure_commands": {"level": "FAIL"},
            "_check_for_cache_action_usage": {"level": "WARN"},
            "_check_for_dangerous_write_permissions": {"level": "FAIL"},
            "_check_for_inline_script": {"level": "WARN"},
            "_check_for_pull_request_target": {"level": "FAIL"},
            "_check_for_script_injection": {"level": "FAIL"},
            "_check_for_self_hosted_runners": {"level": "WARN"},
            "_check_for_aws_configure_credentials_non_oidc": {"level": "WARN"},
        }
        self.action = {}

    def _print_failed_check_msg(self, check: str, level: str):
        if level == "FAIL":
            level_color = Colors.RED
        elif level == "WARN":
            level_color = Colors.LIGHT_GREEN
        else:
            level_color = Colors.LIGHT_PURPLE
        print(
            f"{level_color}{level}{Colors.END} {Colors.YELLOW}{check[1:]}{Colors.END}",
        )

    def _action_has_required_elements(self) -> bool:
        passed = True
        # a check for "permissions" is not done here because it is not required
        if not all(key in self.action for key in ["name", "on", "jobs"]):
            passed = False
        for job in self.jobs.keys():
            if "steps" not in self.jobs[job]:
                passed = False
                break
        return passed

    def _check_for_3p_actions_without_hash(self) -> bool:
        passed = True
        ACTION_WITH_VERSION_REGEX = r"([\w-]+)\/([\w-]+)@v\d+(\.\d+)?(\.\d+)?"
        for job in self.jobs.keys():
            for step in self.jobs[job]["steps"]:
                if "uses" in step:
                    uses = step["uses"]
                    if match(ACTION_WITH_VERSION_REGEX, uses):
                        if self.verbose:
                            print(
                                f"{Colors.LIGHT_GRAY}INFO{Colors.END} step using action('{uses}') with version number instead of a SHA hash"
                            )
                        passed = False
                        break
        return passed

    def _check_for_inline_script(self) -> bool:
        passed = True
        for job in self.jobs.keys():
            steps = self.jobs[job]["steps"]
            for step in steps:
                if "run" in step:
                    if self.verbose:
                        print(
                            f"{Colors.LIGHT_GRAY}INFO{Colors.END} found inline script in job('{job}').step('{step['name']}')"
                        )
                    passed = False
        return passed

    def _check_for_script_injection(self) -> bool:
        passed = True
        DANGEROUS_GITHUB_CONTEXT_VARIABLE_REGEX = r"\$\{\{.*github.+\}\}"
        for job in self.jobs.keys():
            steps = self.jobs[job]["steps"]
            for step in steps:
                if "run" in step:
                    script = step["run"]
                    variable = match(DANGEROUS_GITHUB_CONTEXT_VARIABLE_REGEX, script)
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
                        print(
                            f"{Colors.LIGHT_GRAY}INFO{Colors.END} step('{step['name']}') contains dangerous ACTIONS_ALLOW_UNSECURE_COMMANDS environment variable"
                        )
                    passed = False
                    return passed
        return passed

    def _check_for_pull_request_target(self) -> bool:
        passed = True
        event_triggers = self.action["on"]
        if type(event_triggers) in (list, dict):
            if "pull_request_target" in event_triggers:
                passed = False
        elif type(event_triggers) == str:
            if event_triggers == "pull_request_target":
                passed = False
        return passed

    def _check_for_cache_action_usage(self) -> bool:
        passed = True
        CACHE_ACTION_REGEX = r"actions\/cache@(v\d+(\.\d+)?(\.\d+)?|[a-f0-9]{40})"
        for job in self.jobs.keys():
            steps = self.jobs[job]["steps"]
            for step in steps:
                if "uses" in step:
                    action = match(CACHE_ACTION_REGEX, step["uses"])
                    if action:
                        if self.verbose:
                            print(
                                f"{Colors.LIGHT_GRAY}INFO{Colors.END} job('{job}') is using cache action('{action.group()}')"
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
        # ***** default runners as of 7/17/23 *****
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
            if "strategy" in self.jobs[job] and "matrix" in self.jobs[job]["strategy"]:
                matrix = self.jobs[job]["strategy"]["matrix"]
                if "runner" in matrix:
                    if type(matrix["runner"]) == list:
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

    def _check_for_aws_configure_credentials_non_oidc(self):
        passed = True
        # if these are specifed in the configure-aws-credentials action
        # then the action will not use GitHub's OIDC provider
        # see this: https://github.com/aws-actions/configure-aws-credentials#assuming-a-role
        CONFIGURE_AWS_CREDS_ACTION_REGEX = (
            r"aws\-actions\/configure\-aws\-credentials@(v\d+(\.\d+)?(\.\d+)?|[a-f0-9]{40})"
        )
        non_oidc_inputs = [
            "aws-access-key-id",
            "web-identity-token-file",
        ]
        for job in self.jobs.keys():
            steps = self.jobs[job]["steps"]
            for step in steps:
                if "uses" in step:
                    action = match(CONFIGURE_AWS_CREDS_ACTION_REGEX, step["uses"])
                    if action:
                        if any(input in non_oidc_inputs for input in step["with"]):
                            if self.verbose:
                                print(
                                    f"{Colors.LIGHT_GRAY}INFO{Colors.END} found step('{step['name']}') not using OIDC with `configure-aws-credentials`"
                                )
                        if passed:
                            passed = False
        return passed

    def get_checks(self) -> list:
        """Returns all available checks performed against
        provided GitHub Action.

        Returns:
            list: all available checks performed by Analzyer
        """
        return [*self.checks.keys()]

    def run_checks(self, action: dict) -> bool:
        """Run all checks against a GitHub Action

        Args:
            action (dict): the dict representation of the Action YAML file.

        Returns:
            bool: returns False if any checks fails.
        """

        self.action = action
        self.jobs = self.action["jobs"]

        passed_all_checks = True
        fail_checks = []
        if self._action_has_required_elements():
            for check in self.checks.keys():
                if self.ignore_warnings:
                    if self.checks[check]["level"] == "WARN":
                        continue
                if not Analyzer.__dict__[check](self):
                    fail_checks.append(check)
                    if passed_all_checks:
                        passed_all_checks = False
            for check in fail_checks:
                self._print_failed_check_msg(check, self.checks[check]["level"])
        return passed_all_checks
