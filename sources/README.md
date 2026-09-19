# External dictionary sources

This directory contains metadata and import pipelines for external open language resources.

Goals:

- use existing high quality Polish language resources,
- verify license compatibility,
- filter low quality entries,
- preserve reproducible builds,
- generate a mobile keyboard optimized dictionary.

Pipeline:

source database
-> license check
-> quality analysis
-> cleanup
-> frequency ranking
-> CleverKeys format

No external dictionary is included directly without verification.
