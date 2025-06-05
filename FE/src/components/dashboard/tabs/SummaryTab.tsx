
import React, { useMemo } from 'react';
import SentimentSummaryCard from '../SentimentSummaryCard';
import SentimentTrendChart from '../charts/SentimentTrendChart';
import SentimentDonutChart from '../charts/SentimentDonutChart';

interface DateRange {
  from: Date;
  to?: Date;
}

interface SummaryTabProps {
  channel: string;
  period: string;
  dateRange: DateRange;
}

const SummaryTab: React.FC<SummaryTabProps> = ({ channel, period, dateRange }) => {
  // Define consistent color palette for all charts
  const SENTIMENT_COLORS = {
    positive: "#A0E8AF",  // Light Green
    negative: "#F28B82",  // Soft Red
    neutral: "#9FA8DA",   // Purple
    total: "#D1C4E9"      // Light Purple for total line
  };
  
  // Platform-specific percentages and totals based on channel filter
  const getPlatformData = useMemo(() => {
    const baseTotals = {
      youtube: 500,
      tiktok: 500,
      instiz: 500, // Changed from community to instiz
      overall: 1500
    };

    // Adjust totals based on period
    const periodMultiplier = {
      "최근 7일": 1,
      "최근 14일": 1.8,
      "최근 30일": 3.5,
      "사용자 지정": 2 // Default multiplier for custom range
    };

    const multiplier = periodMultiplier[period as keyof typeof periodMultiplier] || 1;
    
    const adjustedTotals = {
      youtube: Math.round(baseTotals.youtube * multiplier),
      tiktok: Math.round(baseTotals.tiktok * multiplier),
      instiz: Math.round(baseTotals.instiz * multiplier),
      overall: Math.round(baseTotals.overall * multiplier)
    };

    const platformPercentages = {
      youtube: {
        positive: 65,
        neutral: 20,
        negative: 15
      },
      tiktok: {
        positive: 40,
        neutral: 30,
        negative: 30
      },
      instiz: {
        positive: 20,
        neutral: 25,
        negative: 55
      }
    };

    return { adjustedTotals, platformPercentages };
  }, [channel, period]);

  // Calculate counts for each platform
  const calculateCounts = (percentages: { positive: number, neutral: number, negative: number }, totalCount: number) => {
    return {
      positive: Math.round((percentages.positive / 100) * totalCount),
      neutral: Math.round((percentages.neutral / 100) * totalCount),
      negative: Math.round((percentages.negative / 100) * totalCount)
    };
  };

  const { adjustedTotals, platformPercentages } = getPlatformData;
  
  const youtubeCounts = calculateCounts(platformPercentages.youtube, adjustedTotals.youtube);
  const tiktokCounts = calculateCounts(platformPercentages.tiktok, adjustedTotals.tiktok);
  const instizCounts = calculateCounts(platformPercentages.instiz, adjustedTotals.instiz);
  
  const overallCounts = {
    positive: youtubeCounts.positive + tiktokCounts.positive + instizCounts.positive,
    neutral: youtubeCounts.neutral + tiktokCounts.neutral + instizCounts.neutral,
    negative: youtubeCounts.negative + tiktokCounts.negative + instizCounts.negative
  };

  // Get current platform data based on channel filter
  const getCurrentPlatformData = useMemo(() => {
    switch(channel) {
      case "유튜브":
        return {
          counts: youtubeCounts,
          total: adjustedTotals.youtube,
          percentages: platformPercentages.youtube
        };
      case "틱톡":
        return {
          counts: tiktokCounts,
          total: adjustedTotals.tiktok,
          percentages: platformPercentages.tiktok
        };
      case "인스티즈":
        return {
          counts: instizCounts,
          total: adjustedTotals.instiz,
          percentages: platformPercentages.instiz
        };
      default: // "전체"
        return {
          counts: overallCounts,
          total: adjustedTotals.overall,
          percentages: {
            positive: Math.round((overallCounts.positive / (overallCounts.positive + overallCounts.neutral + overallCounts.negative)) * 100),
            neutral: Math.round((overallCounts.neutral / (overallCounts.positive + overallCounts.neutral + overallCounts.negative)) * 100),
            negative: Math.round((overallCounts.negative / (overallCounts.positive + overallCounts.neutral + overallCounts.negative)) * 100)
          }
        };
    }
  }, [channel, youtubeCounts, tiktokCounts, instizCounts, overallCounts, adjustedTotals, platformPercentages]);

  // Get summary card data based on period and platform
  const getSummaryCardData = useMemo(() => {
    const baseData = {
      "최근 7일": {
        positiveChange: "+8.5%",
        positiveDelta: "2.1%",
        negativeChange: "-1.2%",
        negativeDelta: "0.4%",
        totalChange: "+245",
        totalDelta: "12.3%"
      },
      "최근 14일": {
        positiveChange: "+12.3%",
        positiveDelta: "4.2%",
        negativeChange: "-1.8%",
        negativeDelta: "0.6%",
        totalChange: "+382",
        totalDelta: "15.8%"
      },
      "최근 30일": {
        positiveChange: "+16.8%",
        positiveDelta: "9.4%",
        negativeChange: "-3.5%",
        negativeDelta: "1.7%",
        totalChange: "+528",
        totalDelta: "23.2%"
      },
      "사용자 지정": {
        positiveChange: "+14.2%",
        positiveDelta: "5.8%",
        negativeChange: "-2.1%",
        negativeDelta: "0.9%",
        totalChange: "+421",
        totalDelta: "18.5%"
      }
    };

    const data = baseData[period as keyof typeof baseData] || baseData["최근 7일"];
    
    // Adjust data based on platform
    const platformMultiplier = {
      "전체": 1,
      "유튜브": 1.2,
      "틱톡": 0.8,
      "인스티즈": 0.6
    };

    const multiplier = platformMultiplier[channel as keyof typeof platformMultiplier] || 1;
    
    return {
      positiveChange: data.positiveChange,
      positiveDelta: `${(parseFloat(data.positiveDelta) * multiplier).toFixed(1)}%`,
      positiveType: "increase" as const,
      negativeChange: data.negativeChange,
      negativeDelta: `${(parseFloat(data.negativeDelta) * multiplier).toFixed(1)}%`,
      negativeType: "decrease" as const,
      totalChange: `+${Math.round(parseInt(data.totalChange.replace('+', '')) * multiplier)}`,
      totalDelta: `${(parseFloat(data.totalDelta) * multiplier).toFixed(1)}%`,
      totalType: "increase" as const
    };
  }, [period, channel]);
  
  // Generate donut chart data for current platform/filter
  const currentPlatformDonutData = useMemo(() => {
    const { counts } = getCurrentPlatformData;
    return [
      { name: "긍정", value: counts.positive, color: SENTIMENT_COLORS.positive },
      { name: "중립", value: counts.neutral, color: SENTIMENT_COLORS.neutral },
      { name: "부정", value: counts.negative, color: SENTIMENT_COLORS.negative }
    ];
  }, [getCurrentPlatformData, SENTIMENT_COLORS]);

  // Generate individual platform donut chart data (always show all platforms)
  const youtubeDonutData = useMemo(() => {
    return [
      { name: "긍정", value: youtubeCounts.positive, color: SENTIMENT_COLORS.positive },
      { name: "중립", value: youtubeCounts.neutral, color: SENTIMENT_COLORS.neutral },
      { name: "부정", value: youtubeCounts.negative, color: SENTIMENT_COLORS.negative }
    ];
  }, [youtubeCounts, SENTIMENT_COLORS]);

  const tiktokDonutData = useMemo(() => {
    return [
      { name: "긍정", value: tiktokCounts.positive, color: SENTIMENT_COLORS.positive },
      { name: "중립", value: tiktokCounts.neutral, color: SENTIMENT_COLORS.neutral },
      { name: "부정", value: tiktokCounts.negative, color: SENTIMENT_COLORS.negative }
    ];
  }, [tiktokCounts, SENTIMENT_COLORS]);

  const instizDonutData = useMemo(() => {
    return [
      { name: "긍정", value: instizCounts.positive, color: SENTIMENT_COLORS.positive },
      { name: "중립", value: instizCounts.neutral, color: SENTIMENT_COLORS.neutral },
      { name: "부정", value: instizCounts.negative, color: SENTIMENT_COLORS.negative }
    ];
  }, [instizCounts, SENTIMENT_COLORS]);

  return (
    <div className="space-y-6">
      {/* Summary Cards - Period and Platform specific data */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <SentimentSummaryCard
          title="긍정 언급 변화율"
          value={getSummaryCardData.positiveChange}
          delta={getSummaryCardData.positiveDelta}
          deltaType={getSummaryCardData.positiveType}
          description="지난 기간 대비"
        />
        <SentimentSummaryCard
          title="부정 언급 변화율"
          value={getSummaryCardData.negativeChange}
          delta={getSummaryCardData.negativeDelta}
          deltaType={getSummaryCardData.negativeType}
          description="지난 기간 대비"
        />
        <SentimentSummaryCard
          title="총 콘텐츠 수 변화"
          value={getSummaryCardData.totalChange}
          delta={getSummaryCardData.totalDelta}
          deltaType={getSummaryCardData.totalType}
          description="지난 기간 대비"
        />
      </div>

      {/* Trend Chart - Platform and Period specific */}
      <div className="grid grid-cols-1 gap-6">
        <div className="col-span-1">
          <SentimentTrendChart 
            dateRange={dateRange} 
            platform={channel}
          />
        </div>
      </div>

      {/* Current Platform/Filter Sentiment Distribution */}
      <div className="grid grid-cols-1 gap-6">
        <SentimentDonutChart
          title={channel === "전체" ? "전체 감성 분포" : `${channel} 감성 분포`}
          description={channel === "전체" ? "전체 댓글 기준 감성 비율" : `${channel} 댓글 감성 분포`}
          data={currentPlatformDonutData}
          showCount={true}
        />
      </div>

      {/* Individual Platform Charts - Always show all platforms with period-adjusted data */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <SentimentDonutChart
          title="유튜브 감성 분석"
          description="유튜브 댓글 감성 분포"
          data={youtubeDonutData}
          emptyMessage="유튜브 채널 데이터가 없습니다"
          showCount={true}
        />
        
        <SentimentDonutChart
          title="틱톡 감성 분석"
          description="틱톡 댓글 감성 분포"
          data={tiktokDonutData}
          emptyMessage="틱톡 채널 데이터가 없습니다"
          showCount={true}
        />
        
        <SentimentDonutChart
          title="인스티즈 감성 분석"
          description="온라인 커뮤니티 감성 분포"
          data={instizDonutData}
          emptyMessage="인스티즈 채널 데이터가 없습니다"
          showCount={true}
        />
      </div>
    </div>
  );
};

export default SummaryTab;
