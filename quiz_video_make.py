import os
import subprocess

import sys

# 1단계: 퀴즈 생성 및 시트 저장
from step1_quiz_collection import main as step1_main

# 2단계: 카드뉴스 이미지 생성
from step2_quiz_card_product import main as step2_main

# 3단계: 동영상 생성
from Step3_video_make import main as step3_main

# 환경 점검 및 bgm 재인코딩 함수 추가

def check_bgm_and_env():
    bgm_path = "asset/bgm.mp3"
    if not os.path.exists(bgm_path):
        print(f"[오류] 배경음악 파일이 없습니다: {bgm_path}")
        sys.exit(1)
    if os.path.getsize(bgm_path) < 1000:
        print(f"[오류] 배경음악 파일 용량이 너무 작습니다(손상 가능): {bgm_path}")
        sys.exit(1)
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        print("[ffmpeg 버전 정보]", result.stdout.splitlines()[0])
    except Exception as e:
        print("[오류] ffmpeg가 설치되어 있지 않습니다.")
        sys.exit(1)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[경고] OPENAI_API_KEY 환경변수가 없지만, 코드 내 기본값을 사용합니다.")
    else:
        print("[점검 완료] OPENAI_API_KEY 환경변수 정상.")
    print("[점검 완료] bgm.mp3, ffmpeg, OPENAI_API_KEY 모두 정상입니다.")

def reencode_bgm():
    bgm_path = "asset/bgm.mp3"
    fixed_path = "asset/bgm_fixed.mp3"
    cmd = [
        "ffmpeg", "-y", "-i", bgm_path,
        "-acodec", "libmp3lame", "-ab", "192k", fixed_path
    ]
    subprocess.run(cmd, check=True)
    print(f"[재인코딩 완료] {fixed_path} 파일 생성됨. 이후 동영상 생성 시 이 파일을 사용하세요.")
    return fixed_path

if __name__ == "__main__":
    check_bgm_and_env()
    reencode_bgm()
    print("[STEP1] 세대별 퀴즈 생성 및 시트 저장")
    step1_main()
    print("[STEP2] 카드뉴스 이미지 생성")
    step2_main()
    print("[STEP3] 동영상 생성 및 합치기")
    step3_main()
    print("[완료] quiz_video_make.py 전체 자동화가 끝났습니다.") 