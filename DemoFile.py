#demoFile.py
#쓰기
f=open("demo.txt", "w", encoding="utf-8")
f.write("첫번째\n두번째\n세번째\n")
f.close()  #닫기를 잊지말기

#읽기
f=open("demo.txt", "rt", encoding="utf-8")
content=f.read()
print(content)
f.close()

#문자열 데이터 처리 메서드
data =" spam and ham "
result = data.strip()  #양쪽 공백 제거
print(data)
print(result)
result2 = data.replace("spam", "eggs")  #문자열 치환
print(result2)
lst = result2.split()  #문자열 분리
print(lst)
print(":)".join(lst))  #문자열 결합+

print(len(data))  #문자열 길이
print(data.upper())  #대문자 변환
print(data.lower())  #소문자 변환
print(data.find("and"))  #문자열 위치 찾기
print("hello".upper())  #소문자 변환
print("2580".isdecimal)  #문자 개수 세기

#정규표현식
import re
#선택한 블럭을 주석 처리:ctrl+/
# result = re.match("[0-9]*th", " 35th") #match는 공백 포함 못함
# print(result)
# print(result.group())

result = re.search("[0-9]*th", " 35th")
print(result)
print(result.group())

#단어 검색
result = re.search("apple", "this is apple")
print(result.group())

result = re.search("\d{4}", "올해는 2025년입니다.")
print(result.group())

result = re.search("\d{5}", "우리 동네는 12345번지 입니다.")
print(result.group())