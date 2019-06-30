# Captivitate - Django captive portal

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![CircleCI](https://circleci.com/gh/erdnaxe/captivitate.svg?style=svg)](https://circleci.com/gh/erdnaxe/captivitate)
[![Maintainability](https://api.codeclimate.com/v1/badges/1923ecfb64aa7553b6d6/maintainability)](https://codeclimate.com/github/erdnaxe/captivitate/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/1923ecfb64aa7553b6d6/test_coverage)](https://codeclimate.com/github/erdnaxe/captivitate/test_coverage)

This captive portal enables users to log in on a guest network.
Their MAC addresses are captured then injected into an ipset
enabling external network access.

## History

Initially it was forked from [re2o](https://gitlab.federez.net/federez/re2o)
by [G. Detraz](https://gitlab.crans.org/detraz) but it had been since mostly
rewritten by [erdnaxe](https://gitlab.crans.org/erdnaxe).

## Manual install

For development in a virtualenv:

```bash
$ pip3 install -e . --user
```

## Licence

Ce projet est sous [licence GPL](COPYING) parce que l'on croît au développement
ouvert.
La licence GPL implique des droits et des devoirs.
Veuillez vous référer au fichier de licence pour plus d'informations.
