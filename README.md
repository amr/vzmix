INTRODUCTION
============

  `vzmix` generates OpenVZ container configurations based on existing ones.

  For example, given a base configuration file, `vzmix` can multiply it by
  a given factor. Check the full options by invoking `vzmix` with `--help`.


USAGE
=====

  Check `vzmix --help`.


BUGS? FEATURE REQUESTS?
=======================

  Please send them to: "Amr Mostafa" <amr.mostafa@gmail.com>


TODO
====

  - Add UBC interdependencies checks.
    See: http://wiki.openvz.org/UBC_consistency_check

  - Implement checks for maximum and minimum of each UBC. vzsplit
    tool (part of vzctl) can be a good reference.
    See: http://git.openvz.org/?p=vzctl;a=summary
