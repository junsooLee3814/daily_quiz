import os
import pickle
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    creds = Credentials.from_authorized_user_file('youtube_uploader/token.json', SCOPES)
    return build('youtube', 'v3', credentials=creds)


def upload_video(file_path, title, description, tags):
    youtube = get_authenticated_service()
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': 'private'
        }
    }
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=file_path
    )
    response = request.execute()
    print('업로드 성공! 영상 ID:', response['id'])

if __name__ == '__main__':
    # 오늘 날짜 구하기
    today = datetime.now().strftime('%Y%m%d')

    # 제목, 설명, 태그 자동 생성
    title = f"퀴즈#{today} 오늘퀴즈!!이 포스팅은 쿠팡파트너스 활동의 일환으로 일정보수를 지급받습니다"
    description = "퀴즈로 뇌를 깨워보세요. 맞출 수 있을까요?이 포스팅은 쿠팡파트너스 활동으로 일정보수를 지급받습니다"
    tags = ["퀴즈", "교육", "상식", "게임", "문제풀이", "IQ", "재미", "학습"]

    upload_video(
        'video_merge/combined_video.mp4',
        title,
        description,
        tags
    )

