import random
from collections import defaultdict
import re

d = "words.csv"
dictionary = [strngs.strip().lower() for strngs in open(d,"r")]
bag_of_words = [word for word in dictionary if len(word) == 5]

with open('char_freq.csv','r') as f:
    lines = f.readlines()

char_freq = {}
for line in lines:
    char_freq[line.rstrip().lower().split(',')[0]] = int(line.rstrip().lower().split(',')[1])

y_chars = []
g_chars = []

def guessword(inword = None, status = None):
    if inword == None:
        inword = input("Enter a word: ")
    if status == None:
        status = input("Enter color of each letter: ")
    if len(inword) != 5 or len(status) != 5 or len([i for i in status if i not in ['o','y','g']]) > 0: #list(set(status)) not in ['o','y','g']:
        print('\n')
        print('Somethings not right.')
        print('Please make sure you\'ve input 5 characters and that the word scheme is only using o y g characters.')
        print('\n')
        inword, status = guessword()

    return inword.lower(), status.lower()

def grab_locations(grp):
    dic = defaultdict(list)
    for i, item in enumerate(grp):
        dic[item].append(i)
    return dic

def attempt(word = None, status = None):

    all_locs = grab_locations(status)
    all_locs_items = defaultdict(list)

    for key, values in all_locs.items():
        for value in values:
            all_locs_items[key].append(word[value])
    semi_bad = []
    for key,values in all_locs_items.items():
        if key == 'o':
            for value in values:
                bad_letter_in_mult_classes = [status for status, letters in all_locs_items.items() if value in letters]
                if len(bad_letter_in_mult_classes) > 1:
                    semi_bad.append(value)
    word_locs = grab_locations(word)
    semi_bad_locs = {}
    for key, values in word_locs.items():
        for sb in semi_bad:
            if sb == key:
                semi_bad_locs[key] = values
    sol = ['^','^','^','^','^']
    ol = ''
    yellows = []
    greens = []
    for s in range(len(status)):
        if status[s] == 'g':
            greens.append(word[s])
            sol[s] = word[s]
        elif status[s] == 'y' and word[s] in semi_bad:
            sol[s] += word[s]
        elif (status[s] == 'o' and word[s] in all_locs_items['y']) or (status[s] == 'y' and word[s] not in semi_bad):
            yellows.append(word[s])
            sol[s] += word[s]
        else:
            ol += word[s]

    for i in range(len(sol)):
        if '^' in sol[i]:
            sol[i] += ol
    sol_copy = sol.copy()
    all_possible_sols = []
    yellows_regx = '|'.join(yellows)
    if len(semi_bad) > 0:
        for s in semi_bad:
            for j in semi_bad_locs[s]:
                for i in range(len(sol_copy)):
                    sol_copy = sol.copy()
                    if word[j] not in  sol_copy[i] and '^' in sol_copy[i] and word[j] not in greens:
                        sol_copy[i] += ']|' + '[' + word[j]
                        all_possible_sols.append(sol_copy)
                    elif word[j] in greens and '^' not in sol_copy[i]:
                        sol_copy[i] = word[j]
                        all_possible_sols.append(sol_copy)
        sols = [list(t) for t in {tuple(item) for item in all_possible_sols}]
        return sols, greens, yellows
    elif len(yellows) > 0:
        for s in yellows:
            for i in range(len(sol_copy)):
                sol_copy = sol.copy()
                if s not in  sol_copy[i] and '^' in sol_copy[i] and word[i] not in yellows:
                    sol_copy[i] += ']|' + '[' + yellows_regx
                    all_possible_sols.append(sol_copy)
                elif s not in  sol_copy[i] and '^' in sol_copy[i]:
                    sol_copy[i] += ']|' + '[' + s
                    all_possible_sols.append(sol_copy)
        sols_1 = [list(t) for t in {tuple(item) for item in all_possible_sols}]
        return sols_1, greens, yellows
    else:
        return [sol], greens, yellows

def compare(mash, sols, bag):
    matchingwords = []
    patterns = []
    for sol in sols:
        for i in range(len(sol)):
            if '|' not in sol[i]:
                sol[i] = '[' + sol[i] + ']'
            else:
                sol[i] = '([' + sol[i] + '])'
        m = re.compile(''.join(sol))
        patterns.append(m)
        for m in patterns:
            matchingwords += list(filter(m.match, bag))
    matchingwords = list(set(matchingwords))
    mw = [word for word in matchingwords if all(x in word for x in mash) == True]
    print('\n')
    print('Current pattern for this word:')
    print(patterns)
    print('Size of current wordbank', len(mw))
    mw_dict = {}
    for word in mw:
        for k,v in char_freq.items():
            if word not in mw_dict:
                mw_dict[word] = 0
            if k in word:
                mw_dict[word] += v
    try:
        suggest_word = max(mw_dict, key=mw_dict.get)
    except ValueError:
        print('No words found, check the wordbank...')
    return suggest_word, mw, mw_dict, patterns
print('#####################')
print('To play, enter a word on Wordle, then provide the results here.', '\n',
'o = black, y = yellow, g = green', '\n',
'Example: Initial guess could be ''adieu''','\n', 'The status for that word could be googo', '\n',
'where ''a'' and ''e'' are in the solution.')
print('#####################', '\n')
w, s = guessword()
all_solutions, greens, yellows = attempt(w,s)
y_chars += yellows
g_chars += greens
mash = []
mash += y_chars + g_chars
ss = ''
len_mw = 2
all_patterns = []
while ss != 'ggggg':
    if len_mw <= 1:
        print('\n')
        print('Sorry -- there are no more words in the wordbank!')
        print('\n')
        break
    try:
        suggest_word, mw, mw_dict, patterns = compare(mash, all_solutions, bag_of_words)
    except UnboundLocalError:
        print('Sound the alarms! Somethings not right!')
        break
    all_patterns += patterns
    print('\n')
    print('All patterns for this game:')
    print(all_patterns)
    print('\n')
    print('Next suggestion ****',suggest_word,'**** This word has the highest score: ', suggest_word, '(Score: ', mw_dict[suggest_word], ')')
    ww, ss = guessword(suggest_word, None)
    all_solutions, g, y = attempt(ww, ss)
    y_chars += g
    g_chars += y
    mash += g + y
    bag_of_words = mw.copy()
    len_mw = len(mw)
else:
    print('Great job, you\'ve solved it!')
