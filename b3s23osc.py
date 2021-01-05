# b3s23osc.py version 1.1
# version 1.0: David Raucci, 1/5/2021 ( https://conwaylife.com/forums/viewtopic.php?p=118160#p118160 )
# version 1.1: Dave Greene,  1/5/2021 ( handle various possible error conditions, copy result to clipboard )

import time
import golly as g
import os

start_time = time.time()
g.setrule("B3/S23")
# clear the universe before starting to build stamp collection
g.new("oscillators.rle")

def show_message(message, time_):
    g.show(str(message))
    time.sleep(time_)

def convert_rle_to_grid(rle):
    comments = ''
    rle = rle.replace('rule = b3/s23', 'rule = B3/S23')
    if 'rule = B3/S23' in rle:
        comments = rle[:rle.index('x =')]
        rle = rle[rle.index('rule = B3/S23')+13:] #starts after the dimension and rule identifiers
    else:
        show_message('"rule = B3/S23 not in RLE": ' + rle,0.5)
        return {}
    x = 0
    y = 0
    pattern = {}
    num = '' #num keeps track of digits and then processes it when it hits a b, o, or $
    while rle:
        if rle[0] in '0123456789': #digit
            num += rle[0]
            rle = rle[1:] #remove leftmost character
        elif rle[0] in ('o','b'):
            if num == '': #no number: only one
                num = 1
            num = int(num)
            for i in range(num):
                pattern[(x,y)] = (1 if rle[0] == 'o' else 0)
                x += 1
            num = ''
            rle = rle[1:] #remove leftmost character
        elif rle[0] == '$':
            if num == '':
                num = 1
            num = int(num)
            for i in range(num):
                y += 1
            x = 0
            num = ''
            rle = rle[1:] #remove leftmost character
        elif rle[0] == '!':
            break
        elif rle[0] in ' \n\t%': #percent sign is used to mark as period 1000+; just for this program, not typical RLE
            rle = rle[1:] #remove leftmost character
        else:
            raise ValueError('Invalid RLE', rle)
    max_x = max((-1000 if pattern[cell] == 0 else cell[0]) for cell in pattern)
    max_y = max((-1000 if pattern[cell] == 0 else cell[1]) for cell in pattern)
    for i in range(max_x+1):
        for j in range(max_y+1):
            pattern[(i,j)] = pattern.get((i,j), 0)
    return (pattern, comments)

def print_grid(pattern): #shows pattern as a readable grid
    min_x = min((1000 if pattern[cell] == 0 else cell[0]) for cell in pattern) #only reads cells that are on
    max_x = max((-1000 if pattern[cell] == 0 else cell[0]) for cell in pattern)
    min_y = min((1000 if pattern[cell] == 0 else cell[1]) for cell in pattern)
    max_y = max((-1000 if pattern[cell] == 0 else cell[1]) for cell in pattern)
    for y in range(min_y, max_y+1):
        for x in range(min_x, max_x+1):
            print(('o' if pattern[(x,y)] == 1 else '.'), end='')
        print('') #newline

def run_pattern_in_golly(pattern, comments, extended):
    pattern_rle = pattern
    pattern = g.parse(pattern)
    if len(pattern) % 2 == 1:
        g.warn(pattern_rle)
        g.warn(str(pattern))
    initial_pattern = pattern.copy()
    xs = pattern[::2]
    ys = pattern[1::2]
    min_x = 0
    max_x = max(xs)
    min_y = 0
    max_y = max(ys)
    min_min_x = min_x #these four are the permanent minima and maxima, used for determining maximum pattern size
    max_max_x = max_x
    min_min_y = min_y
    max_max_y = max_y
    for period in range(1, 100000 if extended else 1000): #maximum oscillator period
        pattern = g.evolve(pattern,1)
        if not pattern:
            print('Not an oscillator, dies out completely: %s' % initial_pattern)
            return
        xs = pattern[::2]
        ys = pattern[1::2]
        min_min_x = min(min_min_x, min(xs)) #sets new absolute minima and maxima
        max_max_x = max(max_max_x, max(xs))
        min_min_y = min(min_min_y, min(ys))
        max_max_y = max(max_max_y, max(ys))
        if pattern == initial_pattern:
            return (comments + convert_grid_to_rle(pattern), period, max_max_x-min_min_x+1, max_max_y-min_min_y+1, -min_min_x, -min_min_y)
            #0: RLE. 1: period. 2, 3: maximum bounding box for x and y. 4, 5: Greatest negative for calculating offset.
        #if extended == 'file': #one at a time
        #    return pattern
    print('Not an oscillator, maximum generations reached: %s' % initial_pattern)
    return

#these create the digits for labeling periods
zero = 'x = 8, y = 14, rule = B3/S23\n2b2obo$2bob2o$2o4b2o$o5bo$bo5bo$2o4b2o$o5bo$bo5bo$2o4b2o$o5bo$bo5bo$2o4b2o$2b2obo$2bob2o!'
one = 'x = 8, y = 14, rule = B3/S23 6b2o$7bo$6bo$6b2o2$6b2o$7bo$6bo$6b2o2$6b2o$7bo$6bo$6b2o!'
two = 'x = 8, y = 14, rule = B3/S23\n2b2obo$2bob2o$6b2o$6bo$7bo$6b2o$2b2obo$2bob2o$2o$o$bo$2o$2b2obo$2bob2o!'
three = 'x = 8, y = 14, rule = B3/S232b2obo$2bob2o$6b2o$6bo$7bo$6b2o$2b2obo$2bob2o$6b2o$6bo$7bo$6b2o$2b2obo$2bob2o!'
four = 'x = 8, y = 14, rule = B3/S23\n2o4b2o$bo5bo$o5bo$2o4b2o$2bob2o$2b2obo$6b2o$7bo$6bo$6b2o3$6b2o$6b2o!'
five = 'x = 8, y = 14, rule = B3/S23\n2bob2o$2b2obo$2o$bo$o$2o$2bob2o$2b2obo$6b2o$7bo$6bo$6b2o$2bob2o$2b2obo!'
six = 'x = 8, y = 14, rule = B3/S23\n2b2obo$2bob2o$2o$o$bo$2o$2b2obo$2bob2o$2o4b2o$o5bo$bo5bo$2o4b2o$2b2obo$2bob2o!'
seven = 'x = 8, y = 14, rule = B3/S232bob2o$2b2obo$6b2o$7bo$6bo$6b2o$4b2o$5bo$4bo$4b2o$2b2o$3bo$2bo$2b2o!'
eight = 'x = 8, y = 14, rule = B3/S23\n2b2obo$2bob2o$2o4b2o$o5bo$bo5bo$2o4b2o$2b2obo$2bob2o$2o4b2o$o5bo$bo5bo$2o4b2o$2b2obo$2bob2o!'
nine = 'x = 8, y = 14, rule = B3/S23\n2b2obo$2bob2o$2o4b2o$o5bo$bo5bo$2o4b2o$2b2obo$2bob2o$6b2o$6bo$7bo$6b2o$2b2obo$2bob2o!'

num_dict = {'0':'zero','1':'one','2':'two','3':'three','4':'four','5':'five','6':'six','7':'seven','8':'eight','9':'nine'}

digit_rles = [zero,one,two,three,four,five,six,seven,eight,nine]

height = 650 #note: if a single period is taller than height variable, it won't work properly

def spacing(period): #both for horizontal and vertical spacing
    if period == 1:
        return 3
    elif period in (2, 3):
        return 4
    elif 4 <= period <= 9:
        return 5
    else:
        return 7

def digit_width(num):
    num = str(num)
    return 10*len(num) - 6*(num[0] == '1')

def create_column(pattern_dict):
    global grid, comments
    current_period = min(pattern_dict[i][1] for i in pattern_dict)
    period_row = 0
    pattern_dict_copy = pattern_dict.copy()
    for i in pattern_dict_copy:
        if i[1]+pattern_dict[i][3] >= period_y:
            del pattern_dict[i]
    max_y = max(i[1]+pattern_dict[i][3] for i in pattern_dict)
    rows = max(i[3] for i in pattern_dict)
    while max(i[1]+pattern_dict[i][3]+rows for i in pattern_dict) <= height:
        if max(i[1] for i in pattern_dict) < 30:
            break #prevent infinite loop on single line
        pattern_dict_copy = {}
        for i in pattern_dict:
            pattern_dict_copy[(i[0], i[1]+i[3], i[2], i[3])] = pattern_dict[i] #spaces out patterns vertically
        pattern_dict = pattern_dict_copy.copy()
    for x1 in range(-len(str(period))*10 + column_x, 120 + column_x): #negative numbers used for creating the digits
        for y1 in range(0, height-1):
            grid[(x1,y1)] = 0 #fill everything with off scells
    for i in pattern_dict:
        grid_form = convert_rle_to_grid(pattern_dict[i][0])
        if pattern_dict[i][1] > current_period:
            comments += '#C ----------------------------------------------------------------------\n'
            current_period = pattern_dict[i][1]
            period_row = i[3]
        if i[2] >= 0: #not a digit
            current_comment = grid_form[1]
            if '#N' not in current_comment:
                current_comment = '#N\n' + current_comment
            comments += '#N %s.%s.%s ' % (pattern_dict[i][1], i[3]-period_row, i[2]) + current_comment[3:]
        grid_form = grid_form[0]
        for j in grid_form:
            if grid_form.get(j, 0) == 1:
                grid[(j[0]+i[0], j[1]+i[1])] = 1 #paste patterns in

def convert_grid_to_rle(grid1):
    if type(grid1) == list:
        grid = {}
        for i in range(0,len(grid1),2):
            grid[(grid1[i],grid1[i+1])] = 1
    else:
        grid = grid1
    min_x = min(cell[0] for cell in grid)
    max_x = max(cell[0] for cell in grid)
    min_y = min(cell[1] for cell in grid)
    max_y = max(cell[1] for cell in grid)
    for i in range(min_x,max_x+1):
        for j in range(min_y,max_y+1):
             grid[(i,j)] = grid.get((i,j),0)
    to_return = 'x = %s, y = %s, rule = B3/S23\n' % (max_x-min_x+1, max_y-min_y+1) #\n is newline
    for j in range(min_y,max_y+1):
        while to_return[-1] == 'b': #remove blanks at the end of a line
            to_return = to_return[:-1]
        to_return += '$'
        for i in range(min_x,max_x+1):
            to_return += ('o' if grid.get((i,j),0) == 1 else 'b')
    while to_return[-1] == 'b': #remove blanks at the end of the last line
         to_return = to_return[:-1]
    while to_return[-1] == '$': #remove empty lines at the end
         to_return = to_return[:-1]
    to_return += '!'
    while '\n$' in to_return:
        to_return = to_return.replace('\n$', '\n')
    for i in ('b','o','$'):
        for j in ('b','o','$','\n'):
            if j != i:
                to_return = to_return.replace(j+i+i, j+'2'+i) #bb becomes 2b, but bbbbbbb becomes 2bbbbb, not 2b2b2b
        num = 2
        while (str(num) + i + i) in to_return:
            to_return = to_return.replace(str(num) + i + i,str(num+1) + i) #2bbbb becomes 3bbbb, 3bbbb becomes 4bb, etc.
            num += 1
    while 'B3/S23 ' in to_return:
        to_return = to_return.replace('B3/S23 $','B3/S23 ') #remove newlines at the beginning
    return to_return

def open_file2(file):
    if not os.path.exists(file):
        oldfile = file
        file = g.opendialog("Please locate " + file + ":", "Text files (*.txt)|*.txt", "", file)     
        if not os.path.exists(file):
            g.exit("Could not find '" + oldfile + "' or '" + file + "'.")
    f = open(file, 'r')
    f1 = f.read()
    f1 = f1.replace('b3/s23', 'B3/S23')
    while '\n\n\n' in f1:
        f1 = f1.replace('\n\n\n', '\n\n')
    f1 = f1.split('\n\n')
    f1 = f1[:-2] #last two are larger than column width and will cause infinite loop; P2700 is just too high of a period
    for i in f1:
        #try:
        #    i = i[i.index('x ='):]
        #except ValueError:
        #    print('No "x =": ' + i)
        patterns.append(i)
        show_message(len(patterns),0.001)
    show_message('Total number of patterns: %s' % len(patterns),0.5)

patterns = []
open_file2('oscillators.txt')
data = [(0,1234567,0,0,0,0)] #this period 1234567 marks the end of the file
count = 0
for i in patterns:
    count += 1
    show_message(str(count) + ' done, ' + str(int(time.time() - start_time)) + ' seconds',0.005)
    try:
        data.append(run_pattern_in_golly(i[i.index('= B3/S23')+9:], i[:i.index('x =')], '%' in i)) #max period 1000 without %, 100000 with %
    except ValueError:
        g.warn('"= B3/S23" not found: ' + i)
show_message('All done, ' + str(int(time.time() - start_time)) + ' seconds',0.5)

while None in data: #non-oscillators:
    data.remove(None)
#for i in num_dict.values(): #digits from other files
#    if eval(i) in data:
#        data.remove(eval(i))
num_patterns = len(data)

data.sort(key=lambda a:(a[1],a[3])) #first by period, then height

num_periods = 0
comments = ''
grid = {}
column = 1 #column number
column_x = 0 #column x offset
period = 1
period_y = 0 #y value at the beginning of the period
x = 0
y = 0
pattern_dict = {}
pattern_list = [] #pattern_list empties into pattern_dict at the end of each row, column, and period
while len(set(j[1] for j in data)): #this allows repeating periods that couldn't fit due to end of a column
    x = column_x
    rows = 0
    for period in sorted(set(j[1] for j in data)): #lowest periods first; they get deleted as they're completed
        if period == 1234567: #end of file
            period_y = height + 100 #so that everything will be included
            period = max((j[1] * (j[1] != 1234567)) for j in data) #so it doesn't try to place a 7-digit number
            create_column(pattern_dict)
            data = [] #empties data to complete program
            break
        period = int(period)
        if y < period_y + 20 - spacing(period) and y > 0:
            y = period_y + 20 #so displayed digits don't conflict
        elif y > 0:
            y += spacing(period)
        period_y = y #becomes the y value at the beginning of the period
        period_str = str(period)
        for digit in range(len(period_str)): #creates displayed digits
            pattern_dict[-10*(len(period_str)-digit)+column_x, y, -1, rows] = (eval(num_dict[period_str[digit]]),1,14,8,0,0)
        period_patterns = list(filter(lambda a:a[1]==period, data)) #only patterns of the correct period
        if period == 1: #still lifes are sorted by size up to 10 bits
            period_patterns.sort(key=lambda a:min(11,sum(i == 1 for i in convert_rle_to_grid(a[0])[0].values())))
        if period == 2: #p2 oscillators are sorted by size up to 14 bits
            period_patterns.sort(key=lambda a:min(15,sum(i == 1 for i in convert_rle_to_grid(a[0])[0].values())))
        period_patterns.append(('End of period', period, 0, period_patterns[-1][3], 0, 0))
        #prevents the last pattern going past the height limit
        for pattern in period_patterns:
            if pattern[0] == 'End of period' and y + pattern[3] < height:
                break
            if x + pattern[2] >= 120 + column_x or y + pattern[3] >= height: #end of row or column
                if y + pattern[3] + spacing(period) >= height: #end of column
                    create_column(pattern_dict)
                    column += 1
                    column_x += 132 + digit_width(period)
                    y = -1 #-1 is used to break out of loop
                    period_y = 0
                    pattern_list = []
                    pattern_dict = {}
                    rows = 0
                    break
                while x + len(pattern_list) <= 120 + column_x: #end of row
                    for i in pattern_list:
                        i[1] += i[2] #i[2] is the pattern number in the row; this spaces the row out to fill the full 120 cells
                    x += len(pattern_list)
                for i in pattern_list:
                    pattern_dict[(i[1], y+i[0][5], i[2], rows)] = i[0] #puts the list into a dict
                rows += 1
                y += max(i[0][3] for i in pattern_list) + spacing(period) #maximum height
                #will enter an infinite loop if a single pattern is more than 120 rows wide
                x = column_x - digit_width(period) * (y - 16 >= period_y) #moves left if the digit doesn't interfere
                pattern_list = []
            pattern_list.append([pattern, x+pattern[4], len(pattern_list)])
            x += pattern[2] + spacing(period)
        if y == -1: #end of column; beginning of new column
            y = 0
            break
        data = list(filter(lambda a:a[1] > period, data)) #removes a period when it's done
        show_message('Period done: ' + str(period),0.02)
        num_periods += 1
        while x + len(pattern_list) <= 120 + column_x: #these lines are the same as the end-of-row lines
            for i in pattern_list:
                i[1] += i[2]
            x += len(pattern_list)
        for i in pattern_list:
            pattern_dict[(i[1], y+i[0][5], i[2], rows)] = i[0]
        rows += 1
        y += pattern_list[-1][0][3] + spacing(period)
        pattern_list = []
        x = column_x
final_list = []
for i in grid:
    if grid[i] == 1:
        final_list.extend([i[0],i[1]])
g.putcells(final_list)

comments = '''#N Stamp collection
#C A collection of %s oscillators of %s different periods from 1
#C to 40894. 
#C
#C The oscillators included here were found/built by many people over
#C many years.  I finished putting the collection together in August 1995,
#C and have worked on this header file off and on since then.  It's still
#C incomplete and probably inaccurate, but I've decided to make it public
#C anyway; if you find any errors or can fill in any of the blanks, please
#C let me (David Raucci; Dean Hickerson is no longer updating) know. This
#C file has since been updated in 2020
#C by David Raucci, converting it to a Python program that automatically updates
#C based on a text file input and includes more oscillators that were not
#C known in 1995.
#C
#C Since this collection was built, many new oscillators have been found.
#C Most notably, in 1996 David Buckingham showed how to create tracks
#C built from still-lifes through which Herschels can move.  (See
#C  http://www.radicaleye.com/lifepage/patterns/bhept/bhept.html
#C for Buckingham's description of this, and
#C  http://www.radicaleye.com/lifepage/patterns/p1/p1.html
#C for Paul Callahan's discussion of using such conduits to build a stable
#C glider reflector.)  Using Herschel tracks, Buckingham obtained glider
#C guns of all periods >= 62 and oscillators of all periods >= 61.  Further
#C work on Herschel tracks has been done by Buckingham, Paul Callahan,
#C Dieter Leithner, and me; such tracks now give oscillators of all periods
#C >=54, and guns of periods 54, 55, and 56. In addidion, the 2013 discovery
#C of the Snark allowed all oscillators of all periods 43 and higher.
#C There are 4 periods for which oscillators
#C are still unknown as of late 2020: 19, 34, 38, and 41.
#C (For period 34, we could use a noninteracting combination of p2 and p17
#C oscillators, but that's considered trivial.)
#C
#C Building this collection would have been impossible without the help
#C of many people.  In addition to those who found the oscillators, I'd
#C like to thank Alan Hensel, Bill Gosper, Robert Wainwright,
#C Rich Schroeppel, and Jonathan Cooley for helpful suggestions, and
#C Andrew Trevorrow for writing LifeLab, an excellent Macintosh program
#C for building and running Life patterns.  LifeLab's cross-platform
#C successor, Golly, is available as freeware at http://golly.sf.net .
#C
#O Dean Hickerson, dean.hickerson@yahoo.com
#C 2/2/2000; last updated 9/16/2000. URLs corrected
#C and list of missing periods updated on 5/8/2009.
#C
#C David Raucci, updated 1/1/2021.
#C
#C ----------------------------------------------------------------------
#C
#C Most lines of this header describe particular oscillators.  Each entry
#C begins with an identifying label, of the form "period.row.column";
#C row and column numbers start at zero.  This is followed by the name of
#C the oscillator (if any) in quotation marks, the discoverer and date of
#C discovery (if known) in brackets, and perhaps a comment about the
#C oscillator.  For example:
#C
#C     2.0.0   "blinker"  [JHC 3/70]  Example of "+c*c" symmetry.  This
#C             often occurs in a group of 4, known as a "traffic light",
#C             which arises, for example, from a T-tetromino. 
#C
#C This indicates that the leftmost oscillator in the top row of the period 2
#C section is called a "blinker", and was found by John Conway in March 1970.
#C The notation "+c*c" indicates the symmetry type of the oscillator, which
#C is described later.
#C
#C Many oscillators were found by the following people or groups, so their
#C names are abbreviated in this header, for the oscillators in the original
#C DRH file (ones added in 2020 are unabbreviated):
#C 
#C    AF  = Achim Flammenkamp
#C    AWH = Alan Hensel
#C    DIB = David Bell
#C    DJB = David Buckingham
#C    DRH = Dean Hickerson
#C    HH  = Hartmut Holzwart
#C    JHC = John Conway
#C    MDN = Mark Niemiec
#C    MM  = Matthias Merzenich
#C    NB  = Nicolay Beluchenko
#C    NDE = Noam Elkies
#C    PC  = Paul Callahan
#C    RCS = Rich Schroeppel
#C    RTW = Robert Wainwright
#C    RWG = Bill Gosper
#C    SN  = Simon Norton
#C    JHC group  = A group of people working with John Conway in the
#C                 early 1970s, including Conway, S. R. Bourne,
#C                 M. J. T. Guy, and Simon Norton.
#C    MIT group  = A group of people at MIT during the early 1970s,
#C                 including Robert April, Michael Beeler, Bill Gosper,
#C                 Richard Howell, Rici Liknaitzky, Bill Mann,
#C                 Rich Schroeppel, and Michael Speciner.
#C 
#C Also, many of the common oscillators were found independently by many
#C people; this is indicated by an asterisk in the name field.
#C
#C Here are definitions of some terminology and notation used below; for
#C a more extensive glossary, see Stephen Silver's Life Lexicon, at
#C  http://www.argentum.freeserve.co.uk/lex_home.htm 
#C 
#C The 'rotor' constists of all cells in an oscillator which change state.
#C The 'stator' constists of all cells which are alive in all generations.
#C (These terms were introduced by Allan Wechsler in 1994.)
#C
#C An oscillator whose stator is large is often called a 'billiard table';
#C such oscillators are somewhat easier to find than others, so many are
#C included in this collection.
#C
#C The 'period' of an oscillator (or spaceship) is the smallest positive
#C integer P for which generation P of the object is congruent to and in
#C the same orientation as generation 0.  The 'mod' of an oscillator (or
#C spaceship) is the smallest positive integer M for which generation M
#C of the object is congruent to generation 0, but not necessarily in the
#C same orientation.  The quotient q=P/M is always either 1, 2, or 4.  To
#C specify both P and M, we often write "period P.M" or "period P/q".
#C
#C There are 43 types of symmetry that an oscillator can have, taking into
#C account both the symmetry of a single generation and the change of
#C orientation (if any) M generations later.  There are 16 types of
#C symmetry that a pattern can have in a single generation.  Each of these
#C is given a one or two character name, as follows:
#C 
#C    n   no symmetry
#C 
#C    -c  mirror symmetry across a horizontal axis through cell centers
#C    -e  mirror symmetry across a horizontal axis through cell edges
#C 
#C    /   mirror symmetry across one diagonal
#C 
#C    .c  180 degree rotational symmetry about a cell center
#C    .e  180 degree rotational symmetry about a cell edge
#C    .k  180 degree rotational symmetry about a cell corner
#C 
#C    +c  mirror symmetry across horizontal and vertical axes meeting
#C        at a cell center
#C    +e  mirror symmetry across horizontal and vertical axes meeting
#C        at a cell edge
#C    +k  mirror symmetry across horizontal and vertical axes meeting
#C        at a cell corner
#C 
#C    xc  mirror symmetry across 2 diagonals meeting at a cell center
#C    xk  mirror symmetry across 2 diagonals meeting at a cell corner
#C 
#C    rc  90 degree rotational symmetry about a cell center
#C    rk  90 degree rotational symmetry about a cell corner
#C 
#C    *c  8-fold symmetry about a cell center
#C    *k  8-fold symmetry about a cell corner
#C 
#C For a period P/1 object, specifying the symmetry of generation 0 tells
#C us all there is to know about the oscillator's symmetry.  For a period
#C P/2 or P/4 object, we also need to know how gen M is related to gen 0.
#C For the P/2 case, gen M can be either a mirror image of gen 0, a 180
#C degree rotation of it, or a 90 degree rotation of it if the pattern
#C has 180 degree rotational symmetry.  For the P/4 case gen M must be a
#C 90 degree rotation of gen 0.  In any case, if we merge all gens which
#C are multiples of M, the resulting pattern will have more symmetry than
#C the original oscillator.  We describe the complete symmetry class of
#C the oscillator by appending the one or two character description of
#C the union's symmetry to that of gen 0's symmetry.  For example, if
#C gen 0 has 180 degree rotational symmetry about a cell center, and
#C gen M is obtained by reflecting gen 0 across a diagonal, then the
#C union of gens 0 and M is symmetric across both diagonals, so its
#C symmetry class is denoted ".cxc".
#C 
#C The 43 possible symmetry types are:
#C 
#C    period/mod = 1:  nn    -c-c  -e-e  //    .c.c  .e.e  .k.k  +c+c
#C                     +e+e  +k+k  xcxc  xkxk  rcrc  rkrk  *c*c  *k*k
#C 
#C    period/mod = 2:  n-c   n-e   n/    n.c   n.e   n.k
#C                     -c+c  -c+e  -e+e  -e+k
#C                     /xc   /xk
#C                     .c+c  .cxc  .crc  .e+e  .k+k  .kxk  .krk
#C                     +c*c  +k*k  xc*c  xk*k  rc*c  rk*k
#C 
#C    period/mod = 4:  nrc   nrk
#C 
#C The collection includes examples of all of these with mod=1, and many
#C with larger periods.
#C
#C ----------------------------------------------------------------------
#C Period 1 oscillators are usually called "still-lifes".  Programs
#C written by MDN and others have counted the still-lifes with N cells
#C for small N; the results up to N=20 are shown here:
#C 
#C N    4 5 6 7 8  9 10 11  12  13  14   15   16   17    18    19     20
#C #    2 1 5 4 9 10 25 46 121 240 619 1353 3286 7773 19044 45759 112243
#C 
#C Those with up to 10 bits are included in the stamp collection.  So are
#C some larger ones that either occur naturally in random soups, or are
#C useful, or exemplify symmetry types.  I'm omitting the discoverers and
#C dates for most of the small and naturally occurring ones, since they've
#C been independently discovered many times.\n''' % (num_patterns, num_periods) + comments
comments = comments.replace(' #O', '\n#O')
comments = comments.replace(' #C', '\n#C')
comments = comments.split('\n')
comments2 = ''
began = False
space_len = 0
for i in range(len(comments)):
    if '1.0.0' in comments[i]: #end of introduction; beginning of patterns
        began = True
    if began and '#N' in comments[i]: #pattern name
        try: #space_len is so that comments are aligned with the automatically generated pattern number
            space_len = comments[i][3:].index(' ')+2
        except ValueError:
            space_len = len(comments[i])-1
    if not began: #if still introduction
        comments2 += comments[i] + '\n'
    elif i != len(comments)-1 and '#O' in comments[i+1]: #puts pattern discoverer on name line with brackets
        comments2 += comments[i] + ' [' + comments[i+1][3:] + ']\n'
    elif '#C' in comments[i] and '----' not in comments[i]: #spaces comment lines to match pattern number
        comments2 += '#C' + ' '*space_len*began + comments[i][3:] + '\n'
    elif '#O' in comments[i]: #discoverers are put on the previous line; this is so that they're not duplicated
        pass
    else:
        comments2 += comments[i] + '\n'
comments2 = comments2.replace(' #C', '\n#C')
comments2 = '#N ' + comments2[3:].replace('#N', '#C') #comments file only has one #N, and it's at the very beginning
show_message('Comments size: %s KB' % ((len(comments2)+500)//1000),0.5)

tempname = os.path.join(g.getdir("temp"),"oscillators.rle")
g.save(tempname, "rle")
with open(tempname,"r") as f:
    allrle = f.read()
with open(tempname,"w") as f:
    f.write(comments2 + "\n" + allrle)
g.open(tempname)  # this integrates the comments into the currently open pattern file
                  # there still seem to be some issues with keeping the comments after re-saving the file,
                  # but I'll deal with that separately.  Meanwhile:
g.note("Click OK to copy pattern with comments to the clipboard.")
g.setclipstr(comments2 + "\n" + allrle)
