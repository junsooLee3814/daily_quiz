import re
from common_utils import get_gsheet, gpt4o_quiz_request, save_to_sheet, SHEET_NAMES, get_today, get_weekday
from datetime import datetime

# 구글시트 문서명과 시트명
SPREADSHEET_NAME = 'todays quizes'

# 퀴즈 프롬프트 (구글시트 열 순서에 맞게)
PROMPTS = [
    f"청소년을 위한 최신 트렌드, 진학, 학업, 시험, 문화, 게임, IT 등과 관련된 흥미로운 객관식 퀴즈 1개를 만들어줘. 반드시 아래 형식의 파이썬 리스트 그대로만 답변해. 첫 번째 값은 '{get_today()}', 두 번째 값은 '{get_weekday()}'로 고정하고, [일자, 요일, 문제, 보기1, 보기2, 정답, 후킹문구, 썸네일문구] 순서로 파이썬 리스트로 반환해. 예시: ['{get_today()}', '{get_weekday()}', '문제', '보기1', '보기2', '정답', '후킹문구', '썸네일문구']",
    f"성인을 위한 재테크, 사회, 경제, 직장, 트렌드 등과 관련된 흥미로운 객관식 퀴즈 1개를 만들어줘. 반드시 아래 형식의 파이썬 리스트 그대로만 답변해. 첫 번째 값은 '{get_today()}', 두 번째 값은 '{get_weekday()}'로 고정하고, [일자, 요일, 문제, 보기1, 보기2, 정답, 후킹문구, 썸네일문구] 순서로 파이썬 리스트로 반환해. 예시: ['{get_today()}', '{get_weekday()}', '문제', '보기1', '보기2', '정답', '후킹문구', '썸네일문구']",
    f"노년층을 위한 재테크, 정치, 경제, 추억, 건강, 시대상, 대중문화 등과 관련된 흥미로운 객관식 퀴즈 1개를 만들어줘. 반드시 아래 형식의 파이썬 리스트 그대로만 답변해. 첫 번째 값은 '{get_today()}', 두 번째 값은 '{get_weekday()}'로 고정하고, [일자, 요일, 문제, 보기1, 보기2, 정답, 후킹문구, 썸네일문구] 순서로 파이썬 리스트로 반환해. 예시: ['{get_today()}', '{get_weekday()}', '문제', '보기1', '보기2', '정답', '후킹문구', '썸네일문구']"
]

def main():
    print(f"[GPT-4o에게 세대별 퀴즈 요청 중...] 열 순서: 일자({get_today()}), 요일({get_weekday()}), 문제, 보기1, 보기2, 정답, 후킹문구, 썸네일문구")
    quizzes = []
    for idx, prompt in enumerate(PROMPTS):
        quiz = gpt4o_quiz_request(prompt, idx, debug=True)
        quizzes.append(quiz)
    if any(q is None for q in quizzes):
        print("[에러] 세대별 퀴즈 데이터가 누락되었습니다. GPT-4o 응답을 확인하세요.")
        return
    print("[구글시트 저장 중...] 열 순서: 일자, 요일, 문제, 보기1, 보기2, 정답, 후킹문구, 썸네일문구")
    sh = get_gsheet(SPREADSHEET_NAME)
    for sheet_name, quiz in zip(SHEET_NAMES, quizzes):
        sheet = sh.worksheet(sheet_name)
        save_to_sheet(sheet, quiz)
        print(f"[{sheet_name}] 저장 완료: {quiz[2]}")
    print("[완료]")

if __name__ == "__main__":
    main() 