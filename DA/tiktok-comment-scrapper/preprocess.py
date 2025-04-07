import pandas as pd
import re

# --- 전처리 조건 함수 정의 ---

def is_meaningful(content):
    content = str(content).strip()
    if len(content) <= 2:
        return False
    if not re.search(r'[가-힣]', content):
        return False
    if not re.search(r'[가-힣a-zA-Z0-9]', content):
        return False
    return True

def is_not_recipe_related(content):
    content = str(content).lower()
    return not ('레시피' in content or '만들기' in content)

# --- 1. 영상 정보 불러오기 ---
video_df = pd.read_csv('data/tiktok_video_ids_with_titles.csv')  # 열: video_id, url, title

# --- 2. 레시피/만들기 관련 영상 제외 ---
filtered_video_ids = video_df[video_df['title'].apply(is_not_recipe_related)]['video_id'].unique()

# --- 3. 댓글 데이터 불러오기 ---
comments_df = pd.read_csv('data/all_comments.csv')  # 열: video_id, comment_id, username, ...

# --- 4. 조건에 해당하는 video_id만 필터링 (조인과 유사) ---
filtered_comments_df = comments_df[comments_df['video_id'].isin(filtered_video_ids)].copy()

# --- 5. 전처리 (is_meaningful) ---
filtered_comments_df['is_valid'] = filtered_comments_df['comment'].apply(is_meaningful)
clean_df = filtered_comments_df[filtered_comments_df['is_valid']].drop(columns=['is_valid'])

# --- 6. 저장 ---
clean_df.to_csv('data/clean_comments.csv', index=False, encoding='utf-8-sig')

print(f"최종 전처리 완료! {len(clean_df)}개의 댓글이 clean_comments.csv에 저장되었습니다.")
