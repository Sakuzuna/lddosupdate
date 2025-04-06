import curses
import time

sword_art = [
    "                                ,-.",
    "                               (\"O_)",
    "                              / `-/",
    "                             /-. /",
    "                            /   )",
    "                           /   /  ",
    "              _           /-. /",
    "             (_)\"-._     /   )",
    "               \"-._ \"-\'\"\"( )/    ",
    "                   \"-/\"-._\" `. ",
    "                    /     \"-.'_",
    "                   /\\       /-._\"-._",
    "    _,---...__    /  ) _,-\"/    \"-(_)",
    "___<__(|) _   \"\"-/  / /   /",
    " '  `----' \"\"-.   \\/ /   /",
    "               )  ] /   /",
    "       ____..-'   //   /                       )",
    "   ,-\"\"      __.,'/   /   ___                 /,",
    "  /    ,--\"\"/  / /   /,-\"\"   \"\"\"-.          ,'/",
    " [    (    /  / /   /  ,.---,_   `._   _,-','",
    "  \\    `-./  / /   /  /       `-._  \"\"\" ,-\'",
    "   `-._  /  / /   /_',            \"\"--\"",
    "       \"/  / /   /\"         ",
    "       /  / /   /",
    "      /  / /   /  ",
    "     /  |,'   /  ",
    "    :   /    /",
    "    [  /   ,'  ",
    "    | /  ,'",
    "    |/,-'",
    "    P'"
]

def draw_sword(stdscr, y, x):
    height, width = stdscr.getmaxyx()

    for i, line in enumerate(sword_art):
        if y + i >= height:  
            break  
        trimmed_line = line[:width - x]  
        stdscr.addstr(y + i, x, trimmed_line)
        stdscr.refresh()
        time.sleep(0.05)  

def main(stdscr):
    curses.curs_set(0)  
    stdscr.clear()

    height, width = stdscr.getmaxyx()

    if len(sword_art) > height:  
        stdscr.addstr(0, 0, "Increase terminal height to fit the sword animation!")
        stdscr.refresh()
        time.sleep(3)
        return

    x = (width - max(len(line) for line in sword_art)) // 2  
    y = (height - len(sword_art)) // 2  

    draw_sword(stdscr, y, x)  

    time.sleep(2)  

curses.wrapper(main)
