import React, { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import SentimentSummaryCard from '../SentimentSummaryCard';
import SentimentTrendChart from '../charts/SentimentTrendChart';
import SentimentDonutChart from '../charts/SentimentDonutChart';
import { Loader2 } from 'lucide-react';

interface DateRange {
  from: Date;
  to?: Date;
}

interface SummaryTabProps {
  channel: string;
  period: string;
  dateRange: DateRange;
}

interface SentimentCounts {
  positive: number;
  neutral: number;
  negative: number;
}

const SENTIMENT_COLORS = {
  positive: "#A0E8AF",
  negative: "#F28B82",
  neutral: "#9FA8DA",
};

const SummaryTab: React.FC<SummaryTabProps> = ({ channel, period, dateRange }) => {
  const { keyword } = useParams<{ keyword: string }>();

  const [summaryData, setSummaryData] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!keyword) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        const res = await axios.get("http://localhost:8000/summary/overview", {
          params: {
            product: keyword,
            from: dateRange.from.toISOString().split("T")[0],
            to: dateRange.to?.toISOString().split("T")[0] ?? dateRange.from.toISOString().split("T")[0]
          }
        });
        setSummaryData(res.data);
      } catch (e) {
        console.error("요약 데이터 요청 실패", e);

        // ✅ fallback 더미 데이터
        setSummaryData({
          summary_change: {
            positive_change: "+1.45%",
            positive_delta: "0.38%",
            negative_change: "-0.32%",
            negative_delta: "0.11%",
            total_change: "+47",
            total_delta: "1.82%"
          },
          sentiment_distribution: {
            youtube: { positive: 60, neutral: 25, negative: 15 },
            tiktok: { positive: 35, neutral: 30, negative: 35 },
            instiz: { positive: 20, neutral: 30, negative: 50 },
            overall: { positive: 115, neutral: 85, negative: 100 }
          },
          sentiment_trend: [
            { date: "10/01", positive: 10, neutral: 3, negative: 5 },
            { date: "10/02", positive: 14, neutral: 5, negative: 6 },
            { date: "10/03", positive: 12, neutral: 4, negative: 7 },
            { date: "10/04", positive: 16, neutral: 6, negative: 5 },
            { date: "10/05", positive: 18, neutral: 5, negative: 6 },
            { date: "10/06", positive: 13, neutral: 4, negative: 4 },
            { date: "10/07", positive: 15, neutral: 3, negative: 7 }
          ]
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [keyword, dateRange]);

  const getSummaryCardData = useMemo(() => {
    if (!summaryData) return null;

    const { summary_change } = summaryData;

    return {
      positiveChange: summary_change.positive_change,
      positiveDelta: summary_change.positive_delta,
      positiveType: "increase" as const,
      negativeChange: summary_change.negative_change,
      negativeDelta: summary_change.negative_delta,
      negativeType: "decrease" as const,
      totalChange: summary_change.total_change,
      totalDelta: summary_change.total_delta,
      totalType: "increase" as const
    };
  }, [summaryData]);


  const getDonutChartData = (counts: SentimentCounts) => [
    { name: "긍정", value: counts.positive, color: SENTIMENT_COLORS.positive },
    { name: "중립", value: counts.neutral, color: SENTIMENT_COLORS.neutral },
    { name: "부정", value: counts.negative, color: SENTIMENT_COLORS.negative }
  ];

  const dist = summaryData?.sentiment_distribution;

  const trendData = summaryData?.sentiment_trend ?? [];

  const currentDist = useMemo(() => {
    if (!dist) return { positive: 0, neutral: 0, negative: 0 };

    if (channel === "유튜브") return dist.youtube;
    if (channel === "틱톡") return dist.tiktok;
    if (channel === "인스티즈") return dist.instiz;
    return dist.overall;
  }, [channel, dist]);

  if (loading || !summaryData) {
    return (
      <div className="w-full flex justify-center items-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <SentimentSummaryCard
          title="긍정 언급 비율"
          value={getSummaryCardData?.positiveChange}
          delta={getSummaryCardData?.positiveDelta}
          deltaType={getSummaryCardData?.positiveType}
          description="지난 기간 대비"
        />
        <SentimentSummaryCard
          title="부정 언급 비율"
          value={getSummaryCardData?.negativeChange}
          delta={getSummaryCardData?.negativeDelta}
          deltaType={getSummaryCardData?.negativeType}
          description="지난 기간 대비"
        />
        <SentimentSummaryCard
          title="수집된 콘텐츠 수"
          value={getSummaryCardData?.totalChange}
          delta={getSummaryCardData?.totalDelta}
          deltaType={getSummaryCardData?.totalType}
          description="지난 기간 대비"
        />
      </div>

      <SentimentTrendChart
        dateRange={dateRange}
        platform={channel}
        data={trendData}
      />

      <SentimentDonutChart
        title={channel === "전체" ? "전체 감성 분포" : `${channel} 감성 분포`}
        description="선택된 채널의 댓글 감성 비율"
        data={getDonutChartData(currentDist ?? { positive: 0, neutral: 0, negative: 0 })}
        showCount={true}
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <SentimentDonutChart
          title="유튜브 감성 분석"
          description="유튜브 댓글 감성 분포"
          data={getDonutChartData(dist?.youtube ?? { positive: 0, neutral: 0, negative: 0 })}
          showCount
        />
        <SentimentDonutChart
          title="틱톡 감성 분석"
          description="틱톡 댓글 감성 분포"
          data={getDonutChartData(dist?.tiktok ?? { positive: 0, neutral: 0, negative: 0 })}
          showCount
        />
        <SentimentDonutChart
          title="인스티즈 감성 분석"
          description="커뮤니티 댓글 감성 분포"
          data={getDonutChartData(dist?.instiz ?? { positive: 0, neutral: 0, negative: 0 })}
          showCount
        />
      </div>
    </div>
  );
};

export default SummaryTab;
