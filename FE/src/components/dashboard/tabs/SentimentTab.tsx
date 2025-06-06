
import React, { useState, useMemo } from 'react';
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import SentimentKeywordsSummary from '../SentimentKeywordsSummary';
import CommentsList from '../CommentsList';
import AttributeSentimentChart from '../charts/AttributeSentimentChart';
import { Bot, Smile, Frown } from 'lucide-react';

interface DateRange {
  from: Date;
  to?: Date;
}

interface SentimentTabProps {
  channel: string;
  period: string;
  dateRange: DateRange;
}

const SentimentTab: React.FC<SentimentTabProps> = ({ channel, period, dateRange }) => {
  const [positiveLikesFilter, setPositiveLikesFilter] = useState("좋아요 상위 10%");
  const [negativeLikesFilter, setNegativeLikesFilter] = useState("좋아요 상위 10%");

  // Event handlers for the new UI elements
  const handlePositiveAllClick = () => {
    console.log("긍정 전체 버튼 클릭");
    // TODO: 전체 데이터 필터링 없이 보여주는 기능
  };

  const handleNegativeAllClick = () => {
    console.log("부정 전체 버튼 클릭");
    // TODO: 전체 데이터 필터링 없이 보여주는 기능
  };

  const handlePositiveLikesFilterChange = (value: string) => {
    setPositiveLikesFilter(value);
    console.log("긍정 좋아요 필터 변경:", value);
    // TODO: 선택된 비율 이상의 좋아요를 받은 댓글만 필터링
  };

  const handleNegativeLikesFilterChange = (value: string) => {
    setNegativeLikesFilter(value);
    console.log("부정 좋아요 필터 변경:", value);
    // TODO: 선택된 비율 이상의 좋아요를 받은 댓글만 필터링
  };

  // 감성 분석 컬러 팔레트 통일
  const SENTIMENT_COLORS = {
    positive: "#A0E8AF",  // Light Green
    negative: "#F28B82",  // Soft Red
    neutral: "#9FA8DA"    // Purple
  };

  // Platform and period-based multipliers for dynamic data
  const getPlatformMultiplier = useMemo(() => {
    const platformMultipliers = {
      "전체": 1,
      "유튜브": 1.2,
      "틱톡": 0.8,
      "인스티즈": 0.6
    };
    return platformMultipliers[channel as keyof typeof platformMultipliers] || 1;
  }, [channel]);

  const getPeriodMultiplier = useMemo(() => {
    const periodMultipliers = {
      "최근 7일": 1,
      "최근 14일": 1.8,
      "최근 30일": 3.5,
      "사용자 지정": 2
    };
    return periodMultipliers[period as keyof typeof periodMultipliers] || 1;
  }, [period]);

  // Dynamic keywords based on platform and period
  const getDynamicKeywords = useMemo(() => {
    const basePositiveKeywords = [
      { text: "달달", size: "xl" as const, type: "positive" as const },
      { text: "맛있", size: "lg" as const, type: "positive" as const },
      { text: "촉촉", size: "md" as const, type: "positive" as const },
      { text: "편의점", size: "md" as const, type: "positive" as const },
      { text: "행복", size: "xs" as const, type: "positive" as const },
    ];

    const baseNegativeKeywords = [
      { text: "느끼", size: "lg" as const, type: "negative" as const },
      { text: "리뉴얼", size: "lg" as const, type: "negative" as const },
      { text: "단맛", size: "md" as const, type: "negative" as const },
      { text: "세븐", size: "md" as const, type: "negative" as const },
      { text: "CU", size: "xs" as const, type: "negative" as const },
    ];

    // Platform-specific keyword variations
    if (channel === "유튜브") {
      basePositiveKeywords.unshift({ text: "영상과 어울림", size: "lg" as const, type: "positive" as const });
      baseNegativeKeywords.unshift({ text: "과대광고", size: "md" as const, type: "negative" as const });
    } else if (channel === "틱톡") {
      basePositiveKeywords.unshift({ text: "트렌드 맛", size: "lg" as const, type: "positive" as const });
      baseNegativeKeywords.unshift({ text: "SNS용만", size: "md" as const, type: "negative" as const });
    } else if (channel === "인스티즈") {
      basePositiveKeywords.unshift({ text: "솔직 후기", size: "lg" as const, type: "positive" as const });
      baseNegativeKeywords.unshift({ text: "실망", size: "md" as const, type: "negative" as const });
    }

    return {
      positive: basePositiveKeywords,
      negative: baseNegativeKeywords
    };
  }, [channel]);

  // Dynamic comments based on platform and period
  const getDynamicComments = useMemo(() => {
    const allPositiveComments = [
      {
        id: "pc1",
        text: "밤티라미수 후기36 맛있긴 한데 또 찾아 먹을 맛은 아니지만 누가 주면 다 먹을 듯",
        date: new Date("2023-10-07T14:32:00"),
        sentiment: "positive" as const,
        source: "인스티즈" as const
      },
      {
        id: "pc2",
        text: "쓰다보니 맛없는줄알겠는데 맛있음!",
        date: new Date("2023-10-06T09:15:00"),
        sentiment: "positive" as const,
        source: "인스티즈" as const
      },
      {
        id: "pc3",
        text: "하나 먹어보고 너무 맛있어서 바로 하나 더 테이크아웃 해서 집에 가져옴..",
        date: new Date("2023-10-04T16:22:00"),
        sentiment: "positive" as const,
        source: "인스티즈" as const
      },
      {
        id: "pc4",
        text: "밤티라미수 후기 한입 먹었을 땐 오 맛있는데?",
        date: new Date("2023-10-03T12:45:00"),
        sentiment: "positive" as const,
        source: "인스티즈" as const
      },
      {
        id: "pc5",
        text: "편의점디저트 늘 기대이하였는데 얘는 맛있다!!	",
        date: new Date("2023-10-08T11:20:00"),
        sentiment: "positive" as const,
        source: "인스티즈" as const
      },
    ];

    const allNegativeComments = [
      {
        id: "nc1",
        text: "떼랑 먹는데 아메리카노랑 먹어야될듯맛피아 인스타보니 달기 줄이고 그래놀라 식감개선하겠다던데...",
        date: new Date("2023-10-05T19:47:00"),
        sentiment: "negative" as const,
        source: "인스티즈" as const
      },
      {
        id: "nc2",
        text: "매장에 재고가 있나포켓씨유로 보니까 매장졀 재고에는 상품 이름조차 안 뜨길래ㅠㅠㅠ",
        date: new Date("2023-10-03T11:08:00"),
        sentiment: "negative" as const,
        source: "인스티즈" as const
      },
      {
        id: "nc3",
        text: "씨유 밤티라미수 리뉴얼 되고나서 왜 칼로리가 더 높아졌을까",
        date: new Date("2023-10-02T15:30:00"),
        sentiment: "negative" as const,
        source: "인스티즈" as const
      },
      {
        id: "nc4",
        text: "너무 느끼해요..ㅠㅠ",
        date: new Date("2023-10-29T10:15:00"),
        sentiment: "negative" as const,
        source: "인스티즈" as const
      },
      {
        id: "nc5",
        text: "리뉴얼이 확실히 돼야할듯.",
        date: new Date("2023-05-01T13:25:00"),
        sentiment: "negative" as const,
        source: "인스티즈" as const
      },
      {
        id: "nc6",
        text: "	씨유 밤티라미수 먹었는데 엄..",
        date: new Date("2023-05-07T16:40:00"),
        sentiment: "negative" as const,
        source: "인스티즈" as const
      }
    ];

    // Filter comments based on selected channel
    const filterCommentsByChannel = (comments: any[], selectedChannel: string) => {
      if (selectedChannel === "전체") return comments;
      
      const channelMap: Record<string, string> = {
        "유튜브": "유튜브",
        "틱톡": "틱톡",
        "인스티즈": "인스티즈"
      };
      
      return comments.filter(comment => comment.source === channelMap[selectedChannel]);
    };

    return {
      positive: filterCommentsByChannel(allPositiveComments, channel),
      negative: filterCommentsByChannel(allNegativeComments, channel)
    };
  }, [channel]);

  // Generate a filtered AI summary based on selected channel and period
  const aiSummary = useMemo(() => {
    let baseText = `최근 ${period} 동안 '밤 티라미수' 제품에 대해 수집된 데이터를 분석한 결과, `;
    
    if (channel !== "전체") {
      baseText += `${channel} 채널에서는 `;
    }
    
    // Platform-specific insights
    let platformInsight = "";
    if (channel === "유튜브") {
      platformInsight = "영상 리뷰를 통해 시각적 만족도가 높게 나타났으며, ";
    } else if (channel === "틱톡") {
      platformInsight = "짧은 영상 형태의 후기가 많아 트렌드 요소가 강조되었으며, ";
    } else if (channel === "인스티즈") {
      platformInsight = "솔직한 커뮤니티 후기가 많아 실제 구매 경험이 상세히 공유되었으며, ";
    }
    
    // Period-specific data volume indicators
    const volumeIndicator = period === "최근 30일" ? "대량의 " : period === "최근 14일" ? "충분한 " : "적절한 ";
    
    baseText += `${platformInsight}'맛'과 '식감' 측면에서 긍정적인 평가가 높게 나타났습니다. ${volumeIndicator}데이터를 통해 분석한 결과, 특히 '부드러움'과 '촉촉함'에 대한 만족도가 두드러지며, '밤 향'과 '크림'의 조화에 대한 긍정적 언급이 다수 있었습니다.
    
    반면 '가격'과 '양'에 대해서는 가성비에 대한 부정적인 언급이 다수 포착되었으며, 일부 소비자들은 '인공적인 맛'과 '과도한 단맛'에 대해 불만을 표시했습니다. ${channel === "유튜브" ? "유튜브에서는 특히 영상과 실제 제품의 차이에 대한 언급이 있었습니다. " : ""}${channel === "인스티즈" ? "인스티즈에서는 '가격 대비 양'에 대한 아쉬움이 특히 많이 언급되었습니다. " : ""}${channel === "틱톡" ? "틱톡에서는 시각적 만족도는 높지만 실제 맛에 대한 평가가 엇갈렸습니다. " : ""}
    
    전반적으로는 긍정적 의견이 부정적 의견보다 우세하나, '인공적인 맛'과 '단맛'에 대한 피드백은 제품 개선 시 고려할 필요가 있습니다.`;
    
    return baseText;
  }, [channel, period]);

  return (
    <div className="space-y-8">
      {/* AI 분석 감성 요약 - 로봇 아이콘 추가 */}
      <Card className="shadow-sm border border-slate-200">
        <CardHeader className="flex flex-row items-start space-x-3">
          <Bot className="h-6 w-6 text-primary mt-1" />
          <div>
            <CardTitle>🤖 AI 분석 요약</CardTitle>
            <CardDescription>
              AI가 분석한 밤 티라미수 제품의 주요 감성 인사이트 
              {channel !== "전체" && `(${channel} 채널 기준)`}
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-32 rounded-md border p-4">
            <p className="text-sm text-foreground">
              {aiSummary}
            </p>
          </ScrollArea>
        </CardContent>
      </Card>
      
      {/* 긍정/부정 감성 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 긍정 감성 카드 - 색상 강화 */}
        <Card className="shadow-sm h-full border-l-4 border-l-[#A0E8AF] bg-green-50">
          <CardHeader className="flex flex-row items-start space-x-3">
            <Smile className="h-6 w-6 text-[#A0E8AF] mt-1" />
            <div className="flex-1">
              <CardTitle>😊 긍정 감성 분석</CardTitle>
              <CardDescription>
                자주 언급된 긍정적 키워드와 댓글
                {channel !== "전체" && ` (${channel})`}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2 ml-auto">
              <Button 
                size="sm" 
                variant="outline"
                onClick={handlePositiveAllClick}
              >
                전체
              </Button>
              <Select value={positiveLikesFilter} onValueChange={handlePositiveLikesFilterChange}>
                <SelectTrigger className="w-auto min-w-[140px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="좋아요 상위 5%">좋아요 상위 5%</SelectItem>
                  <SelectItem value="좋아요 상위 10%">좋아요 상위 10%</SelectItem>
                  <SelectItem value="좋아요 상위 20%">좋아요 상위 20%</SelectItem>
                  <SelectItem value="좋아요 상위 50%">좋아요 상위 50%</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-sm">
                <p>밤 티라미수는 <strong className="text-[#A0E8AF]">크림이 풍부</strong>하고 <strong className="text-[#A0E8AF]">부드러운 식감</strong>이 가장 많이 언급되었습니다. <strong className="text-[#A0E8AF]">달달함</strong>과 <strong className="text-[#A0E8AF]">촉촉함</strong>에 대한 만족도가 높으며, 특히 <strong className="text-[#A0E8AF]">밤 맛이 진하다</strong>는 평가가 주를 이룹니다.</p>
              </div>
              <CommentsList
                title="최신 긍정 댓글"
                description={`최근에 수집된 긍정적인 댓글${channel !== "전체" ? ` (${channel})` : ""}`}
                comments={getDynamicComments.positive}
              />
            </div>
          </CardContent>
        </Card>
        
        {/* 부정 감성 카드 - 색상 강화 */}
        <Card className="shadow-sm h-full border-l-4 border-l-[#F28B82] bg-red-50">
          <CardHeader className="flex flex-row items-start space-x-3">
            <Frown className="h-6 w-6 text-[#F28B82] mt-1" />
            <div className="flex-1">
              <CardTitle>🙁 부정 감성 분석</CardTitle>
              <CardDescription>
                자주 언급된 부정적 키워드와 댓글
                {channel !== "전체" && ` (${channel})`}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2 ml-auto">
              <Button 
                size="sm" 
                variant="outline"
                onClick={handleNegativeAllClick}
              >
                전체
              </Button>
              <Select value={negativeLikesFilter} onValueChange={handleNegativeLikesFilterChange}>
                <SelectTrigger className="w-auto min-w-[140px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="좋아요 상위 5%">좋아요 상위 5%</SelectItem>
                  <SelectItem value="좋아요 상위 10%">좋아요 상위 10%</SelectItem>
                  <SelectItem value="좋아요 상위 20%">좋아요 상위 20%</SelectItem>
                  <SelectItem value="좋아요 상위 50%">좋아요 상위 50%</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-sm">
                <p>밤 티라미수에 대한 주요 불만사항으로는 <strong className="text-[#F28B82]">너무 달다</strong>는 의견이 가장 많고, <strong className="text-[#F28B82]">인공적인 맛</strong>과 <strong className="text-[#F28B82]">느끼함</strong>에 대한 부정적 의견이 꾸준히 제기되고 있습니다. 또한 <strong className="text-[#F28B82]">가격 대비 양</strong>에 대한 아쉬움도 다수 확인됩니다.</p>
              </div>
              <CommentsList
                title="최신 부정 댓글"
                description={`최근에 수집된 부정적인 댓글${channel !== "전체" ? ` (${channel})` : ""}`}
                comments={getDynamicComments.negative}
              />
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* 키워드 워드클라우드 섹션 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
        {/* 긍정 키워드 */}
        <SentimentKeywordsSummary
          title="긍정 키워드"
          description={`자주 언급된 긍정적 키워드${channel !== "전체" ? ` (${channel})` : ""}`}
          keywords={getDynamicKeywords.positive}
        />
        
        {/* 부정 키워드 */}
        <SentimentKeywordsSummary
          title="부정 키워드"
          description={`자주 언급된 부정적 키워드${channel !== "전체" ? ` (${channel})` : ""}`}
          keywords={getDynamicKeywords.negative}
        />
      </div>
      
      {/* 속성별 감성 분포 차트 - 충분한 여백 추가 */}
      <div className="pt-12 pb-8">
        <AttributeSentimentChart />
      </div>
    </div>
  );
};

export default SentimentTab;
