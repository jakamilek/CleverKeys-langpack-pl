# Morfeusz 2 / SGJP attribution — 2026-09-24

Morfeusz 2 is used by the Polish language-pack build as a morphological analysis/synthesis oracle for:

- auditing common-noun homonyms among the already-selected first names;
- generating explicit singular inflection forms for the already-selected first names.

The project does not redistribute the full SGJP database. The generated build output is limited to the selected-name forms needed by this project.

## Copyright

Morfeusz 2 program copyright holder: Institute of Computer Science, Polish Academy of Sciences (IPI PAN).

Authors and copyright holders of SGJP inflectional data: Zygmunt Saloni, Włodzimierz Gruszczyński, Marcin Woliński, Robert Wołosz, Danuta Skowrońska.

Copyright © Institute of Computer Science PAS, 2014–2026.

## License

The Morfeusz 2 program and contained linguistic data are released under the 2-clause BSD License. The official license page states that BSD-licensed material includes the inflectional data needed for morphological analysis (the list of inflected forms), not the entire SGJP publication/database.

Official license: https://morfeusz.sgjp.pl/doc/license/
Official project page: https://morfeusz.sgjp.pl/

CI records the exact Morfeusz package version used for each generated inflection artifact.

## Citation

Witold Kieraś, Marcin Woliński. Morfeusz 2 – analizator i generator fleksyjny dla języka polskiego. Język Polski, XCVII(1):75–83, 2017.

This attribution file is documentation for the language-pack project and does not grant permission to redistribute any other SGJP material beyond the licensed material actually used.

## SGJP index fallback

The build also pins `polish-inflection==0.7.3` as a data-only fallback. Its documentation states that its inflection indexes are derived from SGJP, cover 7 cases × 2 numbers and use reverse analysis for validation; the SGJP data is distributed under 2-clause BSD with attribution requirements. The project uses it only at build time to recover explicit forms for already-selected names/cities that Morfeusz synthesis does not expose, and records the package version in the build dependency set. citeturn381260search0turn782674view1
