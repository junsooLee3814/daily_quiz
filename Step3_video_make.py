import os
import subprocess
import shutil

GENERATIONS = ['youth', 'adult', 'senior']
VIDEO_DIR = 'video'
CARD_DIR = 'card'
ASSET_DIR = 'asset'
VIDEO_MERGE_DIR = 'video_merge'
WIDTH, HEIGHT = 1080, 1920

# 각 카드별 영상 길이(초)
DURATIONS = {
    'intro': 2,
    'quiz': 5,
    'answer': 3
}

# 카드 파일명 패턴
CARD_TYPES = ['intro_카드.png', 'quiz_카드.png', 'answer_카드.png']

# ffmpeg로 이미지 -> mp4 (단순 버전)
def make_zoom_video(img_path, out_path, duration):
    try:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", img_path,
            "-t", str(duration),
            "-vf", f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-r", "25",
            out_path
        ]
        print(f"[FFmpeg 실행] {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print(f"[동영상 생성 완료] {out_path}")
    except subprocess.CalledProcessError as e:
        print(f"[FFmpeg 오류] {e}")
        # 더 간단한 명령어로 재시도
        cmd_simple = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", img_path,
            "-t", str(duration),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-vf", f"scale={WIDTH}:{HEIGHT}",
            out_path
        ]
        print(f"[FFmpeg 재시도] {' '.join(cmd_simple)}")
        subprocess.run(cmd_simple, check=True)

# ffmpeg로 여러 mp4 합치기
def merge_videos(video_list, out_path):
    try:
        with open("video_list.txt", "w", encoding="utf-8") as f:
            for v in video_list:
                abs_path = os.path.abspath(v).replace('\\', '/')
                f.write(f"file '{abs_path}'\n")
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", "video_list.txt",
            "-c", "copy",
            out_path
        ]
        print(f"[동영상 합치기 실행] {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print(f"[동영상 합치기 완료] {out_path}")
    except subprocess.CalledProcessError as e:
        print(f"[동영상 합치기 오류] {e}")
        raise
    finally:
        if os.path.exists("video_list.txt"):
            os.remove("video_list.txt")

# 배경음악 삽입 (단순 버전)
def add_bgm_to_video(video_path, bgm_path, out_path, total_duration, fadein=1, fadeout=2):
    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", bgm_path,
            "-filter_complex", f"[1:a]volume=0.3[a]",
            "-map", "0:v:0", "-map", "[a]",
            "-shortest",
            "-c:v", "copy",
            "-c:a", "aac",
            out_path
        ]
        print(f"[BGM 추가 실행] {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print(f"[BGM 추가 완료] {out_path}")
    except subprocess.CalledProcessError as e:
        print(f"[BGM 추가 오류] {e}")
        # BGM 없이 비디오만 복사
        shutil.copy2(video_path, out_path)
        print(f"[BGM 없이 복사 완료] {out_path}")

# 폴더 내 모든 파일/폴더 삭제
def remove_all_in_folder(folder):
    if not os.path.exists(folder):
        return
    for root, dirs, files in os.walk(folder, topdown=False):
        for name in files:
            try:
                os.remove(os.path.join(root, name))
            except Exception as e:
                print(f"[파일 삭제 실패] {os.path.join(root, name)}: {e}")
        for name in dirs:
            try:
                shutil.rmtree(os.path.join(root, name))
            except Exception as e:
                print(f"[폴더 삭제 실패] {os.path.join(root, name)}: {e}")

def main():
    merged_paths = []
    temp_video_files = []
    ordered_video_files = []
    total_duration = 0
    for gen in GENERATIONS:
        card_folder = os.path.join(CARD_DIR, gen)
        video_folder = os.path.join(VIDEO_DIR, gen)
        os.makedirs(video_folder, exist_ok=True)
        gen_video_files = []
        for idx, card_type in enumerate(CARD_TYPES):
            img_path = os.path.join(card_folder, card_type)
            out_path = os.path.join(video_folder, f'{card_type.replace("_카드.png", "")}.mp4')
            duration = DURATIONS[card_type.split('_')[0]]
            make_zoom_video(img_path, out_path, duration)
            gen_video_files.append(out_path)
            temp_video_files.append(out_path)
            ordered_video_files.append(out_path)
            total_duration += duration
        merged_path = os.path.join(VIDEO_DIR, f'{gen}_merged_video.mp4')
        merge_videos(gen_video_files, merged_path)
        merged_paths.append(merged_path)
    # 세대별 merged_video.mp4 3개를 합치기 (순서대로)
    combined_path = os.path.join(VIDEO_DIR, 'combined_video_no_bgm.mp4')
    merge_videos(ordered_video_files, combined_path)
    # 배경음악 삽입
    bgm_path = os.path.join(ASSET_DIR, 'bgm_fixed.mp3')
    # video_merge 폴더 생성 및 최종 파일 저장
    os.makedirs(VIDEO_MERGE_DIR, exist_ok=True)
    final_out_path = os.path.join(VIDEO_MERGE_DIR, 'combined_video.mp4')
    add_bgm_to_video(combined_path, bgm_path, final_out_path, total_duration, fadein=1, fadeout=2)
    print(f"[최종 영상 저장 완료] {final_out_path}")
    # card, video 폴더 내 모든 파일/폴더 삭제
    remove_all_in_folder(CARD_DIR)
    remove_all_in_folder(VIDEO_DIR)

if __name__ == "__main__":
    main() 