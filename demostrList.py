# demostrList.py

strA= 'Python'
strB= "파이썬은 좋아"

print(len(strA))
print(len(strB))
print(strA[1])
print(strA[-2:])
print("hi")

# 리스트 연습
colors = ["red","green"]
print(len(colors))
colors.append("white")
colors
print(colors)
colors.insert(1,"black")
colors
colors.reverse()
print(colors)
colors.remove("red")
print(colors)

#  set
a= {10,1,2,3,4,4}
b= {3,4,5,6,6}
#print(a[0]) 은 순서가 정해져 있지 않아 오류 발생함
print(a.union(b))
print(a.intersection(b))
print(a.difference(b))

# Tuple 연습
tp=(10,20,30)
print(tp)
print(len(tp))
print(tp[0])

#함수 정의
def calc(a,b):
    return a+b, a*b

#함수 호출
result = calc(3,4)
print(result)

args= (5,6)
print(calc(*args))

#형식 변환 type casting
a= set((1,2,3))
print(a)
b= list(a)
b.append(30)
print(b)
