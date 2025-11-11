# BankAccount.py

#은행의 계정을 표현한 클래스 
class BankAccount:     #BankAccount(object)
    #초기화 메서드
    def __init__(self, id, name, balance):
        #__ 로 내부 매개 변수를 숨김
        self.__id = id
        self.__name = name 
        self.__balance = balance 
    #입금 처리 메서드
    def deposit(self, amount):
        self.__balance += amount 
        print(f"{amount}원이 입금되었습니다. 현재 잔액: {self.balance}원")
    #출금 처리 메서드
    def withdraw(self, amount):
        self.__balance -= amount
        if amount > self.__balance:
            print("잔액이 부족합니다.")
        else:
            self.balance -= amount
            print(f"{amount}원이 출금되었습니다. 현재 잔액: {self.balance}원")
    #결과 문자열로 리턴
    def __str__(self):
        return "{0} , {1} , {2}".format(self.__id, \
            self.__name, self.__balance)
  

#인스턴스 객체를 생성
account1 = BankAccount(100, "전우치", 15000)
print(account1)
account1.deposit(5000)
#입금과 출금 표시 방법?
print(account1)
account1.withdraw(3000)
print(account1)
#외부 접금시 AttributeError 발생
#account1.__balance(3000)
