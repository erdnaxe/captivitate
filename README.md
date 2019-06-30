# Captivitate - Django captive portal

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
