# banana

I spend way too much time on typing-test sites, so I wrote a small one that
lives in my terminal. No browser, no login, no leaderboard begging for your
email. Just words on a screen and a WPM number at the end.

It's a single Python file and only uses the standard library.

## Install

```
pipx install .        # or: pip install --user .
```

That puts a `banana` command on your PATH. Prefer not to install? Just run
`python3 banana.py` from the repo instead.

## Play

```
banana            # 30-second test
banana -t 60      # timed, 60 seconds
banana -n 50      # 50 words, no clock
banana -s 2       # more space between lines (1-4)
banana --seed 7   # same words every run, handy for racing a friend
```

Correct letters go green, mistakes go red. `Tab` reshuffles the words if you
don't like the ones you got, `Backspace` fixes the last character, `Esc` bails.

When the timer runs out (or you finish the words) you get net WPM, raw WPM,
accuracy, time, and a big banana for your trouble.

## Notes

You need a real terminal. `curses` ships with Python on macOS and Linux; on
Windows you'll want `pip install windows-curses`. Works on Python 3.8 and up.
