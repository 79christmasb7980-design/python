#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""인코딩 문제 테스트"""

import requests
from bs4 import BeautifulSoup

def test_kospi_encoding():
    """KOSPI 데이터로 인코딩 테스트"""
    
    print("🔍 KOSPI 데이터 테스트\n")
    
    url = "https://finance.naver.com/sise/sise_index.naver?code=KOSPI"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers, timeout=10)
    
    # response.text 사용
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    
    if len(tables) < 2:
        print("❌ 테이블을 찾을 수 없습니다.")
        return
    
    print("✅ 테이블 발견!\n")
    print("━━━ KOSPI 상위 5개 종목 ━━━\n")
    
    rows = tables[1].find_all('tr')
    
    for idx, row in enumerate(rows[1:6], 1):
        cells = row.find_all('td')
        if len(cells) >= 3:
            # 링크에서 텍스트 추출
            name_cell = cells[1]
            link = name_cell.find('a')
            stock_name = link.get_text(strip=True) if link else name_cell.get_text(strip=True)
            stock_price = cells[2].get_text(strip=True)
            
            # 유효성 검사
            if stock_name and stock_price and len(stock_name) > 1:
                print(f"{idx}. {stock_name:20} | ₩{stock_price}")
            else:
                print(f"{idx}. [데이터 불완전] {repr(stock_name)}")
    
    print("\n✅ 테스트 완료!")

if __name__ == "__main__":
    test_kospi_encoding()
