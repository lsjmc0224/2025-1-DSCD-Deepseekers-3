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

// 실제 유튜브 영상 데이터 기반 더미 데이터 (2024년 10월)
// sentiment 집계는 content_analysis.csv의 youtube_comments 기준
const realVideoData = [
  {
    id: 'TzwAoZc25NU',
    title: '백종원이 극찬한 흑백요리사 밤티라미수 초간단 레시피',
    thumbnailUrl: 'https://source.unsplash.com/320x180/?snack,food,TzwAoZc25NU',
    views: 262799,
    likes: 6068,
    comments: 36,
    publishDate: new Date('2024-10-03T11:47:00'),
    isShort: true,
    sentiments: { positive: 7, negative: 0, neutral: 0 }, // 실제 집계
  },
  {
    id: 'ts17rlS_J1Q',
    title: '밤 티라미수 허겁지겁 먹는 안성재 보고 질투하는 최현석 #흑백요리사',
    thumbnailUrl: 'https://source.unsplash.com/320x180/?snack,food,ts17rlS_J1Q',
    views: 3728657,
    likes: 57585,
    comments: 389,
    publishDate: new Date('2024-10-19T08:31:01'),
    isShort: true,
    sentiments: { positive: 0, negative: 0, neutral: 0 },
  },
  {
    id: 'IjD_10cv4CA',
    title: '흑백요리사 아니 흙백요리사 도전',
    thumbnailUrl: 'https://source.unsplash.com/320x180/?snack,food,IjD_10cv4CA',
    views: 884427,
    likes: 20207,
    comments: 212,
    publishDate: new Date('2024-10-12T08:45:09'),
    isShort: true,
    sentiments: { positive: 2, negative: 0, neutral: 0 },
  },
  {
    id: 'nOqmbUQ51uc',
    title: '나폴리맛피아 밤티라미수 #흑백요리사',
    thumbnailUrl: 'https://source.unsplash.com/320x180/?snack,food,nOqmbUQ51uc',
    views: 83798,
    likes: 1911,
    comments: 29,
    publishDate: new Date('2024-10-01T09:30:27'),
    isShort: true,
    sentiments: { positive: 0, negative: 0, neutral: 0 },
  },
  {
    id: '7pzr9AZWk-U',
    title: '꼭 해먹어봐야 하는 흑백요리사 밤 티라미수',
    thumbnailUrl: 'https://source.unsplash.com/320x180/?snack,food,7pzr9AZWk-U',
    views: 58958,
    likes: 856,
    comments: 21,
    publishDate: new Date('2024-10-04T09:00:07'),
    isShort: true,
    sentiments: { positive: 1, negative: 0, neutral: 0 },
  },
  {
    id: 'g3hVg98AMlI',
    title: '백종원 & 안성재 함박웃음 짓게 만든 나폴리 맛피아의 밤 티라미수 | 흑백요리사: 요리 계급 전쟁 | 넷플릭스',
    thumbnailUrl: 'https://source.unsplash.com/320x180/?snack,food,g3hVg98AMlI',
    views: 2605416,
    likes: 19645,
    comments: 3030,
    publishDate: new Date('2024-10-01T12:00:00'),
    isShort: false,
    sentiments: { positive: 0, negative: 0, neutral: 0 },
  },
  {
    id: 'kw7T23teao4',
    title: '지금 빨리 팔아야 할!!!!!! 밤 티라미수 카페용 레시피 (디저트,라떼)',
    thumbnailUrl: 'https://source.unsplash.com/320x180/?snack,food,kw7T23teao4',
    views: 42139,
    likes: 702,
    comments: 37,
    publishDate: new Date('2024-10-23T05:30:37'),
    isShort: false,
    sentiments: { positive: 4, negative: 0, neutral: 0 },
  },
  {
    id: 'AKlZr07uxkI',
    title: '딱 이렇게 만들어야 제일 맛있어요! 흑백요리사 나폴리 맛피아의 밤 티라미수 만들기',
    thumbnailUrl: 'https://source.unsplash.com/320x180/?snack,food,AKlZr07uxkI',
    views: 23855,
    likes: 353,
    comments: 28,
    publishDate: new Date('2024-10-07T15:12:46'),
    isShort: false,
    sentiments: { positive: 0, negative: 0, neutral: 0 },
  },
  {
    id: '5TFJc-VJx0c',
    title: '파티쉐가 작정하고 밤 티라미수를 만들면? 고급 버전 공개',
    thumbnailUrl: 'https://source.unsplash.com/320x180/?snack,food,5TFJc-VJx0c',
    views: 3762,
    likes: 68,
    comments: 19,
    publishDate: new Date('2024-10-20T04:42:28'),
    isShort: false,
    sentiments: { positive: 1, negative: 0, neutral: 0 },
  },
  {
    id: 'ZdvROQxs9uY',
    title: '밤 티라미수: 흑백요리사 나폴리맛피아 인스파이어드',
    thumbnailUrl: 'https://source.unsplash.com/320x180/?snack,food,ZdvROQxs9uY',
    views: 82600,
    likes: 2616,
    comments: 140,
    publishDate: new Date('2024-10-12T15:16:51'),
    isShort: false,
    sentiments: { positive: 0, negative: 0, neutral: 0 },
  },
  {
    id: 'b6Yj5KxGRSU',
    title: '＜흑백요리사＞ 밤 티라미수 따라잡는 ＜냉부해＞표 티라미수?!🌟 토니정&유현수 셰프의 티라미수 몰아보기｜냉장고를 부탁해｜JTBC 180226 방송 외',
    thumbnailUrl: 'https://source.unsplash.com/320x180/?snack,food,b6Yj5KxGRSU',
    views: 41868,
    likes: 280,
    comments: 63,
    publishDate: new Date('2024-10-03T05:00:30'),
    isShort: false,
    sentiments: { positive: 0, negative: 0, neutral: 0 },
  },
  {
    id: 'G7k-d_ap-7A',
    title: "[sub] 흑백요리사 우승자 '나폴리 맛피아'까지 모셔온 섭외력의 비밀 I 혤's club🍸 ep30 권성준 셰프",
    thumbnailUrl: 'https://source.unsplash.com/320x180/?snack,food,G7k-d_ap-7A',
    views: 1990357,
    likes: 25216,
    comments: 1286,
    publishDate: new Date('2024-10-18T09:00:23'),
    isShort: false,
    sentiments: { positive: 2, negative: 0, neutral: 0 },
  },
  {
    id: 'Ssqr1NDvrHU',
    title: '⭐CU 편의점 특집⭐ 요즘 핫한 밤 티라미수 드디어 구했습니다❗❗❗(※광고 아님) 241022/Mukbang, eating show',
    thumbnailUrl: 'https://source.unsplash.com/320x180/?snack,food,Ssqr1NDvrHU',
    views: 92771,
    likes: 1193,
    comments: 54,
    publishDate: new Date('2024-10-23T01:30:16'),
    isShort: false,
    sentiments: { positive: 2, negative: 0, neutral: 0 },
  },
  {
    id: '-CVvWNwjU48',
    title: '이탈리아 레전드들이 평가하는 나폴리 맛피아 음식 수준 ㄷㄷㄷ 진짜 이탈리아인의 반응이 이정도??? (ENG SUB)',
    thumbnailUrl: 'https://source.unsplash.com/320x180/?snack,food,-CVvWNwjU48',
    views: 7692484,
    likes: 97829,
    comments: 5589,
    publishDate: new Date('2024-10-27T10:30:00'),
    isShort: false,
    sentiments: { positive: 0, negative: 0, neutral: 0 },
  },
  {
    id: 'u3UXhNMqsws',
    title: '흑백요리사 속 밤 티라미수 재현하기! 비싼 재료로 만들면 더 맛있을까?',
    thumbnailUrl: 'https://source.unsplash.com/320x180/?snack,food,u3UXhNMqsws',
    views: 5618,
    likes: 78,
    comments: 9,
    publishDate: new Date('2024-10-04T15:04:08'),
    isShort: false,
    sentiments: { positive: 0, negative: 0, neutral: 0 },
  },
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
  // 실제 데이터로 대체
  const shorts = realVideoData.filter(v => v.isShort);
  const videos = realVideoData.filter(v => !v.isShort);

  return (
    <div className="space-y-10">
      {/* Shorts 섹션 */}
      <VideosGrid
        title="인기 쇼츠"
        videos={shorts}
        isShorts={true}
      />
      {/* 일반 영상 섹션 */}
      <VideosGrid
        title="인기 일반 영상"
        videos={videos}
        isShorts={false}
      />
    </div>
  );
};

export default VideosTab;
