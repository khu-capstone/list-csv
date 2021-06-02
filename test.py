rs = [0,0,0,0]

with open('triples/ul_filter.csv', 'r', encoding='utf-8') as f:
    line = f.readline()
    while line:
        score = int(line.split(',')[0])
        rs[score] += 1
        line = f.readline()
print(rs, sum(rs))

# Explanatory notes
# Footnotes
# Reference
# See also
# Notes
# Sources
# Table notes

# ol
# [626, 85, 120, 84] 915
# 69%, 9%, 13%, 9%

# ul
# [667, 73, 65, 122] 927
# 72%, 8%, 7%, 13%
