import React, { useState } from 'react';
import SentimentHeatmap from './SentimentHeatmap';

// 히트맵 컴포넌트 스타일링
const styles = {
  container: {
    padding: '20px',
    maxWidth: '1200px',
    margin: '0 auto',
    fontFamily: 'Noto Sans KR, Roboto, sans-serif'
  },
  header: {
    marginBottom: '20px',
    borderBottom: '1px solid #e2e8f0',
    paddingBottom: '10px'
  },
  title: {
    fontSize: '1.8rem',
    fontWeight: 600,
    color: '#1a365d',
    marginBottom: '10px'
  },
  description: {
    fontSize: '1rem',
    color: '#4a5568',
    marginBottom: '20px'
  },
  controls: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '15px',
    marginBottom: '20px',
    padding: '15px',
    backgroundColor: '#f8fafc',
    borderRadius: '8px'
  },
  controlGroup: {
    display: 'flex',
    flexDirection: 'column',
    minWidth: '200px'
  },
  label: {
    fontSize: '0.9rem',
    fontWeight: 500,
    marginBottom: '5px',
    color: '#4a5568'
  },
  select: {
    padding: '8px 10px',
    borderRadius: '5px',
    border: '1px solid #e2e8f0',
    backgroundColor: 'white',
    fontSize: '0.9rem'
  },
  input: {
    padding: '8px 10px',
    borderRadius: '5px',
    border: '1px solid #e2e8f0',
    fontSize: '0.9rem'
  },
  chart: {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '20px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
  }
};

/**
 * 감성 분석 히트맵 데모 컴포넌트
 * 
 * SentimentHeatmap 컴포넌트의 사용 예시를 보여주는 데모 페이지입니다.
 * 주요 설정을 변경할 수 있는 컨트롤을 제공합니다.
 */
const SentimentHeatmapDemo = () => {
  // 현재 날짜와 3개월 전 날짜 계산
  const now = new Date();
  const threeMonthsAgo = new Date(now);
  threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);
  
  // 상태 관리
  const [period, setPeriod] = useState('day');
  const [sentiment, setSentiment] = useState('positive');
  const [startDate, setStartDate] = useState(threeMonthsAgo.toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState(now.toISOString().split('T')[0]);
  const [selectedCategories, setSelectedCategories] = useState([
    'taste', 'price', 'packaging', 'place', 'repurchase'
  ]);

  // 카테고리 토글 처리
  const handleCategoryToggle = (category) => {
    if (selectedCategories.includes(category)) {
      setSelectedCategories(selectedCategories.filter(cat => cat !== category));
    } else {
      setSelectedCategories([...selectedCategories, category]);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>감성 분석 히트맵</h1>
        <p style={styles.description}>
          카테고리별, 시간별 감성 변화를 히트맵으로 시각화합니다. 
          아래 설정을 변경하여 다양한 관점에서 데이터를 확인해보세요.
        </p>
      </div>

      <div style={styles.controls}>
        <div style={styles.controlGroup}>
          <label style={styles.label}>기간 단위</label>
          <select 
            style={styles.select}
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
          >
            <option value="hour">시간별</option>
            <option value="day">일별</option>
            <option value="week">주별</option>
            <option value="month">월별</option>
          </select>
        </div>

        <div style={styles.controlGroup}>
          <label style={styles.label}>감성 선택</label>
          <select 
            style={styles.select}
            value={sentiment}
            onChange={(e) => setSentiment(e.target.value)}
          >
            <option value="positive">긍정</option>
            <option value="neutral">중립</option>
            <option value="negative">부정</option>
          </select>
        </div>

        <div style={styles.controlGroup}>
          <label style={styles.label}>시작 날짜</label>
          <input 
            type="date" 
            style={styles.input}
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </div>

        <div style={styles.controlGroup}>
          <label style={styles.label}>종료 날짜</label>
          <input 
            type="date" 
            style={styles.input}
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>
      </div>

      <div style={styles.categorySelection}>
        <label style={styles.label}>카테고리 선택:</label>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '20px' }}>
          {['taste', 'price', 'packaging', 'place', 'repurchase'].map(category => (
            <label key={category} style={{ 
              display: 'flex', 
              alignItems: 'center',
              backgroundColor: selectedCategories.includes(category) ? '#e6fffa' : '#f8fafc',
              padding: '5px 10px',
              borderRadius: '5px',
              border: '1px solid #e2e8f0',
              cursor: 'pointer'
            }}>
              <input
                type="checkbox"
                checked={selectedCategories.includes(category)}
                onChange={() => handleCategoryToggle(category)}
                style={{ marginRight: '5px' }}
              />
              {getCategoryLabel(category)}
            </label>
          ))}
        </div>
      </div>

      <div style={styles.chart}>
        <SentimentHeatmap
          startDate={startDate}
          endDate={endDate}
          period={period}
          categories={selectedCategories}
          sentiment={sentiment}
          height={500}
        />
      </div>
    </div>
  );
};

// 카테고리 라벨 반환
const getCategoryLabel = (category) => {
  switch (category) {
    case 'taste': return '맛';
    case 'price': return '가격';
    case 'packaging': return '포장';
    case 'place': return '구매처';
    case 'repurchase': return '재구매 의향';
    default: return category;
  }
};

export default SentimentHeatmapDemo; 