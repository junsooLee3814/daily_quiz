import os
import datetime
import re
from PIL import Image, ImageDraw, ImageFont
from common_utils import get_today_quiz, get_latest_result_folder, check_files, make_result_folder, SHEET_NAMES
import shutil

# 폰트 경로
FONT_PATH = os.path.join('asset', 'Pretendard-Regular.otf')

# 템플릿 이미지 경로
TEMPLATES = {
    'youth': 'asset/template_youth.png',
    'adult': 'asset/template_adult.png',
    'senior': 'asset/template_senior.png',
}

# 저장 경로
now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
today = datetime.datetime.now().strftime('%Y-%m-%d')
BASE_SAVE_DIR = os.path.join('result_quiz_card', now)

# 텍스트 배치(시행착오 기준, 예시)
QUIZ_LAYOUT = {
    'top_margin': 400,  # 더 위로
    'date':   {'size': 45,  'color': (34, 34, 34)},
    'hook':   {'size': 50,  'color': (34, 34, 34)},
    'quiz':   {'size': 60,  'color': (0, 102, 204)},
    'choice': {'size': 50,  'color': (34, 34, 34)},
    'line_gap': 18,
}
ANSWER_LAYOUT = {
    'size': 80,
    'color': (0, 102, 204),
    'line_gap': 40,
}

# 퀴즈 질문 자동 줄바꿈 및 센터정렬 함수
def draw_multiline_center(draw, text, font, x, y, max_width, fill, line_gap, max_lines=5, min_font_size=16):
    orig_size = font.size
    lines = []
    while True:
        words = text.split()
        lines = []
        while words:
            line = ''
            temp_words = words[:]
            while temp_words:
                test_line = line + (temp_words[0] + ' ')
                bbox = font.getbbox(test_line)
                if bbox[2] - bbox[0] > max_width and line:
                    break
                line = test_line
                temp_words.pop(0)
            lines.append(line.strip())
            words = words[len(line.strip().split()):]
        if len(lines) <= max_lines or font.size <= min_font_size:
            break
        font = ImageFont.truetype(FONT_PATH, font.size - 2)
    for line in lines:
        bbox = font.getbbox(line)
        text_w = bbox[2] - bbox[0]
        draw.text((x + (max_width - text_w)//2, y), line, font=font, fill=fill, letter_spacing=-2)
        y += bbox[3] - bbox[1] + line_gap
    return y

def draw_quiz_card(template_path, quiz_data, save_path, sheet_name):
    img = Image.open(template_path).convert('RGBA')
    draw = ImageDraw.Draw(img)
    # 볼드체 폰트 경로 시도 (없으면 기존 FONT_PATH 사용)
    bold_font_path = FONT_PATH.replace('Regular', 'SemiBold')
    if os.path.exists(bold_font_path):
        font_bold = ImageFont.truetype(bold_font_path, QUIZ_LAYOUT['date']['size'])
    else:
        font_bold = ImageFont.truetype(FONT_PATH, QUIZ_LAYOUT['date']['size'])
    font_date = ImageFont.truetype(FONT_PATH, QUIZ_LAYOUT['date']['size'])
    font_hook = ImageFont.truetype(FONT_PATH, QUIZ_LAYOUT['hook']['size'])
    font_quiz = ImageFont.truetype(FONT_PATH, QUIZ_LAYOUT['quiz']['size'])
    font_choice = ImageFont.truetype(FONT_PATH, QUIZ_LAYOUT['choice']['size'])
    y = QUIZ_LAYOUT['top_margin']
    x = 80
    blue = (0, 102, 204)
    # 첫 줄: [sheet_name] (파란색, 볼드)
    draw.text((x, y), f"[{sheet_name}]", font=font_bold, fill=blue, letter_spacing=-2)
    bbox = font_bold.getbbox(f"[{sheet_name}]")
    height = bbox[3] - bbox[1]
    y += height + QUIZ_LAYOUT['line_gap'] * 3  # 첫 줄과 둘째 줄(일자) 사이 간격을 3배로 넉넉히
    # 둘째 줄: 일자.요일 (기존 색상/폰트)
    draw.text((x, y), f"{quiz_data[0]}. {quiz_data[1]}", font=font_date, fill=QUIZ_LAYOUT['date']['color'], letter_spacing=-2)
    bbox = font_date.getbbox(f"{quiz_data[0]}. {quiz_data[1]}")
    height = bbox[3] - bbox[1]
    y += height + QUIZ_LAYOUT['line_gap'] * 2  # 둘째 줄과 후킹문구 사이 2배 간격
    # 후킹문구(빨강) - 자동 줄바꿈, 센터정렬, 최대 2줄
    max_width = img.size[0] - 2 * x
    y = draw_multiline_center(draw, quiz_data[6], font_hook, x, y, max_width, QUIZ_LAYOUT['hook']['color'], QUIZ_LAYOUT['line_gap'], max_lines=2)
    # 후킹문구와 퀴즈 사이 간격 2배로 추가
    y += QUIZ_LAYOUT['line_gap'] * 1.5
    # 퀴즈(볼드/크게/파랑) - 자동 줄바꿈, 센터정렬, 최대 4줄
    y = draw_multiline_center(draw, quiz_data[2], font_quiz, x, y, max_width, QUIZ_LAYOUT['quiz']['color'], QUIZ_LAYOUT['line_gap'], max_lines=4)
    # 퀴즈와 예시 사이 2배 간격 추가
    y += QUIZ_LAYOUT['line_gap'] * 1.5
    # 보기1/2(검정) - 자동 줄바꿈, 센터정렬, 각 1줄
    y = draw_multiline_center(draw, f"예시1: {quiz_data[3]}", font_choice, x, y, max_width, QUIZ_LAYOUT['choice']['color'], QUIZ_LAYOUT['line_gap'], max_lines=1)
    y = draw_multiline_center(draw, f"예시2: {quiz_data[4]}", font_choice, x, y, max_width, QUIZ_LAYOUT['choice']['color'], QUIZ_LAYOUT['line_gap'], max_lines=1)
    img.save(save_path)
    print(f"[저장 완료] {save_path}")

def draw_answer_card(template_path, quiz_data, save_path):
    img = Image.open(template_path).convert('RGBA')
    draw = ImageDraw.Draw(img)
    font_quiz = ImageFont.truetype(FONT_PATH, QUIZ_LAYOUT['quiz']['size'])
    # 볼드체 시도
    bold_font_path = FONT_PATH.replace('Regular', 'SemiBold')
    if os.path.exists(bold_font_path):
        font_answer = ImageFont.truetype(bold_font_path, ANSWER_LAYOUT['size'])
    else:
        font_answer = ImageFont.truetype(FONT_PATH, ANSWER_LAYOUT['size'])
    w, h = img.size
    # 문제(퀴즈) 자동 줄바꿈, 상단 배치 (여백 500)
    quiz_text = quiz_data[2]
    max_width = w - 160
    quiz_top_margin = 500  # 이미지 상단에서 여백
    y = quiz_top_margin
    y = draw_multiline_center(draw, quiz_text, font_quiz, 80, y, max_width, QUIZ_LAYOUT['quiz']['color'], QUIZ_LAYOUT['line_gap'], max_lines=3)
    # 정답 : [정답] (파란색, 볼드) - 자동 줄바꿈 및 센터정렬
    answer_text = f"정답 : {quiz_data[5]}"
    y += 80  # 문제와 정답 사이 넉넉한 간격
    # 정답 텍스트 줄바꿈 및 센터정렬 (최대 2줄, 폰트 크기 최소 24)
    draw_multiline_center(draw, answer_text, font_answer, 80, y, max_width, ANSWER_LAYOUT['color'], ANSWER_LAYOUT['line_gap'], max_lines=2, min_font_size=24)
    img.save(save_path)
    print(f"[저장 완료] {save_path}")

def draw_intro_card(intro_bg_path, save_path, sheet_name, today):
    try:
        img = Image.open(intro_bg_path).convert('RGBA')
    except Exception as e:
        print(f"[경고] intro_thumbnail.png 파일 읽기 실패: {e}")
        # 대체 이미지 생성 (1080x1920 검은 배경)
        img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    # 상단/센터 [세대]
    bold_font_path = FONT_PATH.replace('Regular', 'SemiBold')
    font_size = 90
    if os.path.exists(bold_font_path):
        font = ImageFont.truetype(bold_font_path, font_size)
    else:
        font = ImageFont.truetype(FONT_PATH, font_size)
    w, h = img.size
    text = f"[{sheet_name}]"
    bbox = font.getbbox(text)
    text_w = bbox[2] - bbox[0]
    x = (w - text_w) // 2
    y = 200
    white = (255, 255, 255)
    draw.text((x, y), text, font=font, fill=white, letter_spacing=-2)
    # 하단/센터 오늘 일자
    date_font_size = 60
    if os.path.exists(bold_font_path):
        date_font = ImageFont.truetype(bold_font_path, date_font_size)
    else:
        date_font = ImageFont.truetype(FONT_PATH, date_font_size)
    date_text = today
    bbox = date_font.getbbox(date_text)
    date_w = bbox[2] - bbox[0]
    date_h = bbox[3] - bbox[1]
    date_x = (w - date_w) // 2
    blue = (0, 102, 204)
    line_gap = QUIZ_LAYOUT['line_gap'] if 'line_gap' in QUIZ_LAYOUT else 30
    date_y = h - date_h - 120 - (line_gap * 5)  # 기존 위치에서 5줄(line_gap*5) 위로
    draw.text((date_x, date_y), date_text, font=date_font, fill=blue, letter_spacing=-2)
    img.save(save_path)
    print(f"[인트로 카드 저장 완료] {save_path}")

def main():
    quiz_list = get_today_quiz()
    card_base = 'card'
    intro_bg_path = os.path.join('asset', 'intro_thumbnail.png')
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    for idx, sheet_name in enumerate(SHEET_NAMES):
        quiz_data = quiz_list[idx]
        template_path = TEMPLATES[sheet_name]
        card_dir = os.path.join(card_base, sheet_name)
        os.makedirs(card_dir, exist_ok=True)
        quiz_save_path = os.path.join(card_dir, 'quiz_카드.png')
        answer_save_path = os.path.join(card_dir, 'answer_카드.png')
        intro_save_path = os.path.join(card_dir, 'intro_카드.png')
        draw_quiz_card(template_path, quiz_data, quiz_save_path, sheet_name)
        draw_answer_card(template_path, quiz_data, answer_save_path)
        draw_intro_card(intro_bg_path, intro_save_path, sheet_name, today)

if __name__ == "__main__":
    main() 