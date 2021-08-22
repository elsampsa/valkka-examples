---
name: Bug Report
about: For bugs and exact issues
title: ''
labels: ''
assignees: ''

---

## Bug report

First, make sure that:

- You are running the latest version of libValkka
- Qt applications: you have experimented with the Qt test suite's [test_studio_1.py](https://elsampsa.github.io/valkka-examples/_build/html/testsuite.html)
- ..and understand at least how buffering time and number of pre-reserved frames are connected together
- You have read the [common problems](https://elsampsa.github.io/valkka-examples/_build/html/pitfalls.html) section

Your bug report should include:

- A copy-paste of the salient features of the terminal output
- Indicate the graphics driver are you using:  Intel, nvidia or opensource nvidia (aka "nouveau")
- Ascii art of the filterchain (like in the tutorial)
- A **minimal, single-file code that reproduces the issue as a github gist**
- Please remember that ValkkaFS-related stuff is still pretty experimental
