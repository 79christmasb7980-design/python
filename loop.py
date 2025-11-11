# demo loop
value =5
while value > 0:  # 0이 나오면 빠져나와라
    print(value)
    value -=1

print("for in 루프")
lst = [100,200,300]
for i in lst:
    print(i)

#구구단 출력

for x in [1,2,3,4,5,6,7,8,9]:
    print("---{0}단---".format(x))
    for y in [1,2,3,4,5,6,7,8,9]:
        print("{0}*{1}={2}".format(x,y,x*y))

print("---range()함수---")
print(list(range(10)))
print(list(range(2000,2026)))
print(list(range(1,32)))

print("---리스트 컴프리핸션---")
lst = list(range(1,11))
print([i**2 for i in lst if i>5])
d = {100:"Apple", 200:"Banana"}
print([v.upper() for v in d.values()])
print([v.capitalize() for v in d.values()])  #첫자만 대문자로 변경 capitalize