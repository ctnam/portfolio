

import random

def convert(u):
    space_i = u.find(' ')
    start_i = space_i+1
    converted_u = u[start_i:]
    return converted_u

question_list = [x for x in range(1,148)]
ql = ['n/a']
with open('questionlist.txt','r') as f:
    run = f.read()
    for u in run.splitlines():
        ql.append(u)
passed_ql = list()

set1 = [70, 117, 74, 94, 139, 80, 6, 100, 61, 68,
        19, 133, 137, 38, 3, 87, 24, 59, 43, 110,
        121, 120, 62, 48, 4, 45, 65, 105, 111, 147,
        106, 37, 85, 79, 124, 126, 60, 91, 72, 104,
        130, 10, 103, 92, 75, 82, 93, 34, 109, 69,
        73, 25, 115, 11, 20, 58, 53, 114, 29, 31,
        144, 141, 32, 28, 143, 118, 88, 63, 64, 2,
        119, 136, 33, 77, 47, 35, 49, 54, 71, 98,
        50, 140, 101, 81, 123, 95, 23, 102, 27, 7,
        44, 107, 39, 125, 127, 78, 36, 84, 134, 129,
        51, 15, 135, 18, 96, 83, 89, 146, 5, 14,
        76, 22, 30, 112, 57, 90, 21, 142, 12, 41,
        13, 66, 132, 56, 40, 97, 52, 116, 122, 128,
        8, 131, 1, 17, 26, 46, 113, 55, 9, 108]

question_listset = set(question_list)-set(set1)
question_list = list(question_listset)

onesharp = []
twosharp = list()
while True:
    random_question = random.choice(question_list)
    print('Mr. Heindl: ' + convert(ql[random_question]))
    passed_ql.append(random_question)
    question_list.remove(random_question)
    endkey = input('')
    if endkey == '#' or endkey.lower() == '#done':
        onesharp.append(random_question)
    if endkey == '##' or endkey.lower() == '##done':
        twosharp.append(random_question)
    if endkey.lower() == 'done' or endkey.lower() == '#done' or endkey.lower() == '##done':
        print('\n')
        break
    
print('passed '+str(passed_ql))
print('# '+str(onesharp))
print('## '+str(twosharp))

import time
struct_time = time.localtime()
year = time.localtime().tm_year
month = time.localtime().tm_mon
day = time.localtime().tm_mday
hour = time.localtime().tm_hour
minute = time.localtime().tm_min
second = time.localtime().tm_sec
with open('logs.txt','a') as f:
    current_time = str(day) +'-'+ str(month) +'-'+ str(year) +' '+ str(hour) +':'+ str(minute) +':'+ str(second)
    line1 = '*'*8+current_time+'*'*8+'\n'
    line2 = 'passed '+str(passed_ql)+'\n'
    line3 = '# '+str(onesharp)+'\n'
    line4 = '## '+str(twosharp)+'\n'
    log = line1+line2+line3+line4
    f.write(log)
    
