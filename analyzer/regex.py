""" regex.py """

ACTION_WITH_VERSION = r"([\w-]+)\/([\w-]+)@v\d+(\.\d+)?(\.\d+)?"
DANGEROUS_GITHUB_CONTEXT_VARIABLE = r"\$\{\{.*github.+\}\}"
POTENTIAL_REMOTE_SCRIPT = (
    r"((?<=[^a-zA-Z0-9])(?:https?\:\/\/|[a-zA-Z0-9]{1,}\.{1}|\b)(?:\w{1,}\.{1})"
    r"{1,5}(?:com|org|edu|gov|uk|net|ca|de|jp|fr|au|us|ru|ch|it|nl|se|no|es|mil|iq|io|ac|ly|sm){1}(?:\/[a-zA-Z0-9.-_]{1,})*)"
)
CACHE_ACTION = r"actions\/cache@(v\d+(\.\d+)?(\.\d+)?|[a-f0-9]{40})"
UPLOAD_DOWNLOAD_ARTIFACTS_ACTION = r"actions\/(upload|download)\-artifact@(v\d+(\.\d+)?(\.\d+)?|[a-f0-9]{40})"
CONFIGURE_AWS_CREDS_ACTION = r"aws\-actions\/configure\-aws\-credentials@(v\d+(\.\d+)?(\.\d+)?|[a-f0-9]{40})"
GH_CLI_PR_CREATE_APPROVE = r"gh pr (review.*--approve|create.*)"
GITHUB_SCRIPT_ACTION = r"actions\/github\-script@(v\d+(\.\d+)?(\.\d+)?|[a-f0-9]{40})"
GITHUB_SCRIPT_CREATE_APPROVE_PR = r".*github\.rest\.pulls\.(create\(.*|reviews\(.*APPROVE.*)"
CURL_CREATE_APPROVE_PR = (
    r".*curl.*https:\/\/api\.github\.com\/repos\/[0-9a-zA-Z-._]+\/[0-9a-zA-Z-._]+\/pulls\/[0-9]{1,}\/reviews.*"
)
GITHUB_MANAGED_ACTION = r"^actions\/.*"
