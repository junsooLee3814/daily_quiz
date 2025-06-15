import gspread
from oauth2client.service_account import ServiceAccountCredentials
import openai
from datetime import datetime
import os
import re
from dotenv import load_dotenv
import sys

# .env 파일에서 환경변수 로드
load_dotenv()

# 공통 상수
SERVICE_ACCOUNT_FILE = 'google_service_account.json'
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("[에러] OPENAI_API_KEY 환경변수가 없습니다. .env 파일 또는 환경변수를 확인하세요.")
    sys.exit(1)
SHEET_NAMES = ['youth', 'adult', 'senior']
EXPECTED_COLS = 8

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_today():
    return datetime.now().strftime('%Y-%m-%d')

def get_weekday():
    return ['월요일','화요일','수요일','목요일','금요일','토요일','일요일'][datetime.now().weekday()]

def get_gsheet(sheet_name):
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPE)
    client_gs = gspread.authorize(creds)
    sheet = client_gs.open(sheet_name)
    return sheet

def extract_first_list(text):
    import re
    text = text.strip()
    match = re.search(r'\[.*?\]', text, re.DOTALL)
    if match:
        return match.group(0)
    return text

def gpt4o_quiz_request(prompt, idx=0, debug=False):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=512
    )
    text = response.choices[0].message.content
    list_text = extract_first_list(text)
    import ast
    try:
        quiz = ast.literal_eval(list_text)
        if isinstance(quiz, list) and len(quiz) == EXPECTED_COLS and quiz[0] == get_today() and quiz[1] == get_weekday():
            return quiz
    except Exception as e:
        print(f"[에러] 파싱 실패: {e}")
        if debug:
            with open(f'gpt4o_response_{idx}.txt', 'w', encoding='utf-8') as f:
                f.write(text)
    print(f"[에러] GPT-4o 응답 확인 필요: {text}")
    return None

def save_to_sheet(sheet, quiz):
    sheet.append_row(quiz)

def get_today_quiz():
    today = get_today()
    sh = get_gsheet('todays quizes')
    results = []
    for sheet_name in SHEET_NAMES:
        ws = sh.worksheet(sheet_name)
        rows = ws.get_all_values()
        quiz_row = None
        today_rows = [row for row in rows[1:] if row and row[0] == today]
        if today_rows:
            quiz_row = today_rows[-1]
        else:
            print(f"[경고] {sheet_name} 시트에 오늘 날짜({today}) 데이터가 없습니다.")
            quiz_row = [''] * EXPECTED_COLS
        results.append(quiz_row)
    return results

def get_latest_result_folder(base_dir='result_quiz_card'):
    all_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    date_dirs = [d for d in all_dirs if d and d[0].isdigit()]
    if not date_dirs:
        raise FileNotFoundError('result_quiz_card 내에 날짜_시간 폴더가 없습니다.')
    date_dirs.sort(reverse=True)
    latest_dir = os.path.join(base_dir, date_dirs[0])
    return latest_dir

def check_files(latest_dir):
    required_files = [
        os.path.join('asset', 'intro_thumbnail.png'),
        os.path.join('asset', 'bgm.mp3'),
    ]
    for gen in SHEET_NAMES:
        required_files.append(os.path.join(latest_dir, gen, 'quiz_카드.png'))
        required_files.append(os.path.join(latest_dir, gen, 'answer_카드.png'))
    for f in required_files:
        if not os.path.exists(f):
            raise FileNotFoundError(f'필수 파일이 없습니다: {f}')
    return required_files

def make_result_folder(base_dir='result_merge_quiz'):
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_dir = os.path.join(base_dir, now)
    os.makedirs(result_dir, exist_ok=True)
    return result_dir 