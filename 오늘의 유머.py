# 오늘의 유머

from bs4 import BeautifulSoup
import urllib.request
import re 

#User-Agent를 조작하는 경우(아이폰에서 사용하는 사파리 브라우져의 헤더) 
hdr = {'User-agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/603.1.23 (KHTML, like Gecko) Version/10.0 Mobile/14E5239e Safari/602.1'}

#파일로 저장
f= open("todayhumor r1.txt", "wt", encoding="utf-8")

for n in range(1,5):
        #오늘의 유머 주소 
        data ='https://www.todayhumor.co.kr/board/list.php?table=bestofbest&page=' + str(n)
        #웹브라우져 헤더 추가 
        req = urllib.request.Request(data, \
                                    headers = hdr)
        data = urllib.request.urlopen(req).read()
        #한글이 깨지는 경우 디코딩 utf-8로
        page = data.decode('utf-8', 'ignore')
        soup = BeautifulSoup(page, 'html.parser')
        list = soup.find_all('td', attrs={'class':'subject'})

        for item in list:
                try:
                    title = item.find('a').text.strip()  #<a>태그 안의 text 추출 
                    #특정 속성을 검색
                    href = item.find('a')['href']
                    if re.search('일본', title): #조건 검색
                        print(title.strip())
                        print("https://www.todayhumor.co.kr/" + href)
                        f.write('a' + title + "\n")
                        #print('https://www.clien.net'  + item['href'])
                        f.write("https://www.todayhumor.co.kr/" + href + "\n")
                except:
                        pass
f.close()
#<td class="subject"
#<a href="/board/view.php">한국 아마추어 러닝씬에 홀연히 등장한 노력의 천재</a>        
#<img src="//www.todayhumor.co.kr/board/images/list_icon_pencil.gif?2" alt="창작글" style="margin-right:3px;top:2px;position:relative">
