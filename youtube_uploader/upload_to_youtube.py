import textwrap
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    """
    OAuth 2.0 인증을 통해 YouTube API 서비스 객체를 생성합니다.
    'youtube_uploader/token.json' 파일이 필요합니다.
    """
    creds = Credentials.from_authorized_user_file('youtube_uploader/token.json', SCOPES)
    return build('youtube', 'v3', credentials=creds)


def upload_video(file_path, title, description, tags):
    """
    지정된 파일 경로의 동영상을 YouTube에 업로드합니다.
    """
    try:
        youtube = get_authenticated_service()
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': '24'  # 카테고리 ID (24: Entertainment, 27: Education)
            },
            'status': {
                'privacyStatus': 'private'  # 동영상 공개 상태 (private, public, unlisted)
            }
        }
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=file_path
        )
        response = request.execute()
        print(f"업로드 성공! 영상 ID: {response['id']}")
    except FileNotFoundError:
        print(f"오류: '{file_path}' 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
    except Exception as e:
        print(f"업로드 중 오류가 발생했습니다: {e}")

if __name__ == '__main__':
    # 오늘 날짜 구하기 (YYYYMMDD 형식)
    today = datetime.now().strftime('%Y%m%d')

    # SEO에 최적화된 영상 제목 (60자 이내 권장)
    title = f"{today}🧠 오늘의 퀴즈 | 당신은 몇 개나 맞출 수 있을까? 이 숏츠는 쿠팡파트너스 활동으로 일정보수를 지급받습니다."

    # SEO에 최적화된 영상 설명
    description = textwrap.dedent(f"""
        🧠 {today} 당신의 두뇌를 깨워줄 오늘의 퀴즈! 이 숏츠는 쿠팡파트너스 활동으로 일정보수를 지급받습니다.
        재미있는 상식 퀴즈로 하루를 시작해보세요!
        친구, 가족과 함께 풀어보며 세대간 소통의 시간을 가져보세요.
        당신은 몇 개나 맞출 수 있을까요? 댓글로 정답을 알려주세요!
        #오늘의퀴즈 #상식퀴즈 #두뇌게임 #퀴즈챌린지 #재미있는퀴즈 #교육콘텐츠 #세대소통
    """)

    # SEO에 최적화된 태그
    tags = [
        "퀴즈", "오늘의퀴즈", "상식퀴즈", "교육", "두뇌게임", "퀴즈챌린지",
        "재미있는퀴즈", "문제풀이", "IQ테스트", "상식문제", "학습", "세대소통",
        "퀴즈영상", "교육콘텐츠", "브레인게임"
    ]
    
    video_file_path = 'video_merge/combined_video.mp4'

    upload_video(
        video_file_path,
        title,
        description,
        tags
    )
