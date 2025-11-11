#개발자 클래스를 정의: id , name, skill 속성 포함
class Developer:    
    def __init__(self, dev_id, name, skill):
        self.dev_id = dev_id
        self.name = name
        self.skill = skill

    def display_info(self):
        #f-string을 사용하여 개발자 정보 반환
        return f"ID: {self.dev_id}, Name: {self.name}, Skill: {self.skill}"
#개발자 인스턴스 생성
dev1 = Developer(1, "Alice", "Python")      
dev2 = Developer(2, "Bob", "JavaScript")
#개발자 정보 출력
print(dev1.display_info())  
print(dev2.display_info())
