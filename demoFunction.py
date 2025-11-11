#demo Funcion
def setValue(newValue):
    x = newValue
    print("함수내부:", x)

#2) 함수 호출
retValue =setValue(5)
print(retValue)

#함수 정의
def swap(x,y):
    return y,x
#호출
result =swap(3,4)
print(result)

#디버깅연습 함수
def intersect(prelist, postlist):
    result =[]
    for x in prelist:   #→ 첫 번째 자료에서 한 항목씩 꺼냄.
        if x in postlist and x not in result:  # if x in postlist → 두 번째 자료에도 있으면, and x not in result → 아직 결과에 없으면
            result.append(x) #→ 결과 리스트에 추가.
    return result

#호출
print(intersect("HAM","SPAM"))  

#LGB 이름 해석 규칙

X=5 #전역 변수 (전체 변수)
def func(a):
    return a+ X

print(func(1))

def func2(a):
    X=10 #지역 변수 (여기서만 써라)
    return a+ X

print(func2(1))

#분기 반복문

def times(a=10,b=20):
    return a*b
print(times())
print(times(5))
print(times(5,6))

#기본값 명시
def connectURL(server, port):
    strURL = "http://" + server + ":" +port
    return strURL
print(connectURL ("daum.net","80"))

print(connectURL(port="80",server="daum.net"))

#가변인자 처리
def union(*ar):
    result = []
    for item in ar:
        for x in item:
            if x not in result:
                result.append(x)
    return result

#호출
print(union("HAM","EGG"))
print(union("HAM","EGG","SPAM"))