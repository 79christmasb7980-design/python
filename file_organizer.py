import os
import shutil
from pathlib import Path

# 다운로드 폴더 경로
DOWNLOAD_FOLDER = r"C:\Users\student\Downloads"

# 파일 분류 규칙 (확장자: 대상 폴더)
FILE_CATEGORIES = {
    'images': ['.jpg', '.jpeg'],
    'data': ['.csv', '.xlsx'],
    'docs': ['.txt', '.doc', '.pdf'],
    'archive': ['.zip']
}


def create_destination_folders():
    """필요한 대상 폴더들을 생성합니다."""
    for folder_name in FILE_CATEGORIES.keys():
        folder_path = os.path.join(DOWNLOAD_FOLDER, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"✓ 폴더 생성: {folder_path}")
        else:
            print(f"✓ 폴더 존재: {folder_path}")


def get_destination_folder(file_extension):
    """파일 확장자에 따라 대상 폴더를 반환합니다."""
    file_extension = file_extension.lower()
    for folder_name, extensions in FILE_CATEGORIES.items():
        if file_extension in extensions:
            return folder_name
    return None


def organize_files():
    """다운로드 폴더의 파일들을 분류하여 이동합니다."""
    if not os.path.exists(DOWNLOAD_FOLDER):
        print(f"❌ 다운로드 폴더가 존재하지 않습니다: {DOWNLOAD_FOLDER}")
        return
    
    moved_count = 0
    skipped_count = 0
    
    # 다운로드 폴더의 모든 파일 순회
    for item in os.listdir(DOWNLOAD_FOLDER):
        item_path = os.path.join(DOWNLOAD_FOLDER, item)
        
        # 디렉토리는 스킵
        if os.path.isdir(item_path):
            # 이미 생성된 폴더는 건너뛰기
            if item not in FILE_CATEGORIES:
                print(f"📁 디렉토리 (건너뜀): {item}")
            continue
        
        # 파일 확장자 추출
        file_name, file_extension = os.path.splitext(item)
        
        # 대상 폴더 결정
        destination_folder = get_destination_folder(file_extension)
        
        if destination_folder:
            destination_path = os.path.join(DOWNLOAD_FOLDER, destination_folder, item)
            
            try:
                # 파일 이동
                shutil.move(item_path, destination_path)
                print(f"✓ 이동 완료: {item} → {destination_folder}/")
                moved_count += 1
            except Exception as e:
                print(f"❌ 이동 실패: {item} - {str(e)}")
        else:
            print(f"⊘ 분류 안 함: {item} (해당 규칙 없음)")
            skipped_count += 1
    
    # 결과 요약
    print("\n" + "="*50)
    print(f"처리 완료!")
    print(f"이동된 파일: {moved_count}개")
    print(f"건너뛴 파일: {skipped_count}개")
    print("="*50)


def main():
    print("파일 정렬 시작...")
    print(f"대상 폴더: {DOWNLOAD_FOLDER}\n")
    
    # 필요한 폴더 생성
    print("[1단계] 대상 폴더 생성")
    create_destination_folders()
    
    # 파일 정렬
    print("\n[2단계] 파일 이동")
    organize_files()


if __name__ == "__main__":
    main()
