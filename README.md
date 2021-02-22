# salt-template

This repository provides salt template files and module functions to serialize data and text into configuration files.

## Examples

```yaml
/etc/default/application:
  file.managed:
    - template: py
    - source: salt://_templates/env.py
    - context:
        # Default config data to merge with pillar data
        default:
          LOG_LEVEL: debug

        # Load data from one or multiple pillar keys and merge
        source:
          - env:default
          - env:application
```

```yaml
/etc/systemd/system/application.service:
  file.managed:
    - template: py
    - source: salt://_templates/systemd.py
    - context:
        default:
          Unit:
            Description: My Demo Application
          Service:
            EnvironmentFile: -/etc/default/application
            ExecStart: /usr/local/bin/application -l $LOG_LEVEL
```

```yaml
/rails/config/database.yaml:
  file.managed:
    - template: py
    - source: salt://_templates/yaml2.py
    - context:
        source: myapp:rails:database
        root: production
```

## Installation

The recommended installation uses salt `GitFS` to include this repository into your state tree:

```yaml
gitfs_remotes:
  - https://github.com/jgraichen/salt-template.git:
      - base: v1.0.0
```

It is recommended to checkout a specific revision to avoid getting unexpected updates or changes.


## Templates

The repository ships a set of Python templates to serialize different kind of files. The can be used via e.g. `file.managed`. Templates accept configuration via the `context` option.

All templates accept a `source` and a `default` option. Some templates have more options to tweak things specific to them. They all use [`template.managed`](#templatemanaged) to render the final output, see [here](#templatemanaged) for details and more options.

<dl>
<dt>

`source` (str, list, optional)

<dd>

A comma-separated string or a list of pillar keys to load data from. The pillar values will be recursively merged, lists will be concatenated.

```yaml
/etc/salt/minion.d/minion.conf:
  file.managed:
    - template: py
    - source: salt://_templates/yaml2.py
    - context:
        source:
          - salt:common
          - salt:minion
```

<dt>

`default` (optional)

<dd>

Some default data to use with the template. If an additional `source` is specified, it will be merged into the default data.

```yaml
/etc/salt/minion.d/minion.conf:
  file.managed:
    - template: py
    - source: salt://_templates/yaml2.py
    - context:
        default:
          log_level: INFO
        source: salt:minion
```

Using `default` without `source` only renders the given default data.

</dl>


### Environment

Renders a single-level dictionary into an environment file.

```yaml
/etc/default/application:
  file.managed:
    - template: py
    - source: salt://_templates/env.py
    - context:
        default:
          KEY: 1
          LONG_VALUE: |
            Long string
            on multiple lines
```

```
# This file is managed by salt. Changes will be overwritten.

KEY=1
LONG_VALUE='Long string
on multiple lines'
```


### Sysctl

Renders a sysctl-like configuration with additional list suppport.

```yaml
/etc/rabbitmq/rabbitmq.conf:
  file.managed:
    - template: py
    - source: salt://_templates/sysctl.py
    - context:
        default:
            cluster_formation.peer_discovery_backend: classic_config
            cluster_formation.classic_config.nodes:
              - rabbit@hostname1.example.org
              - rabbit@hostname2.example.org
```

```
# This file is managed by salt. Changes will be overwritten.

cluster_formation.peer_discovery_backend = classic_config
cluster_formation.classic_config.nodes.1 = rabbit@hostname1.example.org
cluster_formation.classic_config.nodes.2 = rabbit@hostname2.example.org
```

*Note:* List index starts with `1`.


### Systemd

Renders a file using an [`systemd.syntax`](https://www.freedesktop.org/software/systemd/man/systemd.syntax.html) approximation.

```yaml
/etc/systemd/system/application.service.d/override.conf:
  file.managed:
    - template: py
    - source: salt://_templates/systemd.py
    - context:
        default:
          Unit:
            After: consul.service
          Service:
            Environment: KEY=1
            ExecStart: [Null, /usr/local/bin/application]
```

```
# This file is managed by salt. Changes will be overwritten.

[Unit]
After=consul.service

[Service]
Environment=KEY=1
ExecStart=
ExecStart=/usr/local/bin/application
```

#### Additional arguments

<dl>
<dt>

`section` (str, optional)

<dd>

Render the given data as a flat dictionary into the given section.

```yaml
/etc/systemd/resolved.conf.d/override.conf:
  file.managed:
    - template: py
    - source: salt://_templates/systemd.py
    - context:
        default:
          DNS: 127.0.0.1
          Domains: ~consul
        section: Resolve
```

```
# This file is managed by salt. Changes will be overwritten.

[Resolve]
DNS=127.0.0.1
Domains=~consul
```

</dl>


### Text

Renders a list of text blobs into a combined file.

```yaml
/etc/application/config:
  file.managed:
    - template: py
    - source: salt://_templates/text.py
    - context:
        default: |
          First blob.
        source:
          - pillar:key:one
          - pillar:key:two
```

```
# This file is managed by salt. Changes will be overwritten.

First blob.


# pillar:key:one

Blob from first pillar key.


# pillar:key:two

Blob from second pillar key.
```

*Note:* The text template recognizes `comment_prefix` from [`template.managed`](#templatemanaged) and uses this to prefix source comments.


### Yaml2

Renders into a YAML document.

```yaml
/etc/application/config.yaml:
  file.managed:
    - template: py
    - source: salt://_templates/yaml2.py
    - context:
        default:
          database:
            host: 127.0.0.1
            port: 1234
        source: pillar:key
```

```yaml
# This file is managed by salt. Changes will be overwritten.

database:
  host: 127.0.0.1
  port: 1234
  name: from_pillar
```

#### Additional arguments

<dl>
<dt>

`root` (str, optional)

<dd>

A colon-separated string to recursively nest the data into the given path. Useful if applications expected the configuration in a specific path but you do not want have that in the source pillar.

```yaml
/rails/config/database.yaml:
  file.managed:
    - template: py
    - source: salt://_templates/yaml2.py
    - context:
        source: myapp:rails:database
        root: production
```

```yaml
# This file is managed by salt. Changes will be overwritten.

production:
  adapter: postgresql
  hostname: 127.0.0.1
```

</dl>


## Execution modules

### `template.managed`

This execution module takes a string or a list of lines and renders this into a consistent text. It will add preamble and ensure there is a final newline.

The preamble text is loaded via [`config.get`](https://docs.saltproject.io/en/latest/ref/modules/all/salt.modules.config.html#salt.modules.config.get) using the `template_managed` key. Therefore the preamble can be specified everywhere including the salt master configuration. This allows to easily set custom message specific to a salt master, e.g.:

```yaml
# /etc/salt/master
template_managed: >
    This file is part of the salt.example.org
    collective. Resistance is futile.
```

All provided templates here use `template.managed` to render the final output. Options from the template are passed through to the module function.

#### Arguments

<dl>
<dt>

`text` (string or list, required)

<dd>

A text string or a list of lines.

<dt>

`preamble` (bool, default: `True`)

<dd>

Set to `False` to not add a preamble.

<dt>

`comment_prefix` (string, default: `"#"`)

<dd>

The string to prepend each line from preamble and comment with. If set to `False`, no preamble or comment will be added.

<dt>

`comment` (string, optional)

<dd>

An additional comment to be added in front of the text.

</dl>

#### Example: Using it in your own template

```py
#!py

def run():
    # generate complex config file
    config = "Very complex config!"

    return __salt__["template.managed"](config, sign="//")
```

```
// This file is managed by salt. Changes will be overwritten.

Very complex config!
```
