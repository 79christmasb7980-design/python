import os
import shutil

# 다운로드 폴더 경로 설정
download_folder = r"C:\Users\student\Downloads"

# 이동할 폴더와 확장자 정의
file_types = {
    "images": [".jpg", ".jpeg"],
    "data": [".csv", ".xlsx"],
    "docs": [".txt", ".doc", ".pdf"],
    "archive": [".zip"]
}

# 정의된 파일 종류에 따라 폴더를 생성하고 파일을 이동
for folder_name, extensions in file_types.items():
    # 생성할 폴더 경로
    target_folder = os.path.join(download_folder, folder_name)
    
    # 폴더가 존재하지 않으면 생성
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        print(f"'{target_folder}' 폴더를 생성했습니다.")

    # 다운로드 폴더 내의 모든 파일 목록을 가져옴
    for filename in os.listdir(download_folder):
        # 파일의 전체 경로
        source_file = os.path.join(download_folder, filename)
        
        # 파일인 경우에만 처리
        if os.path.isfile(source_file):
            # 파일의 확장자를 소문자로 가져옴
            file_extension = os.path.splitext(filename)[1].lower()
            
            # 해당 확장자가 이동 대상 확장자 목록에 포함되어 있으면 이동
            if file_extension in extensions:
                shutil.move(source_file, target_folder)
                print(f"'{filename}'을(를) '{target_folder}'(으)로 이동했습니다.")

print("\n파일 정리가 완료되었습니다.")

#폴더별 날짜 폴더를 생성하여 분류하는 기능은 추