/**
 * 분석 데이터 API 서비스
 * 
 * 백엔드 API를 호출하여 감성 분석 및 키워드 추출 결과를 가져오는 서비스 모듈
 */

import axios from 'axios';
import { 
  mockOverviewData, 
  mockSentimentTrendsData, 
  mockKeywordTrendsData,
  mockSentimentAnalysisData,
  mockKeywordExtractionsData,
  mockTimeSeriesData
} from './mockData';

// API 기본 URL 설정
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// 목업 데이터 사용 여부
const USE_MOCK_DATA = false;

// 날짜를 ISO 문자열로 변환하는 유틸리티 함수
const formatDateParam = (date) => {
  if (!date) return undefined;
  return date instanceof Date ? date.toISOString() : date;
};

/**
 * 분석 서비스 클래스
 */
class AnalysisService {
  /**
   * 대시보드 요약 정보 조회
   * 
   * @returns {Promise<Object>} 대시보드 요약 정보 객체
   */
  async getAnalysisOverview() {
    if (USE_MOCK_DATA) {
      return Promise.resolve(mockOverviewData);
    }
    
    try {
      const response = await axios.get(`${API_URL}/dashboard/summary`);
      
      // API 응답 구조를 프론트엔드 구조에 맞게 변환
      const data = response.data;
      return {
        total_analyzed: data.totalComments,
        average_sentiment: data.averageSentiment,
        sentiment_distribution: data.sentimentDistribution,
        recent_positive_keywords: [], // 이 데이터는 keywords API에서 별도로 가져와야 함
        recent_negative_keywords: [], // 이 데이터는 keywords API에서 별도로 가져와야 함
        top_categories: [], // 이 데이터는 top-channels API를 활용하여 변환해야 함
        top_keywords: [], // 이 데이터는 keywords API에서 별도로 가져와야 함
        recent_items: data.recentVideos,
        last_updated: data.lastUpdated
      };
    } catch (error) {
      console.error('Error fetching dashboard summary:', error);
      throw error;
    }
  }

  /**
   * 감성 분석 결과 조회
   * 
   * @param {Object} params - 조회 파라미터
   * @param {Date|string} [params.startDate] - 시작 날짜
   * @param {Date|string} [params.endDate] - 종료 날짜
   * @param {string} [params.category] - 제품 카테고리
   * @param {string} [params.sentiment] - 감성 분류 (positive, neutral, negative)
   * @param {number} [params.limit=100] - 결과 제한 수
   * @param {number} [params.offset=0] - 결과 오프셋
   * @returns {Promise<Array>} 감성 분석 결과 배열
   */
  async getSentimentAnalysis(params = {}) {
    if (USE_MOCK_DATA) {
      // 목업 데이터 필터링
      let filtered = [...mockSentimentAnalysisData];
      
      if (params.sentiment) {
        filtered = filtered.filter(item => item.sentiment === params.sentiment);
      }
      
      // 정렬 및 페이징
      const start = params.offset || 0;
      const end = start + (params.limit || 100);
      
      return Promise.resolve(filtered.slice(start, end));
    }
    
    try {
      const { startDate, endDate, sentiment, limit = 100, offset = 0 } = params;
      
      // videoId가 있으면 특정 비디오의 댓글을 가져옴
      if (params.videoId) {
        const response = await axios.get(`${API_URL}/dashboard/videos/${params.videoId}/comments`, {
          params: {
            sentiment,
            limit,
            skip: offset
          }
        });
        
        return response.data.items;
      }
      
      // 비디오 없이 전체 감성 분석 결과 가져옴 (현재 API에서는 지원하지 않음)
      // 대안으로 비디오 목록을 가져와서 감성 분석 결과 포함하도록 함
      const response = await axios.get(`${API_URL}/dashboard/videos`, {
        params: {
          start_date: formatDateParam(startDate),
          end_date: formatDateParam(endDate),
          limit,
          skip: offset
        }
      });
      
      // 비디오 목록에서 감성 분석 결과 추출
      return response.data.items.map(video => ({
        id: video.id,
        title: video.title,
        channel: video.channelTitle,
        date: video.publishedAt,
        sentiment: video.sentimentAnalysis ? 
          (video.sentimentAnalysis.averageScore > 0.05 ? 'positive' : 
           video.sentimentAnalysis.averageScore < -0.05 ? 'negative' : 'neutral') 
          : 'neutral',
        sentiment_score: video.sentimentAnalysis ? video.sentimentAnalysis.averageScore : 0,
        positive_percentage: video.sentimentAnalysis ? video.sentimentAnalysis.positivePercentage : 0,
        negative_percentage: video.sentimentAnalysis ? video.sentimentAnalysis.negativePercentage : 0,
        neutral_percentage: video.sentimentAnalysis ? video.sentimentAnalysis.neutralPercentage : 0
      }));
    } catch (error) {
      console.error('Error fetching sentiment analysis:', error);
      throw error;
    }
  }

  /**
   * 감성 분석 트렌드 조회
   * 
   * @param {Object} params - 조회 파라미터
   * @param {number} [params.days=30] - 몇 일 동안의 데이터를 가져올지 지정
   * @returns {Promise<Array>} 감성 분석 트렌드 데이터 배열
   */
  async getSentimentTrends(params = {}) {
    if (USE_MOCK_DATA) {
      return Promise.resolve(mockSentimentTrendsData);
    }
    
    try {
      const { days = 30 } = params;
      
      const response = await axios.get(`${API_URL}/dashboard/sentiment/trends`, {
        params: {
          days
        }
      });
      
      return response.data.trends;
    } catch (error) {
      console.error('Error fetching sentiment trends:', error);
      throw error;
    }
  }

  /**
   * 감성 분석 집계 데이터 조회
   * 
   * @param {Object} params - 조회 파라미터
   * @param {string} [params.period='day'] - 집계 기간 (hour, day, week, month)
   * @param {Date|string} [params.startDate] - 시작 날짜
   * @param {Date|string} [params.endDate] - 종료 날짜
   * @param {string} [params.category] - 제품 카테고리
   * @returns {Promise<Array>} 감성 분석 집계 데이터 배열
   */
  async getSentimentAggregate(params = {}) {
    if (USE_MOCK_DATA) {
      const { period = 'day' } = params;
      
      // period에 따라 다른 목업 데이터 반환
      if (period === 'hour') {
        return Promise.resolve(mockTimeSeriesData.hourly);
      }
      
      return Promise.resolve(mockTimeSeriesData.daily);
    }
    
    try {
      // 현재 백엔드 API에서는 세부 기간별 집계가 아직 구현되지 않음
      // 대안으로 감성 트렌드 API를 사용
      const { days = 30 } = params;
      
      const response = await axios.get(`${API_URL}/dashboard/sentiment/trends`, {
        params: {
          days
        }
      });
      
      return response.data.trends;
    } catch (error) {
      console.error('Error fetching sentiment aggregate:', error);
      throw error;
    }
  }

  /**
   * 상위 채널 목록 조회
   * 
   * @param {Object} params - 조회 파라미터
   * @param {number} [params.limit=10] - 결과 제한 수
   * @param {number} [params.days=30] - 몇 일 동안의 데이터를 가져올지 지정
   * @returns {Promise<Array>} 상위 채널 목록
   */
  async getTopChannels(params = {}) {
    if (USE_MOCK_DATA) {
      return Promise.resolve(mockKeywordTrendsData.topChannels || []);
    }
    
    try {
      const { limit = 10, days = 30 } = params;
      
      const response = await axios.get(`${API_URL}/dashboard/top-channels`, {
        params: {
          limit,
          days
        }
      });
      
      return response.data.channels;
    } catch (error) {
      console.error('Error fetching top channels:', error);
      throw error;
    }
  }

  /**
   * 키워드 추출 결과 조회
   * 
   * @param {Object} params - 조회 파라미터
   * @param {number} [params.days=30] - 몇 일 동안의 데이터를 가져올지 지정
   * @param {string} [params.sentiment] - 감성 필터 (positive, negative, neutral)
   * @param {number} [params.limit=20] - 결과 제한 수
   * @returns {Promise<Array>} 키워드 추출 결과 배열
   */
  async getKeywordExtractions(params = {}) {
    if (USE_MOCK_DATA) {
      // 목업 데이터 필터링
      let filtered = [...mockKeywordExtractionsData];
      
      if (params.sentiment) {
        filtered = filtered.filter(item => item.sentiment === params.sentiment);
      }
      
      // 정렬 및 페이징
      const start = 0;
      const end = params.limit || 20;
      
      return Promise.resolve(filtered.slice(start, end));
    }
    
    try {
      const { days = 30, sentiment, limit = 20 } = params;
      
      const response = await axios.get(`${API_URL}/dashboard/keywords`, {
        params: {
          days,
          sentiment,
          limit
        }
      });
      
      return response.data.keywords;
    } catch (error) {
      console.error('Error fetching keyword extractions:', error);
      throw error;
    }
  }

  /**
   * 비디오 목록 조회
   * 
   * @param {Object} params - 조회 파라미터
   * @param {string} [params.keyword] - 검색 키워드
   * @param {Date|string} [params.startDate] - 시작 날짜
   * @param {Date|string} [params.endDate] - 종료 날짜
   * @param {number} [params.limit=10] - 결과 제한 수
   * @param {number} [params.offset=0] - 결과 오프셋
   * @returns {Promise<Object>} 비디오 목록 및 메타데이터
   */
  async getVideos(params = {}) {
    if (USE_MOCK_DATA) {
      // 가상의 비디오 목록 데이터
      return Promise.resolve({
        items: mockSentimentAnalysisData.slice(0, params.limit || 10),
        total: mockSentimentAnalysisData.length,
        page: 1,
        pages: Math.ceil(mockSentimentAnalysisData.length / (params.limit || 10)),
        limit: params.limit || 10
      });
    }
    
    try {
      const { keyword, startDate, endDate, limit = 10, offset = 0 } = params;
      
      const response = await axios.get(`${API_URL}/dashboard/videos`, {
        params: {
          keyword,
          start_date: formatDateParam(startDate),
          end_date: formatDateParam(endDate),
          limit,
          skip: offset
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching videos:', error);
      throw error;
    }
  }

  /**
   * 특정 비디오의 댓글 목록 조회
   * 
   * @param {Object} params - 조회 파라미터
   * @param {string} params.videoId - 비디오 ID
   * @param {string} [params.sentiment] - 감성 필터 (positive, negative, neutral)
   * @param {number} [params.limit=50] - 결과 제한 수
   * @param {number} [params.offset=0] - 결과 오프셋
   * @returns {Promise<Object>} 댓글 목록 및 메타데이터
   */
  async getVideoComments(params = {}) {
    if (USE_MOCK_DATA) {
      // 가상의 댓글 데이터
      return Promise.resolve({
        items: mockKeywordExtractionsData.slice(0, params.limit || 50),
        total: mockKeywordExtractionsData.length,
        page: 1,
        pages: Math.ceil(mockKeywordExtractionsData.length / (params.limit || 50)),
        limit: params.limit || 50
      });
    }
    
    try {
      const { videoId, sentiment, limit = 50, offset = 0 } = params;
      
      if (!videoId) {
        throw new Error('Video ID is required');
      }
      
      const response = await axios.get(`${API_URL}/dashboard/videos/${videoId}/comments`, {
        params: {
          sentiment,
          limit,
          skip: offset
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching video comments:', error);
      throw error;
    }
  }
}

export default new AnalysisService(); 