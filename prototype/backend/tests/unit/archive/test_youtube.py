"""
YouTube 수집기 단위 테스트

YouTube 데이터 수집 모듈에 대한 단위 테스트를 제공합니다.
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import json
from datetime import datetime

# 상위 디렉토리 추가하여 app 모듈 import 가능하게 함
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pipelines.youtube import YouTubeCollector
from app.services.collectors.youtube import collect_youtube_data, generate_request_id


class TestYouTubeCollector(unittest.TestCase):
    """YouTube 수집기 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.collector = YouTubeCollector(api_key="test_api_key")
        
    @patch('pipelines.youtube.build')
    def test_get_video_info(self, mock_build):
        """비디오 정보 가져오기 테스트"""
        # Mock YouTube API 응답 설정
        mock_videos_list = MagicMock()
        mock_videos = MagicMock()
        mock_videos.list.return_value = mock_videos_list
        mock_build.return_value = mock_videos
        
        # 샘플 응답 데이터
        mock_response = {
            "items": [{
                "id": "test_video_id",
                "snippet": {
                    "title": "테스트 비디오",
                    "description": "테스트 설명",
                    "publishedAt": "2023-01-01T00:00:00Z",
                    "channelTitle": "테스트 채널",
                    "thumbnails": {
                        "default": {"url": "http://example.com/thumbnail.jpg"}
                    }
                },
                "statistics": {
                    "viewCount": "1000",
                    "likeCount": "100",
                    "commentCount": "50"
                }
            }]
        }
        mock_videos_list.execute.return_value = mock_response
        
        # 테스트 실행
        result = self.collector.get_video_info("test_video_id")
        
        # 결과 검증
        self.assertEqual(result["title"], "테스트 비디오")
        self.assertEqual(result["channel_title"], "테스트 채널")
        self.assertEqual(result["view_count"], 1000)
        self.assertEqual(result["like_count"], 100)
        self.assertEqual(result["comment_count"], 50)
        
    @patch('pipelines.youtube.build')
    def test_get_video_comments(self, mock_build):
        """비디오 댓글 가져오기 테스트"""
        # Mock YouTube API 응답 설정
        mock_comments_list = MagicMock()
        mock_comments_thread = MagicMock()
        mock_comments_thread.list.return_value = mock_comments_list
        mock_build.return_value.commentThreads = mock_comments_thread
        
        # 샘플 응답 데이터
        mock_response = {
            "items": [{
                "id": "comment_id_1",
                "snippet": {
                    "topLevelComment": {
                        "id": "comment_id_1",
                        "snippet": {
                            "textOriginal": "테스트 댓글 1",
                            "authorDisplayName": "테스트 사용자 1",
                            "publishedAt": "2023-01-02T00:00:00Z",
                            "likeCount": 5
                        }
                    }
                }
            }],
            "nextPageToken": "token123"
        }
        mock_comments_list.execute.return_value = mock_response
        
        # 테스트 실행 (1페이지만 가져오도록 max_results=1 설정)
        result = self.collector.get_video_comments("test_video_id", max_results=1)
        
        # 결과 검증
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["text_original"], "테스트 댓글 1")
        self.assertEqual(result[0]["author"], "테스트 사용자 1")
        
    def test_clean_comments(self):
        """댓글 데이터 정제 테스트"""
        # 샘플 댓글 데이터
        comments = [
            {
                "id": "comment1",
                "text_original": "이것은 테스트 댓글입니다.",
                "author": "테스터",
                "published_at": "2023-01-01T00:00:00Z",
                "like_count": 5
            },
            {
                "id": "comment2",
                "text_original": "",  # 빈 댓글
                "author": "테스터2",
                "published_at": "2023-01-02T00:00:00Z",
                "like_count": 0
            }
        ]
        
        # 테스트 실행
        result = self.collector.clean_comments(comments)
        
        # 결과 검증
        self.assertEqual(len(result), 1)  # 빈 댓글은 제거됨
        self.assertEqual(result[0]["id"], "comment1")


class TestYouTubeService(unittest.TestCase):
    """YouTube 서비스 함수 테스트 클래스"""
    
    @patch('app.services.collectors.youtube.YouTubeCollector')
    async def test_collect_youtube_data(self, mock_collector_class):
        """YouTube 데이터 수집 서비스 테스트"""
        # Mock 설정
        mock_collector = MagicMock()
        mock_collector_class.return_value = mock_collector
        
        # 샘플 데이터 설정
        mock_collector.get_video_info.return_value = {
            "title": "테스트 비디오",
            "channel_title": "테스트 채널"
        }
        mock_collector.get_video_comments.return_value = [
            {"text_original": "테스트 댓글"}
        ]
        
        # 테스트 실행
        mock_db = MagicMock()
        result = await collect_youtube_data(
            video_ids=["test_video_id"],
            keywords=None,
            max_comments=10,
            db=mock_db
        )
        
        # 검증
        self.assertTrue(mock_collector.get_video_info.called)
        self.assertTrue(mock_collector.get_video_comments.called)
    
    def test_generate_request_id(self):
        """요청 ID 생성 테스트"""
        request_id = generate_request_id()
        self.assertIsNotNone(request_id)
        self.assertIsInstance(request_id, str)
        self.assertTrue(len(request_id) > 0)


if __name__ == '__main__':
    unittest.main() 