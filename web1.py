# web1.py

#크롤링하는 코드작성
from bs4 import BeautifulSoup

#페이지를 로딩
page = open("chap09_test.html", "rt", encoding="utf-8").read()

#스프객체를 생성
soup = BeautifulSoup(page, "html.parser")

#검색
#print(soup.prettify())  #전체 출력
#<p>태크 전체 검색
#print(soup.find_all("p"))
#첫번째 <p>태그만 검색
#print(soup.find("p"))  #첫번째 <p>태그만 검색
#조건 검색: <p class="outer-text">
#print(soup.find_all("p", attrs={"class":"outer-text"})) #attrs 딕셔너리로 조건 전달
#태그내부의 문자열: .text 속성
for tag in soup.find_all("p"):
    title = tag.text.strip()  #문자열 양쪽 공백제거
    title = title.replace("\n", " ")  #문자열 내부의 줄바꿈문자 공백으로 변경
    print(title)
