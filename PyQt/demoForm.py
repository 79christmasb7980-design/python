#DemoForm.py
#DemoForm.ui(화면단) + DemoForm.py(로직단) 자동 생성
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import *

#UI파일 연결
form_class = uic.loadUiType(".\PyQt\DemoForm.ui")[0]

#폼 클래스 정의
class DemoForm(QDialog, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label.setText("첫번째 PyQt 코딩")

#직접모듈을 실행한 경우에만 실행
if __name__ == "__main__":    
    app = QApplication(sys.argv)
    demo = DemoForm()
    demo.show()
    app.exec_()   #sys.exit(app.exec_()) 와 동일
