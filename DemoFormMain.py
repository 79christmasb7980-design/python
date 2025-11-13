#DemoForm.py
#DemoForm.ui(화면단) + DemoForm.py(로직단) 자동 생성
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import *
from bs4 import BeautifulSoup
#웹서버 요청
import urllib.request


#UI파일 연결
form_class = uic.loadUiType("DemoFormMain.ui")[0]

#폼 클래스 정의 (부모 클래스 : QMainWindow)
class DemoForm(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label.setText("첫번째 PyQt 코딩")
    #슬롯 메소드
    def slot1(self):  #메소드 def 및에 원하는 web 크롤링 코드 추가
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

        self.label.setText("IPA 활용")
    def slot2(self):
        self.label.setText("RPA 활용")
    def slot3(self):
        self.label.setText("Python 활용")       

#직접모듈을 실행한 경우에만 실행
if __name__ == "__main__":    
    app = QApplication(sys.argv)
    demo = DemoForm()
    demo.show()
    app.exec_()   #sys.exit(app.exec_()) 와 동일


#pyinstaller --noconsole --onefile 원하는 파일명.py 실행하면 exe 파일 생성됨
