# ghast

GHAST (GitHub Actions Static Analysis Tool) is a tool to analyze the security posture of your GitHub Actions.

### See Additional Workflow Examples

#### Specify what branches to run Ghast in

```yaml
name: 'RunGhast'
on:
  push:
    branches:
      - main
      - dev
      - pauls-baseline
jobs:
  RunGhast:
    runs-on: ubuntu-latest
    steps:
    - name: "Checkout repo"
      uses: actions/checkout@96f53100ba2a5449eb71d2e6604bbcd94b9449b5 # v3.5.3
    - name: "Run Ghast"
      uses: "bin3xish477/ghast@ee733379e314d44f1a960a70339ee5e5d19e404d"
```

#### Ignore specific checks

```yaml
name: 'RunGhast'
on:
  push:
jobs:
  RunGhast:
    runs-on: ubuntu-latest
    steps:
    - name: "Checkout repo"
      uses: actions/checkout@96f53100ba2a5449eb71d2e6604bbcd94b9449b5 # v3.5.3
    - name: "Run Ghast"
      uses: "bin3xish477/ghast@ee733379e314d44f1a960a70339ee5e5d19e404d"
      with:
        ignore-checks: 'check_for_inline_script check_for_cache_action_usage'
```

#### Specify directory where Action Workflow files are

```yaml
name: 'RunGhast'
on:
  push:
    paths:
      - '.github/workflows/**'
jobs:
  RunGhast:
    runs-on: ubuntu-latest
    steps:
    - name: "Checkout repo"
      uses: actions/checkout@96f53100ba2a5449eb71d2e6604bbcd94b9449b5 # v3.5.3
    - name: "Run Ghast"
      uses: "bin3xish477/ghast@ee733379e314d44f1a960a70339ee5e5d19e404d"
      with:
        dir: "./actions/"
```

#### Run in verbose mode and don't show tool summary section

```yaml
name: 'RunGhast'
on:
  push:
jobs:
  RunGhast:
    runs-on: ubuntu-latest
    steps:
    - name: "Checkout repo"
      uses: actions/checkout@96f53100ba2a5449eb71d2e6604bbcd94b9449b5 # v3.5.3
    - name: "Run Ghast"
      uses: "bin3xish477/ghast@ee733379e314d44f1a960a70339ee5e5d19e404d"
      with:
        verbose: true
        no-summary: true
```

#### The kitchen sink...

```yaml
name: 'RunGhast'
on:
  push:
    branches:
      - main
      - dev
    paths:
      - '.github/workflows/**'
jobs:
  RunGhast:
    runs-on: ubuntu-latest
    steps:
    - name: "Checkout repo"
      uses: actions/checkout@96f53100ba2a5449eb71d2e6604bbcd94b9449b5 # v3.5.3
    - name: "Run Ghast"
      uses: "bin3xish477/ghast@ee733379e314d44f1a960a70339ee5e5d19e404d"
      with:
        dir: "./actions/"
        verbose: true
        no-summary: true
        ignore-checks: 'check_for_inline_script check_for_cache_action_usage'
```
