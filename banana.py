#!/usr/bin/env python3
"""A typing test for the terminal.

    python3 banana.py            30-second test (default)
    python3 banana.py -t 60      timed test, 60 seconds
    python3 banana.py -n 50      50 words, untimed
    python3 banana.py -s 2       wider line spacing, 1-4
    python3 banana.py --seed 7   fixed word list

Tab restarts with new words, Esc quits, Backspace fixes the last character.
"""

import argparse
import curses
import os
import random
import time

os.environ.setdefault("ESCDELAY", "25")  # don't stall a second after a lone Esc

# The 100 most common English words.
WORDS = """
the be of and a to in he have it that for they i with as not on she at by this we
you do but from or which one would all will there say who make when can more if no
man out other so what time up go about than into could state only new year some
take come these know see use get like then first any work now may such give over
think most even find day also after way many must look before great back through
long where much should well people down own just because good each those feel seem
how high too place little world very still nation hand old life tell write become
here show house both between need mean call develop under last right move thing
general school never same another begin while number part turn real leave might
want point form off child few small since against ask late home interest large
person end open public follow during present without again hold govern around
possible head consider word program problem however lead system set order eye
plan run keep face fact group play stand increase early course change help line
""".split()

BANANA = [ln.rstrip() for ln in """
      -#####*
    :##*...-###
   :##.......-##
   ##:.........##
  :##...........##
  +#+...........+##
  *#=............##-
  ##-.............##
  ##-.............##*
  *#=..............##
  =#+..............=##
  :#*...............##-
  .##................##.
   ##:...............=##
   *#+................*#* -########+:
   :##.................####*:.....=#####
    ##:...............##*.............:###+
    =#*..............##-.................=##*
     ##.............##-....................=##+
     +#*...........:##.......................###
      ##:..........*#+....-+*#####*=-.........*##
      .##############+##########-=*#####*.....=##
     #####=:..:-+######=------+##=     -########
   =###:........####=##+--------*##:       .-:
  +##+.........###-...##*---------###-
 =##=.........###......*##----------*##*
.##*.........###........=##+----------+###+
=##:.........###..........###=-----------+####
###..........###...........:###=------------+####+:
##*..........####:...........:###=--------------+#####+
###..........######.............###*-----------------*#####*=
+##..........:##==##+.............+###+-------------------+*####:
.##+..........###  *##=..............*####=--------------------###
 *##:.........:##+   *##*...............-#####*-----------------+##
  ###..........###     =###-................-+#######*+=======++###
   ###:.........##*       ####-....................-*#############-
    ###*........###         .####+:...........................-##=
     :####......=##.            =####*-:...................:*###
       .#####*=*###                 :#########*++=++*########-
          :######+                        .-=*######*+=:.
""".strip("\n").split("\n")]


def make_text(n, rng):
    return " ".join(rng.choice(WORDS) for _ in range(n))


def layout(target, width):
    """Map every index of `target` to a (row, col) cell, wrapping on spaces."""
    pos = []
    row = col = 0
    words = target.split(" ")
    for wi, word in enumerate(words):
        if col > 0 and col + len(word) > width:  # word won't fit, wrap
            row, col = row + 1, 0
        for _ in word:
            pos.append((row, col))
            col += 1
        if wi != len(words) - 1:  # the space between words
            pos.append((row, col))
            col += 1
    return pos, row + 1


def run(stdscr, target, time_limit=None, size=1):
    curses.use_default_colors()
    curses.curs_set(0)
    stdscr.timeout(100)  # ms; redraw on a timer even when no key is pressed
    lead = size - 1  # blank rows between text lines
    curses.init_pair(1, curses.COLOR_GREEN, -1)  # correct
    curses.init_pair(2, curses.COLOR_RED, -1)  # wrong
    curses.init_pair(3, curses.COLOR_YELLOW, -1)  # the banana
    C_OK, C_BAD, C_DIM = curses.color_pair(1), curses.color_pair(2), curses.A_DIM
    C_BAN = curses.color_pair(3) | curses.A_BOLD

    def put(y, x, s, attr=0):
        try:
            stdscr.addstr(y, x, s, attr)
        except curses.error:  # off-screen write, e.g. the bottom-right cell
            pass

    def banana(x=2):
        for i, line in enumerate(BANANA):
            put(i, x, line, C_BAN)

    # splash: draw the banana and wait for a key before the test starts
    stdscr.erase()
    banana()
    h, w = stdscr.getmaxyx()
    put(h - 1, 4, "banana  -  any key to start,  Esc to quit", C_DIM)
    stdscr.refresh()
    stdscr.timeout(-1)
    if stdscr.getch() == 27:
        return "quit"
    stdscr.timeout(100)

    typed = []      # what the player has typed so far
    start = None    # perf_counter() at the first keystroke
    keystrokes = 0  # every printable key, the accuracy denominator
    hits = 0        # keystrokes that matched the expected character

    while True:
        h, w = stdscr.getmaxyx()
        mx, my = 4, 2
        pos, nrows = layout(target, max(10, w - 2 * mx))

        stdscr.erase()
        put(0, mx, "banana", C_BAN)

        for i, ch in enumerate(target):
            r, c = pos[i]
            y, x = my + r * (1 + lead), mx + c
            if i < len(typed):
                if typed[i] == ch:
                    put(y, x, ch, C_OK)
                else:
                    put(y, x, ch if ch != " " else "_", C_BAD | curses.A_UNDERLINE)
            elif i == len(typed):
                put(y, x, ch, curses.A_REVERSE)  # cursor
            else:
                put(y, x, ch, C_DIM)

        elapsed = (time.perf_counter() - start) if start else 0.0
        correct = sum(1 for i, c in enumerate(typed) if c == target[i])
        wpm = (correct / 5 / (elapsed / 60)) if elapsed > 0.5 else 0.0
        acc = (hits / keystrokes * 100) if keystrokes else 100.0
        clock = f"{max(0.0, time_limit - elapsed):5.1f}s left" if time_limit else f"{elapsed:5.1f}s"
        put(my + nrows * (1 + lead) + 1, mx,
            f"{len(typed):>3}/{len(target)}   {wpm:5.1f} wpm   {acc:5.1f}% acc   {clock}",
            C_DIM)
        put(h - 1, mx, "Tab restart   Esc quit", C_DIM)

        if len(typed) == len(target):  # finished the text
            break
        if time_limit and start and elapsed >= time_limit:  # time's up
            break
        stdscr.refresh()

        ch = stdscr.getch()
        if ch == -1:  # timer tick, no key
            continue
        if ch == 27:  # Esc
            return "quit"
        if ch == 9:  # Tab
            return "restart"
        if ch in (curses.KEY_BACKSPACE, 127, 8):
            if typed:
                typed.pop()
            continue
        if ch == curses.KEY_RESIZE:
            continue
        if 32 <= ch <= 126:  # printable character
            if start is None:
                start = time.perf_counter()
            keystrokes += 1
            if chr(ch) == target[len(typed)]:
                hits += 1
            typed.append(chr(ch))

    # results screen
    if start is None:  # player never typed anything
        return "quit"
    elapsed = time.perf_counter() - start
    correct = sum(1 for i, c in enumerate(typed) if c == target[i])
    wpm = correct / 5 / (elapsed / 60) if elapsed else 0.0
    raw = keystrokes / 5 / (elapsed / 60) if elapsed else 0.0
    acc = hits / keystrokes * 100 if keystrokes else 100.0
    stdscr.erase()
    put(2, 4, "done!", curses.A_BOLD)
    put(4, 4, f"wpm       {wpm:6.1f}")
    put(5, 4, f"raw wpm   {raw:6.1f}")
    put(6, 4, f"accuracy  {acc:6.1f}%")
    put(7, 4, f"time      {elapsed:6.1f}s")
    put(9, 4, "Tab restart   Esc quit", C_DIM)
    stdscr.refresh()
    while True:
        ch = stdscr.getch()
        if ch == 27:
            return "quit"
        if ch == 9:
            return "restart"


def main():
    ap = argparse.ArgumentParser(
        description="A typing test for the terminal.")
    ap.add_argument("-t", "--time", type=int, nargs="?", const=30, metavar="SECONDS",
                    help="time mode: type for SECONDS (this is the default, 30s)")
    ap.add_argument("-n", "--num", type=int, metavar="WORDS",
                    help="word mode: fixed number of words, no clock")
    ap.add_argument("-s", "--size", type=int, choices=range(1, 5), default=1,
                    metavar="1-4", help="line spacing: blank rows between lines (default 1)")
    ap.add_argument("--seed", type=int, help="seed the random word list")
    args = ap.parse_args()
    rng = random.Random(args.seed)

    if args.time is not None:  # -t / -t N: timed
        time_limit = max(1, args.time)
        word_count = max(80, round(time_limit / 60 * 260) + 40)  # enough for ~260 wpm
    elif args.num is not None:  # -n N: fixed word count
        time_limit, word_count = None, max(1, args.num)
    else:  # no flags: 30-second test
        time_limit, word_count = 30, 170

    while True:
        text = make_text(word_count, rng)
        if curses.wrapper(run, text, time_limit, args.size) != "restart":
            break


if __name__ == "__main__":
    main()
