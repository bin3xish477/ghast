# asa
asa (actions-security-analzyer) is a tool to analyze the security posture of your GitHub Actions.

### Installation

> Make sure you `~/.local/bin` in your PATH!

```
pip install asa
```

### Usage

```
asa --file action.yml
asa -d directory-with-actions/ --verbose
asa --file action.yml --ignore-warnings
asa --list-checks
```

### References

- [Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
