# demoRandom.py
import random   

print(random.random())  #0.0~1.0미만의 실수 난수 생성
print(random.randint(1, 10))  #1~10사이의 정수 난수 생성
print(random.randrange(20) for i in range(5))
  #1~10사이의 홀수 난수 생성
print(random.uniform(2.0, 5.0))  #2.0~5.0미만의 실수 난수 생성
print( random.sample(range(1,46), 5) )  
print( random.sample(range(46), 5) )    #1~45사이의 숫자 중에서 6개를 중복없이 추출

from os.path import *
import os

fileName = "c:\\python310\\python.exe"
print(basename(fileName))
print(abspath(fileName))
print(abspath("python.exe"))

if exists(fileName):
    print("파일 크기:", getsize(fileName))
else:
    print("파일이 존재하지 않습니다.")  