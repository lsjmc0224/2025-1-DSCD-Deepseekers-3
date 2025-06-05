
import React, { useState, useRef, useEffect } from 'react';
import VideosGrid from '../VideosGrid';

interface DateRange {
  from: Date;
  to?: Date;
}

interface VideosTabProps {
  channel: string;
  period: string;
  dateRange: DateRange;
}

// 간식 이모지 배열
const snackEmojis = ['🍫', '🍪', '🍭', '🍩', '🍰', '🥐', '🍦', '🌮', '🥤', '🥡', '🍙', '🍕', '🥨', '🥪', '🍿'];

// 편의점 간식 관련 제목 생성 배열
const snackTitles = [
  '이 과자 맛있나요? 편의점 신상 3종 리뷰!',
  '편의점 라면 BEST 5 순위 발표합니다',
  '편의점 디저트 신상품 언박싱',
  '400원으로 살 수 있는 간식은?',
  '편의점 과자 1만원어치 먹방',
  '편의점 아이스크림 추천 TOP 10',
  '주머니 가벼운 날 추천! 천원대 간식',
  '편의점 샌드위치 전메뉴 리뷰',
  '편의점 냉동식품 추천',
  '편의점 음료수 신상 맛 비교',
  '과자 투어 브이로그',
  '편의점 도시락 신상품 리뷰',
  '편의점 디저트 간식 추천',
  '편의점 저칼로리 간식 추천',
  '가성비 최고 편의점 과자 추천',
];

const snackShortsTitles = [
  '[쇼츠] 이 과자 최고임 ㄹㅇ',
  '[쇼츠] 편의점 베스트 간식 찾았다',
  '[쇼츠] 신상 아이스크림 먹방',
  '[쇼츠] 이거 먹어봄?',
  '[쇼츠] 편의점 삼각김밥 전종류 먹어봄',
  '[쇼츠] 500원으로 살 수 있는 최고 과자',
  '[쇼츠] 편의점 도넛 맛 비교',
  '[쇼츠] 이 과자 먹어봄? 대박 맛남',
  '[쇼츠] 신상 과자 먹방',
  '[쇼츠] 편의점 음료 꿀조합',
  '[쇼츠] 500원 과자 리뷰',
  '[쇼츠] 밤에 먹기 좋은 간식',
  '[쇼츠] 편의점 핫도그 가성비 최고',
  '[쇼츠] 이 과자 아는 사람?',
  '[쇼츠] 간식 ASMR',
];

// 목업 비디오 데이터 생성 함수
const generateMockVideos = (count: number, isShorts = false, startDate: Date, endDate: Date) => {
  return Array.from({ length: count }, (_, i) => {
    const id = isShorts ? `short-${i + 1}` : `video-${i + 1}`;
    
    // Generate random date within the date range
    const dateRange = endDate.getTime() - startDate.getTime();
    const randomTime = Math.random() * dateRange;
    const publishDate = new Date(startDate.getTime() + randomTime);
    
    const positive = Math.floor(Math.random() * 80) + 20;
    const negative = Math.floor(Math.random() * 40);
    const neutral = 100 - positive - negative;
    
    const views = isShorts 
      ? Math.floor(Math.random() * 900000) + 100000
      : Math.floor(Math.random() * 100000) + 10000;

    // 랜덤 이모지 선택
    const randomEmoji = snackEmojis[Math.floor(Math.random() * snackEmojis.length)];
    
    // 제목 선택 (쇼츠 또는 일반 비디오)
    const titles = isShorts ? snackShortsTitles : snackTitles;
    const title = titles[Math.floor(Math.random() * titles.length)];
    
    // 썸네일 URL - 더미 이미지에서 이모지 배경 이미지로 개선
    const thumbnailUrl = Math.random() > 0.3 
      ? `https://source.unsplash.com/320x180/?snack,food,${id}` 
      : `https://via.placeholder.com/320x180/FFCC99/333333?text=${randomEmoji}`;
    
    return {
      id,
      title,
      thumbnailUrl,
      views,
      likes: Math.floor(views * (Math.random() * 0.2 + 0.05)),
      comments: Math.floor(views * (Math.random() * 0.02 + 0.01)),
      publishDate,
      sentiments: {
        positive,
        negative,
        neutral
      },
      isShort: isShorts
    };
  });
};

const VideosTab: React.FC<VideosTabProps> = ({ period, dateRange }) => {
  // Use date range for generating mock videos
  const [mockShorts, setMockShorts] = useState<any[]>([]);
  const [mockVideos, setMockVideos] = useState<any[]>([]);
  
  // Update videos when date range changes
  useEffect(() => {
    const endDate = dateRange.to || new Date();
    
    // Generate new videos within the selected date range
    setMockShorts(generateMockVideos(20, true, dateRange.from, endDate));
    setMockVideos(generateMockVideos(12, false, dateRange.from, endDate));
  }, [dateRange]);

  return (
    <div className="space-y-10">
      {/* Shorts 섹션 */}
      <VideosGrid
        title="인기 쇼츠"
        videos={mockShorts}
        isShorts={true}
      />
      
      {/* 일반 영상 섹션 */}
      <VideosGrid
        title="인기 일반 영상"
        videos={mockVideos}
        isShorts={false}
      />
    </div>
  );
};

export default VideosTab;
