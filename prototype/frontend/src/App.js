import React, { useState, useEffect } from 'react';
import './App.css';
import analysisService from './services/analysisService';
import DashboardLayout from './components/dashboard/DashboardLayout';
import SentimentHeatmapDemo from './components/charts/SentimentHeatmapDemo';
import SentimentTrendChartDemo from './components/charts/SentimentTrendChartDemo';
import InsightCardDemo from './components/dashboard/InsightCardDemo';

function App() {
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState(null);
  const [error, setError] = useState(null);
  const [activeView, setActiveView] = useState('overview'); // 'overview', 'heatmap', 'trend'
  const [currentView, setCurrentView] = useState('default');
  const [videos, setVideos] = useState([]);
  const [topKeywords, setTopKeywords] = useState([]);
  const [topChannels, setTopChannels] = useState([]);

  useEffect(() => {
    // 분석 개요 데이터 로드
    async function loadDashboardData() {
      try {
        setLoading(true);
        
        // 대시보드 요약 정보 로드
        const overviewData = await analysisService.getAnalysisOverview();
        
        // 동영상 목록 로드
        const videosData = await analysisService.getVideos({ limit: 5 });
        
        // 키워드 목록 로드
        const keywordsData = await analysisService.getKeywordExtractions({ limit: 20 });
        
        // 상위 채널 목록 로드
        const channelsData = await analysisService.getTopChannels({ limit: 5 });
        
        // 상태 업데이트
        setOverview(overviewData);
        setVideos(videosData.items || []);
        setTopKeywords(keywordsData || []);
        setTopChannels(channelsData || []);
        setError(null);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
        setError('데이터를 불러오는 중 오류가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    }

    loadDashboardData();
  }, []);

  // 대시보드 콘텐츠 렌더링
  const renderDashboardContent = () => {
    if (loading) {
      return <div className="loading">데이터 로딩 중...</div>;
    }
    
    if (error) {
      return <div className="error">{error}</div>;
    }

    if (activeView === 'heatmap') {
      return <SentimentHeatmapDemo />;
    }
    
    if (activeView === 'trend') {
      return <SentimentTrendChartDemo />;
    }

    return (
      <>
        {overview && (
          <div className="overview-container">
            <h2>분석 개요</h2>
            
            <div className="stats-container">
              <div className="stat-box">
                <h3>전체 분석 항목</h3>
                <div className="stat-value">{overview.total_analyzed}</div>
              </div>
              
              <div className="stat-box">
                <h3>감성 분포</h3>
                <div className="sentiment-distribution">
                  <div 
                    className="sentiment-bar positive" 
                    style={{ width: `${(overview.sentiment_distribution.positive || 0) * 100}%` }}
                  >
                    {Math.round((overview.sentiment_distribution.positive || 0) * 100)}%
                  </div>
                  <div 
                    className="sentiment-bar neutral" 
                    style={{ width: `${(overview.sentiment_distribution.neutral || 0) * 100}%` }}
                  >
                    {Math.round((overview.sentiment_distribution.neutral || 0) * 100)}%
                  </div>
                  <div 
                    className="sentiment-bar negative" 
                    style={{ width: `${(overview.sentiment_distribution.negative || 0) * 100}%` }}
                  >
                    {Math.round((overview.sentiment_distribution.negative || 0) * 100)}%
                  </div>
                </div>
                <div className="sentiment-legend">
                  <span className="positive-legend">긍정</span>
                  <span className="neutral-legend">중립</span>
                  <span className="negative-legend">부정</span>
                </div>
              </div>
            </div>
            
            <div className="categories-keywords">
              <div className="top-categories">
                <h3>상위 채널</h3>
                <ul>
                  {topChannels.map((channel, index) => (
                    <li key={index}>
                      <span className="category-name">{channel.channelTitle}</span>
                      <span className="category-count">{channel.commentCount}</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="top-keywords">
                <h3>상위 키워드</h3>
                <div className="keyword-tags">
                  {topKeywords.slice(0, 10).map((keyword, index) => (
                    <span 
                      key={index} 
                      className="keyword-tag"
                      style={{ 
                        fontSize: `${Math.max(0.8, Math.min(1.5, 0.8 + keyword.count / 50))}em` 
                      }}
                    >
                      {keyword.keyword}
                    </span>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="recent-videos">
              <h3>최근 수집된 동영상</h3>
              <ul className="video-list">
                {videos.map((video, index) => (
                  <li key={index} className="video-item">
                    <div className="video-thumbnail">
                      {video.thumbnailUrl && (
                        <img src={video.thumbnailUrl} alt={video.title} />
                      )}
                    </div>
                    <div className="video-info">
                      <h4>{video.title}</h4>
                      <div className="video-meta">
                        <span className="channel-name">{video.channelTitle}</span>
                        <span className="view-count">조회수 {video.viewCount}</span>
                        <span className="comment-count">댓글 {video.commentCount}</span>
                      </div>
                      {video.sentimentAnalysis && (
                        <div className="video-sentiment">
                          <div className="sentiment-mini-chart">
                            <div 
                              className="positive-bar" 
                              style={{ width: `${video.sentimentAnalysis.positivePercentage}%` }}
                            ></div>
                            <div 
                              className="neutral-bar" 
                              style={{ width: `${video.sentimentAnalysis.neutralPercentage}%` }}
                            ></div>
                            <div 
                              className="negative-bar" 
                              style={{ width: `${video.sentimentAnalysis.negativePercentage}%` }}
                            ></div>
                          </div>
                          <span className="sentiment-score">
                            평균 감성 점수: {video.sentimentAnalysis.averageScore.toFixed(2)}
                          </span>
                        </div>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
        
        <div className="action-buttons">
          <button 
            className="action-button"
            onClick={() => setActiveView('heatmap')}
          >
            감성 분석 히트맵 보기
          </button>
          <button 
            className="action-button"
            onClick={() => setActiveView('trend')}
          >
            감성 트렌드 차트 보기
          </button>
          <button 
            className="action-button"
            onClick={() => alert('키워드 분석 상세 페이지로 이동')}
          >
            키워드 분석 상세보기
          </button>
        </div>
      </>
    );
  };

  return (
    <DashboardLayout>
      <div className="view-buttons">
        <button 
          onClick={() => setCurrentView('default')} 
          className={currentView === 'default' ? 'active' : ''}
        >
          기본 대시보드
        </button>
        <button 
          onClick={() => setCurrentView('sentimentTrend')} 
          className={currentView === 'sentimentTrend' ? 'active' : ''}
        >
          감성 트렌드 차트
        </button>
        <button 
          onClick={() => setCurrentView('insights')} 
          className={currentView === 'insights' ? 'active' : ''}
        >
          인사이트 카드 보기
        </button>
      </div>
      <main>
        {currentView === 'default' && renderDashboardContent()}
        {currentView === 'sentimentTrend' && <SentimentTrendChartDemo />}
        {currentView === 'insights' && <InsightCardDemo />}
      </main>
    </DashboardLayout>
  );
}

export default App; 