import json
import csv
import os

# JSON 파일 로드
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# CSV 파일 저장 함수 (파일이 존재하면 추가, 없으면 생성)
def save_to_csv(file_path, data, headers, append=False):
    mode = "a" if append and os.path.exists(file_path) else "w"
    with open(file_path, mode, encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        if mode == "w":
            writer.writerow(headers)  # 헤더 추가 (파일이 없을 경우만)
        writer.writerows(data)  # 데이터 추가

# JSON 데이터 분류 및 저장
def process_tiktok_data(json_file, append=False):
    data = load_json(json_file)
    video_id = os.path.basename(json_file).replace(".json", "")
    
    # 저장할 CSV 파일명
    videos_csv = "videos.csv"
    comments_csv = "comments.csv"
    replies_csv = "replies.csv"
    
    # 영상 데이터 저장
    videos_data = [[video_id, data["caption"], data["video_url"]]]
    videos_headers = ["video_id", "caption", "video_url"]
    save_to_csv(videos_csv, videos_data, videos_headers, append)
    
    # 댓글 및 대댓글 데이터 정리
    comments_data = []
    replies_data = []
    
    for comment in data["comments"]:
        comments_data.append([
            video_id, comment["comment_id"], comment["username"], comment["nickname"],
            comment["comment"], comment["create_time"], comment["avatar"], comment["total_reply"]
        ])
        
        # 대댓글 처리
        for reply in comment.get("replies", []):
            replies_data.append([
                video_id, comment["comment_id"], reply["comment_id"], reply["username"],
                reply["nickname"], reply["comment"], reply["create_time"], reply["avatar"]
            ])
    
    # CSV 저장 (파일이 존재하면 추가)
    comments_headers = ["video_id", "comment_id", "username", "nickname", "comment", "create_time", "avatar", "total_reply"]
    replies_headers = ["video_id", "parent_comment_id", "comment_id", "username", "nickname", "comment", "create_time", "avatar"]
    
    save_to_csv(comments_csv, comments_data, comments_headers, append)
    save_to_csv(replies_csv, replies_data, replies_headers, append)
    
    print(f"{json_file} 데이터 추가 완료!")

# 여러 JSON 파일 처리
def process_multiple_tiktok_files(json_files):
    first_file = True  # 첫 번째 파일인지 여부 확인
    for json_file in json_files:
        process_tiktok_data(json_file, append=not first_file)
        first_file = False

# 실행 예제
json_files = ["7424776996175088903.json", "7424897841175626517.json"]  # 예제 JSON 파일 리스트
process_multiple_tiktok_files(json_files)
