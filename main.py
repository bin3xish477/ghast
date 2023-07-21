"""main.py for actions-security-analyzer"""
from argparse import ArgumentParser
from pathlib import Path
from os import sep
from analyzer.analyzer import Analyzer
from colors import Colors
from yaml.resolver import Resolver
from yaml import safe_load, YAMLError
from sys import exit

FAILED = 1
SUCCESS = 0


def _rewrite_pyyaml_boolean_recognition_rules():
    for ch in "OoYyNn":
        if len(Resolver.yaml_implicit_resolvers[ch]) == 1:
            del Resolver.yaml_implicit_resolvers[ch]
        else:
            Resolver.yaml_implicit_resolvers[ch] = [
                x for x in Resolver.yaml_implicit_resolvers[ch] if x[0] != "tag:yaml.org,2002:bool"
            ]


def _parse_args():
    parser = ArgumentParser()
    parser.add_argument("--file", "-f", type=str, help="path to GitHub Action .yaml|.yml file")
    parser.add_argument(
        "--dir",
        "-d",
        type=str,
        help="path to directory with GitHub Action .yaml|.yml files",
    )
    parser.add_argument(
        "--list-checks",
        "-l",
        action="store_true",
        help="list all checks performed against provided GitHub Action",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="increase tool verbosity")
    parser.add_argument(
        "--ignore-warnings",
        "-i",
        action="store_true",
        help="ignore checks labeled as warning",
    )
    return parser.parse_args()


def _main():
    _rewrite_pyyaml_boolean_recognition_rules()
    args = _parse_args()

    file_ = args.file
    dir_ = args.dir
    list_checks = args.list_checks
    verbose = args.verbose
    ignore_warnings = args.ignore_warnings

    analyzer = Analyzer(ignore_warnings=ignore_warnings, verbose=verbose)

    errored = False
    failed_actions = []
    try:
        if file_:
            file_ = Path(file_)
            if file_.exists():
                print(f"FILE: {Colors.BOLD}{file_}{Colors.END}")
                with file_.open("r") as action_file:
                    action_dict = safe_load(action_file)
                    if not analyzer.run_checks(action=action_dict):
                        failed_actions.append(file_)
            else:
                errored = True
                print(f"[{Colors.RED}ERROR{Colors.END}]: the file '{str(file_)}' does not exist...")
            print()
        elif dir_:
            dir_ = Path(dir_)
            if dir_.is_dir() and dir_.exists():
                if verbose:
                    print(
                        f"{Colors.LIGHT_GRAY}INFO{Colors.END} "
                        f"Scanning {Colors.UNDERLINE}{dir_}{Colors.END} directory..."
                    )
                for action in dir_.iterdir():
                    print(f"File: {Colors.BOLD}{str(action).rsplit(sep, maxsplit=1)[-1]}{Colors.END}")
                    if action.is_file and action.suffix in (".yml", ".yaml"):
                        with action.open("r") as action_file:
                            action_dict = safe_load(action_file)
                            if not analyzer.run_checks(action=action_dict):
                                failed_actions.append(action)
                            else:
                                if verbose:
                                    print(f"{Colors.LIGHT_GRAY}INFO{Colors.END} {str(action)} passed all checks")
                    print()
            else:
                errored = True
                print(f"[{Colors.RED}ERROR{Colors.END}] the directory '{str(dir_)}' does not exist...")
        elif list_checks:
            for i, check in enumerate(analyzer.get_checks(), 1):
                print(f"{i}. {check[1:]}")
        else:
            errored = True
            print(f"[{Colors.LIGHT_GRAY}INFO{Colors.END}] must provide `--file` or `--dir`")

    except (FileNotFoundError, KeyError, YAMLError) as exception:
        errored = True
        print(f"[{Colors.RED}ERROR{Colors.END}] {exception}")
    finally:
        if not errored and not list_checks:
            if failed_actions:
                print(
                    f"{Colors.PURPLE}{Colors.UNDERLINE}Summary{Colors.END}"
                    "\nThe following Actions failed to pass one or more checks:"
                )
                for action in failed_actions:
                    print(f" \u2022 {Colors.BOLD}{action}{Colors.END}")
                exit(FAILED)
            else:
                print(f"{Colors.PURPLE}Summary{Colors.END}: Passed all checks \U0001F44D")
                exit(SUCCESS)


if __name__ == "__main__":
    _main()
