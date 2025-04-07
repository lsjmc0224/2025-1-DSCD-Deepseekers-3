import os
import csv
import click
from loguru import logger
from tiktokcomment import TiktokComment
from tiktokcomment.typing import Comments, Comment
from datetime import datetime

__title__ = 'TikTok Comment Scraper (All-in-One CSV with Replies)'
__version__ = '2.1.0'

@click.command(help=__title__)
@click.version_option(version=__version__, prog_name=__title__)
@click.option(
    "--input_csv",
    help='CSV file containing video IDs',
    default='data/tiktok_video_ids_with_titles.csv'
)
@click.option(
    "--output_file",
    help='Path to output CSV file',
    default='data/all_comments.csv'
)
def main(input_csv: str, output_file: str):
    # 비디오 ID 읽기
    video_ids = []
    with open(input_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header
        for row in reader:
            video_ids.append(row[0])

    if not video_ids:
        raise ValueError('No video IDs found.')

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow([
            'video_id',
            'comment_id',
            'username',
            'nickname',
            'comment',
            'create_time',
            'is_reply',
            'parent_comment_id',
            'total_reply'
        ])


        scraper = TiktokComment()

        for video_id in video_ids:
            logger.info(f"📥 Scraping comments for video: {video_id}")
            try:
                comments_obj: Comments = scraper(aweme_id=video_id)

                def write_comment_row(comment: Comment, is_reply: bool, parent_comment_id: str = ''):
                    writer.writerow([
                        video_id,
                        comment.comment_id,
                        comment.username,
                        comment.nickname,
                        comment.comment,
                        format_time(comment.create_time),
                        is_reply,
                        parent_comment_id,
                        comment.total_reply
                    ])

                for comment in comments_obj.comments:
                    write_comment_row(comment, is_reply=False)

                    # Replies까지 포함해서 저장
                    for reply in comment.replies:
                        write_comment_row(reply, is_reply=True, parent_comment_id=comment.comment_id)

                logger.success(f"✅ {video_id} 완료, 댓글 수: {len(comments_obj.comments)}")
            except Exception as e:
                logger.error(f"❌ {video_id} 실패: {e}")


def format_time(ts) -> str:
    """timestamp(int or str) 또는 ISO8601 문자열 처리"""
    try:
        if isinstance(ts, (int, float)) or (isinstance(ts, str) and ts.isdigit()):
            # 정수 또는 정수형 문자열이면 timestamp로 처리
            return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(ts, str) and 'T' in ts:
            # ISO 8601 문자열이면 처리
            return datetime.fromisoformat(ts).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        logger.warning(f"⚠️ 타임스탬프 변환 실패 ({ts}): {e}")
        return ''




if __name__ == "__main__":
    main()
