/**
 * 분석 데이터 API 서비스의 목업 데이터
 * 
 * 백엔드 API가 준비되지 않은 상태에서 테스트를 위한 가상 데이터
 */

// 분석 개요 데이터
export const mockOverviewData = {
  total_analyzed: 8526,
  sentiment_distribution: {
    positive: 0.67,
    neutral: 0.21,
    negative: 0.12
  },
  top_categories: [
    { category: '맛', count: 3245 },
    { category: '가격', count: 1842 },
    { category: '포장', count: 1156 },
    { category: '구매처', count: 875 },
    { category: '재구매', count: 723 }
  ],
  top_keywords: [
    { keyword: '맛있는', count: 423 },
    { keyword: '달콤한', count: 387 },
    { keyword: '부드러운', count: 321 },
    { keyword: '저렴한', count: 302 },
    { keyword: '편의점', count: 267 },
    { keyword: '가성비', count: 245 },
    { keyword: '재구매', count: 231 },
    { keyword: '디자인', count: 187 },
    { keyword: '포장', count: 176 },
    { keyword: '신제품', count: 154 },
    { keyword: '씁쓸한', count: 132 },
    { keyword: '비싼', count: 121 }
  ],
  recent_positive_keywords: [
    '맛있는', '달콤한', '부드러운', '고소한', '신선한',
    '촉촉한', '풍부한', '매력적인', '저렴한', '가성비'
  ],
  recent_negative_keywords: [
    '비싼', '단맛이 강한', '딱딱한', '너무 달콤한', '싱겁다',
    '실망스러운', '작은 크기', '맛이 나지 않는', '인공적인', '포장 불편'
  ]
};

// 감성 분석 트렌드 데이터
export const mockSentimentTrendsData = [
  { date: '2025-03-01', positive: 65, neutral: 23, negative: 12 },
  { date: '2025-03-02', positive: 68, neutral: 21, negative: 11 },
  { date: '2025-03-03', positive: 64, neutral: 22, negative: 14 },
  { date: '2025-03-04', positive: 62, neutral: 24, negative: 14 },
  { date: '2025-03-05', positive: 70, neutral: 19, negative: 11 },
  { date: '2025-03-06', positive: 73, neutral: 18, negative: 9 },
  { date: '2025-03-07', positive: 75, neutral: 17, negative: 8 },
  { date: '2025-03-08', positive: 69, neutral: 20, negative: 11 },
  { date: '2025-03-09', positive: 67, neutral: 22, negative: 11 },
  { date: '2025-03-10', positive: 69, neutral: 20, negative: 11 },
  { date: '2025-03-11', positive: 72, neutral: 18, negative: 10 },
  { date: '2025-03-12', positive: 70, neutral: 19, negative: 11 },
  { date: '2025-03-13', positive: 68, neutral: 21, negative: 11 },
  { date: '2025-03-14', positive: 66, neutral: 22, negative: 12 },
  { date: '2025-03-15', positive: 69, neutral: 20, negative: 11 },
  { date: '2025-03-16', positive: 71, neutral: 19, negative: 10 },
  { date: '2025-03-17', positive: 74, neutral: 17, negative: 9 },
  { date: '2025-03-18', positive: 76, neutral: 15, negative: 9 },
  { date: '2025-03-19', positive: 73, neutral: 18, negative: 9 },
  { date: '2025-03-20', positive: 71, neutral: 19, negative: 10 }
];

// 키워드 트렌드 데이터
export const mockKeywordTrendsData = {
  dates: ['2025-03-01', '2025-03-05', '2025-03-10', '2025-03-15', '2025-03-20'],
  categories: {
    taste: [
      { keyword: '달콤한', values: [42, 45, 48, 52, 56] },
      { keyword: '고소한', values: [35, 38, 40, 37, 39] },
      { keyword: '부드러운', values: [30, 32, 35, 38, 42] },
      { keyword: '촉촉한', values: [28, 30, 32, 34, 36] },
      { keyword: '진한', values: [25, 27, 29, 28, 30] }
    ],
    price: [
      { keyword: '저렴한', values: [38, 40, 42, 45, 48] },
      { keyword: '가성비', values: [32, 35, 38, 40, 43] },
      { keyword: '할인', values: [28, 30, 32, 34, 36] },
      { keyword: '가격대비', values: [25, 27, 28, 30, 32] },
      { keyword: '비싼', values: [18, 16, 15, 14, 13] }
    ]
  }
};

// 감성 분석 상세 데이터
export const mockSentimentAnalysisData = [
  {
    id: 1,
    text: '이 디저트는 정말 달콤하고 부드러워요. 가격도 저렴해서 자주 구매합니다.',
    sentiment: 'positive',
    confidence: 0.92,
    created_at: '2025-03-19T14:28:32.451Z',
    source: 'youtube_comment',
    keywords: ['달콤한', '부드러운', '저렴한']
  },
  {
    id: 2,
    text: '맛은 괜찮은데 가격이 조금 비싼 것 같아요. 포장은 예쁘게 되어있어서 선물하기 좋아요.',
    sentiment: 'neutral',
    confidence: 0.78,
    created_at: '2025-03-18T09:15:42.123Z',
    source: 'youtube_comment',
    keywords: ['괜찮은', '비싼', '포장', '예쁜', '선물']
  },
  {
    id: 3,
    text: '너무 달아서 한 개 먹기도 힘들었어요. 포장을 뜯기도 어려워요.',
    sentiment: 'negative',
    confidence: 0.85,
    created_at: '2025-03-17T18:42:15.789Z',
    source: 'youtube_comment',
    keywords: ['너무 달은', '먹기 힘든', '포장', '뜯기 어려운']
  }
];

// 키워드 추출 상세 데이터
export const mockKeywordExtractionsData = [
  {
    id: 1,
    text_id: 101,
    keyword: '달콤한',
    category: 'taste',
    count: 5,
    sentiment: 'positive',
    created_at: '2025-03-19T14:28:32.451Z'
  },
  {
    id: 2,
    text_id: 101,
    keyword: '부드러운',
    category: 'taste',
    count: 3,
    sentiment: 'positive',
    created_at: '2025-03-19T14:28:32.451Z'
  },
  {
    id: 3,
    text_id: 102,
    keyword: '저렴한',
    category: 'price',
    count: 4,
    sentiment: 'positive',
    created_at: '2025-03-18T09:15:42.123Z'
  },
  {
    id: 4,
    text_id: 102,
    keyword: '편의점',
    category: 'place',
    count: 2,
    sentiment: 'neutral',
    created_at: '2025-03-18T09:15:42.123Z'
  },
  {
    id: 5,
    text_id: 103,
    keyword: '포장 불편',
    category: 'packaging',
    count: 3,
    sentiment: 'negative',
    created_at: '2025-03-17T18:42:15.789Z'
  }
];

// 시계열 차트용 감성 분석 데이터
export const mockTimeSeriesData = {
  hourly: Array(24).fill(0).map((_, i) => ({
    timestamp: `2025-03-20T${String(i).padStart(2, '0')}:00:00Z`,
    positive: Math.floor(Math.random() * 30) + 50,
    neutral: Math.floor(Math.random() * 15) + 15,
    negative: Math.floor(Math.random() * 10) + 5
  })),
  daily: Array(30).fill(0).map((_, i) => {
    const date = new Date(2025, 2, i + 1);
    return {
      timestamp: date.toISOString().split('T')[0],
      positive: Math.floor(Math.random() * 20) + 60,
      neutral: Math.floor(Math.random() * 10) + 10,
      negative: Math.floor(Math.random() * 10) + 5
    };
  })
}; 