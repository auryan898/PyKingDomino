# PyKingDomino

King Domino is a board game, but it's the game that we must recreate for Course ECSE 223 at McGill University, during Winter 2020.  As a precursor to this large semester-long project that will create a fully fledged digital version of this game, I've gone ahead and created my own version of the game in Python (2.7) that does not use any complicated GUI, just some ASCII characters in the console window.  This Python version is meant to illustrate the MVP (Minimum Viable Product), that can just barely meet the requirements (in this case, just having a simple version of the game).  Making this teaches me what I need at minimum to implement the game, the simple models that go into it, and other weird little logical bits that I didn't think of until I made the game.

## Installation, Playing the game

You can run the game in the browser with this [repl.it](https://PyKingDomino.ryanau.repl.run)

If you'd like to play on your own computer
1. download the [zip file](https://github.com/auryan898/PyKingDomino/archive/master.zip) and extract the contents to a folder
2. install the game dependencies with `python setup.py install` or `sudo python setup.py install`
3. run the script `KingDomino.py` from the zip file OR run this code inside of a separate python script:

    from KingDomino import Game
    game = Game()
    game.run()