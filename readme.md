# fylms

**fylms** sends showtimes of films in local theaters with a Letterboxd rating
bigger than 3.2 in an email.

:earth_americas: `local = Vienna, Austria`.

## Installation

1. Clone this repo and `cd` in.
2. `$ virtualenv env`
3. `$ source env/bin/activate`
4. `$ pip install -r requirements.txt`
5. Sign up for a [Mailgun] account and enter your API keys in `config.py`

## Run

`$ python scrape.py`

Tip: use fylms with a local cron job or push to a Heroku dyno and set
a scheduler.

## Misc

fylms uses a slightly redacted and simplified version of my buddy Zac's
[terminalmdb] in order to fetch iMDB film IDs. It's a nice little trick
because provided with an iMDB ID in the URL, Letterboxd redirects to the
film's permalink.

Furthermore: code's kind of ugly. It's more of a proof of concept for now.
Will get optimized later. But _It Works!™_

**Q:** _Why R ≥ 3.2?_  
**A:** Idk.  ¯\\\_(ツ)_/¯

## Screenshots

![Demo screenshot](http://i.imgur.com/IcJYzMt.png)

## License

≥ GPLv3



<!-- LINKS AND REFERENCES -->

[terminalmdb]: http://github.com/zacoppotamus/TerminaIMdB
[Mailgun]: http://mailgun.com
