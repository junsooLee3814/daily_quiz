import os
import pickle
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    return build('youtube', 'v3', credentials=creds)
    #pickle_file = 'youtube_credentials_1.pickle'
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            creds = pickle.load(token)
    else:
        raise Exception("인증 토큰 파일이 없습니다. 로컬에서 먼저 인증을 진행하세요.")
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(pickle_file, 'wb') as token:
            pickle.dump(creds, token)
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
    upload_video(
        '../video_merge/combined_video.mp4',
        '자동 업로드 테스트',
        '이 영상은 자동 업로드 테스트입니다.',
        ['테스트', '자동업로드']
    )
