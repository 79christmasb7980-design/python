strName = "Not Class Member" #전역 변수

class DemoString:
    def __init__(self):
        #인스턴스 멤버변수
        self.strName = "" 
    def set(self, msg):
        self.strName = msg
    def print(self):
        #꼼꼼하게 코딩 해야 한다. 
       # print(strName) 전역 변수를 가져옴
        print(self.strName) #인스턴스 멤버 변수를 가져와야 함

#인스턴스 생성
d = DemoString()
d.set("First Message")
d.print()
