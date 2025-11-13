#web2.py
from bs4 import BeautifulSoup
#웹서버 요청
import urllib.request

#파일로 저장
f = open("clien.txt", "wt", encoding="utf-8")

#10개 페이지 처리:페이지 처리
for i in range(0,10):
    url = "https://www.clien.net/service/board/sold?&od=T31&category=0&po=" + str(i) #i는 정수값
    print(url)
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, "html.parser")

    #검색
    list = soup.find_all("span", attrs={"data-role":"list-title-text"})
    for tag in list:
        title = tag.text.strip()
        print(title)
        f.write(title + "\n")

    #원하는 데이터 추출

        
f.close()

    #<span class="subject">아이폰 12 미니 팝니다
    # </span>