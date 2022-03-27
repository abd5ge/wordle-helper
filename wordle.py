import random
from collections import defaultdict
import re

#d  = "/usr/share/dict/words"
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
    return inword.lower(), status.lower()


def grab_locations(grp):
    dic = defaultdict(list)
    for i, item in enumerate(grp):
        dic[item].append(i)
    return ((key,locs) for key,locs in dic.items()
                            if len(locs)>0)

def attempt(word = None, status = None):
    all_locs = {'o':[], 'y':[], 'g':[]}
    for locs in sorted(grab_locations(status)):
        all_locs[locs[0]] = locs[1]

    all_locs_items = {'o':[], 'y':[], 'g':[]}
    for key, values in all_locs.items():
        if key not in all_locs_items:
            all_locs_items[key] = []
        for value in values:
            all_locs_items[key].append(word[value])

    semi_bad = []
    for key,values in all_locs_items.items():
        if key == 'o':
            for value in values:
                bad_letter_in_mult_classes = [status for status, letters in all_locs_items.items() if value in letters]
                if len(bad_letter_in_mult_classes) > 1:
                    semi_bad.append(value)

    semi_bad_locs = {}
    for locs in sorted(grab_locations(word)):
        for sb in semi_bad:
            if sb in locs:
                semi_bad_locs[locs[0]] = locs[1]


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
        elif status[s] == 'o' and word[s] in all_locs_items['y']:
            yellows.append(word[s])
            sol[s] += word[s]
        elif status[s] == 'y' and word[s] not in semi_bad:
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
    # Filtering only for words that have greens and yellows in them
    mw = [word for word in matchingwords if all(x in word for x in mash) == True]

    print('------', '\n')
    print('Current pattern for this word:')
    print(patterns)
    print('------', '\n')

    mw_dict = {}
    for word in mw:
        for k,v in char_freq.items():
            if word not in mw_dict:
                mw_dict[word] = 0
            if k in word:
                mw_dict[word] += v

    #suggest_word = mw[(random.randint(0,len(mw) - 1))]
    suggest_word = max(mw_dict, key=mw_dict.get)
    return suggest_word, mw, mw_dict, patterns

w, s = guessword()
all_solutions, greens, yellows = attempt(w,s)
y_chars += yellows
g_chars += greens
mash = []
mash += y_chars + g_chars

ss = ''
all_patterns = []
while ss != 'ggggg':
    suggest_word, mw, mw_dict, patterns = compare(mash, all_solutions, bag_of_words)
    all_patterns += patterns
    print('------', '\n')
    print('All patterns for this game:')
    print(all_patterns)
    print('------', '\n')
    print('Next suggestion ****',suggest_word,'**** This word has the highest score: ', suggest_word, '(Score: ', mw_dict[suggest_word], ')')
    print('------', '\n')
    if len(mw) < 10:
        print('You only have 10 or less words left in the word bank:')
        print(mw_dict)
    ww, ss = guessword()
    all_solutions, g, y = attempt(ww, ss)
    y_chars += g
    g_chars += y
    mash += g + y
    bag_of_words = mw.copy()
