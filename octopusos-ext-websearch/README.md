# octopusos-ext-websearch

Internal extension package for `communication.web_search`.

## Install (internal)

```bash
pip install .
```

## Runtime bridge

Set in OctopusOS runtime:

```bash
export WEB_SEARCH_EXTENSION_ENTRYPOINT="octopus_ext_websearch.plugin:create_web_search_backend"
```
