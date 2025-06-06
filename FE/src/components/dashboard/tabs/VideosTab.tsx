import React, { useState, useEffect } from 'react';
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

interface VideoItem {
  id: string;
  title: string;
  thumbnail_url: string;
  views: number;
  likes: number;
  comments: number;
  publish_date: string;
  is_short: boolean;
  sentiments: {
    positive: number;
    negative: number;
    neutral: number;
  };
}

// ✅ 테스트용 더미 데이터
const fallbackVideos: VideoItem[] = [
  // Shorts (is_short: true)
  {
    id: 'dummy-short-1',
    title: '백종원이 극찬한 흑백요리사 밤티라미수 초간단 레시피',
    thumbnail_url: 'https://via.placeholder.com/320x180?text=Short+1',
    views: 100000,
    likes: 5000,
    comments: 300,
    publish_date: '2024-10-03T11:47:00',
    is_short: true,
    sentiments: { positive: 70, negative: 10, neutral: 20 },
  },
  {
    id: 'dummy-short-2',
    title: '1분 컷 밤티라미수 만들기🔥',
    thumbnail_url: 'https://via.placeholder.com/320x180?text=Short+2',
    views: 85000,
    likes: 4200,
    comments: 250,
    publish_date: '2024-10-05T13:00:00',
    is_short: true,
    sentiments: { positive: 65, negative: 15, neutral: 20 },
  },
  {
    id: 'dummy-short-3',
    title: '요즘 유행하는 밤티라미수, 직접 먹어봤습니다!',
    thumbnail_url: 'https://via.placeholder.com/320x180?text=Short+3',
    views: 120000,
    likes: 6000,
    comments: 400,
    publish_date: '2024-10-07T19:00:00',
    is_short: true,
    sentiments: { positive: 68, negative: 12, neutral: 20 },
  },
  {
    id: 'dummy-short-4',
    title: '밤티라미수 리얼 먹방 (ASMR)',
    thumbnail_url: 'https://via.placeholder.com/320x180?text=Short+4',
    views: 95000,
    likes: 5500,
    comments: 280,
    publish_date: '2024-10-08T08:30:00',
    is_short: true,
    sentiments: { positive: 72, negative: 8, neutral: 20 },
  },
  {
    id: 'dummy-short-5',
    title: '밤티라미수 처음 먹어본 사람 반응ㅋㅋ',
    thumbnail_url: 'https://via.placeholder.com/320x180?text=Short+5',
    views: 110000,
    likes: 4900,
    comments: 320,
    publish_date: '2024-10-09T15:45:00',
    is_short: true,
    sentiments: { positive: 75, negative: 10, neutral: 15 },
  },

  // Long form (is_short: false)
  {
    id: 'dummy-long-1',
    title: '밤 티라미수 허겁지겁 먹는 안성재 보고 질투하는 최현석',
    thumbnail_url: 'https://via.placeholder.com/320x180?text=Long+1',
    views: 300000,
    likes: 8000,
    comments: 500,
    publish_date: '2024-10-10T14:20:00',
    is_short: false,
    sentiments: { positive: 60, negative: 15, neutral: 25 },
  },
  {
    id: 'dummy-long-2',
    title: '밤티라미수 비교 시식기🍰 (CU, GS, 세븐)',
    thumbnail_url: 'https://via.placeholder.com/320x180?text=Long+2',
    views: 200000,
    likes: 7000,
    comments: 450,
    publish_date: '2024-10-11T10:00:00',
    is_short: false,
    sentiments: { positive: 62, negative: 18, neutral: 20 },
  },
  {
    id: 'dummy-long-3',
    title: '편의점 밤티라미수 먹어본 후기 및 솔직한 평가',
    thumbnail_url: 'https://via.placeholder.com/320x180?text=Long+3',
    views: 180000,
    likes: 6500,
    comments: 410,
    publish_date: '2024-10-12T16:00:00',
    is_short: false,
    sentiments: { positive: 58, negative: 22, neutral: 20 },
  },
  {
    id: 'dummy-long-4',
    title: '밤티라미수 직접 만들어봤어요 (노오븐)',
    thumbnail_url: 'https://via.placeholder.com/320x180?text=Long+4',
    views: 220000,
    likes: 7700,
    comments: 480,
    publish_date: '2024-10-13T09:10:00',
    is_short: false,
    sentiments: { positive: 66, negative: 14, neutral: 20 },
  },
  {
    id: 'dummy-long-5',
    title: '밤티라미수 광고 vs 실제 제품 비교🔥',
    thumbnail_url: 'https://via.placeholder.com/320x180?text=Long+5',
    views: 250000,
    likes: 8200,
    comments: 530,
    publish_date: '2024-10-14T18:30:00',
    is_short: false,
    sentiments: { positive: 63, negative: 17, neutral: 20 },
  },
];


const VideosTab: React.FC<VideosTabProps> = ({ channel, period, dateRange }) => {
  const [shorts, setShorts] = useState<VideoItem[]>([]);
  const [longs, setLongs] = useState<VideoItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchVideos = async () => {
      try {
        const from = dateRange.from.toISOString().split('T')[0];
        const to = dateRange.to?.toISOString().split('T')[0] ?? from;

        const response = await fetch(
          `http://localhost:8000/api/videos?product=${encodeURIComponent(channel)}&from=${from}&to=${to}&platform=youtube`
        );

        if (!response.ok) throw new Error('API 요청 실패');

        const data = await response.json();

        if (Array.isArray(data.videos)) {
          // 🔎 클라이언트에서도 날짜 필터링
          const filtered = data.videos.filter((v: VideoItem) => {
            const publishDate = new Date(v.publish_date);
            const fromDate = new Date(dateRange.from);
            const toDate = dateRange.to ? new Date(dateRange.to) : fromDate;
            return publishDate >= fromDate && publishDate <= toDate;
          });

          const shorts = filtered.filter((v) => v.is_short);
          const longs = filtered.filter((v) => !v.is_short);

          setShorts(shorts);
          setLongs(longs);
        } else {
          throw new Error('데이터 형식 오류');
        }
      } catch (error) {
        console.warn('🔁 API 오류 발생, 더미 데이터를 사용합니다:', error);

        const fromDate = new Date(dateRange.from);
        const toDate = dateRange.to ? new Date(dateRange.to) : fromDate;

        const fallbackFiltered = fallbackVideos.filter((v) => {
          const publishDate = new Date(v.publish_date);
          return publishDate >= fromDate && publishDate <= toDate;
        });

        const shorts = fallbackFiltered.filter((v) => v.is_short);
        const longs = fallbackFiltered.filter((v) => !v.is_short);

        setShorts(shorts);
        setLongs(longs);
      } finally {
        setLoading(false);
      }
    };

    fetchVideos();
  }, [channel, dateRange.from, dateRange.to]); // 👈 수정된 의존성

  return (
    <div className="space-y-10">
      {loading ? (
        <p className="text-center text-muted-foreground">영상 데이터를 불러오는 중입니다...</p>
      ) : (
        <>
          <VideosGrid
            title="인기 쇼츠"
            videos={shorts}
            isShorts={true}
          />
          <VideosGrid
            title="인기 일반 영상"
            videos={longs}
            isShorts={false}
          />
        </>
      )}
    </div>
  );
};

export default VideosTab;
