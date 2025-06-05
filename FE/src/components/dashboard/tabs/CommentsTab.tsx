
import React, { useState, useEffect } from 'react';
import CommentsTable from '../CommentsTable';
import CommentDetails from '../CommentDetails';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { 
  Card, 
  CardContent
} from "@/components/ui/card";

interface DateRange {
  from: Date;
  to?: Date;
}

interface CommentsTabProps {
  channel: string;
  period: string;
  dateRange: DateRange;
}

// 밤 티라미수 관련 댓글 데이터 - 정제된 버전
const snackComments = {
  positive: [
    "밤 티라미수 먹어봤는데 진짜 크림이 부드럽고 맛있어요!",
    "밤 맛이 은은해서 너무 달지 않아 좋네요. 완벽한 달콤함이에요.",
    "크림이 정말 부드럽고 밤 맛이 진해요. 디저트로 딱!",
    "밤 티라미수의 촉촉한 식감이 정말 좋아요. 다음에도 꼭 구매할 거예요.",
    "디저트로 먹기에 완벽해요. 밤향이 은은해서 좋네요.",
    "크림과 밤의 조화가 환상적이에요. 친구들에게도 추천하고 싶은 맛이에요!"
  ],
  negative: [
    "가격 대비 양이 너무 적어요. 이 가격이면 좀 더 푸짐했으면 좋겠어요.",
    "너무 달아서 몇 입 먹고 질려서 못 먹겠어요.",
    "인공적인 밤 맛이 좀 아쉬워요. 자연스러운 밤 맛이 아니에요.",
    "가격에 비해 양이 좀 적은 느낌이에요. 실망스러웠습니다.",
    "유통기한이 짧아서 빨리 먹어야 해요. 신선도 유지가 어렵네요.",
    "밤 티라미수가 너무 느끼고 단맛만 강해요. 밤의 고소함이 안 느껴져요."
  ],
  neutral: [
    "밤 티라미수는 달콤하지만 가격이 좀 있는 편이에요.",
    "크림은 부드럽지만 밤 맛은 약간 인공적인 느낌도 있네요.",
    "디저트로는 괜찮은데 유통기한이 짧아서 빨리 먹어야 해요.",
    "일반 티라미수보다는 특별하지만 가격 대비 만족도는 보통이에요.",
    "밤 향이 은은하게 나고 단맛은 적당해요. 개인 취향에 따라 호불호가 갈릴 것 같네요."
  ]
};

// 수정된 속성 목록 - 요청에 따라 고정
const snackAttributes = ["맛", "식감", "가격", "주관적 평가", "기타"];

// 속성별 매칭 키워드 정의
const attributeKeywords = {
  "맛": ["달콤", "맛있", "단맛", "고소", "인공적인 맛", "밤 맛", "밤향", "달지 않", "진해요"],
  "식감": ["부드럽", "촉촉", "질감", "크림", "폭신", "식감"],
  "가격": ["가격", "비싸", "저렴", "가성비", "양이", "푸짐"],
  "주관적 평가": ["좋네요", "좋아요", "추천", "만족", "실망", "아쉬워", "호불호", "완벽"],
  "기타": ["유통기한", "신선도", "포장"]
};

// 목업 댓글 데이터 - 감성과 내용, 속성 정합성 보장
const generateMockComments = (count: number) => {
  const sourceOptions = ["유튜브", "커뮤니티", "틱톡"] as const;
  const sentimentOptions = ["positive", "negative", "neutral"] as const;
  
  return Array.from({ length: count }, (_, i) => {
    // 먼저 감성 유형 결정
    const sentiment = sentimentOptions[Math.floor(Math.random() * sentimentOptions.length)];
    
    // 감성 유형에 맞는 댓글 선택
    let text = "";
    if (sentiment === "positive") {
      text = snackComments.positive[Math.floor(Math.random() * snackComments.positive.length)];
    } else if (sentiment === "negative") {
      text = snackComments.negative[Math.floor(Math.random() * snackComments.negative.length)];
    } else {
      text = snackComments.neutral[Math.floor(Math.random() * snackComments.neutral.length)];
    }
    
    const source = sourceOptions[Math.floor(Math.random() * sourceOptions.length)];
    
    // 내용에 맞는 속성 선택 (텍스트 분석 기반)
    const attributes = [];
    let hasMatchingAttribute = false;
    
    // 각 속성별 키워드를 확인하여 댓글 내용에 맞는 속성 할당
    for (const [attr, keywords] of Object.entries(attributeKeywords)) {
      if (keywords.some(keyword => text.includes(keyword))) {
        attributes.push(attr);
        hasMatchingAttribute = true;
        // 속성은 최대 2개까지만 부여
        if (attributes.length >= 2) break;
      }
    }
    
    // 매칭되는 속성이 없으면 '기타' 추가
    if (!hasMatchingAttribute) {
      attributes.push("기타");
    }
    
    // 날짜 랜덤 생성 (최근 30일 이내)
    const date = new Date();
    date.setDate(date.getDate() - Math.floor(Math.random() * 30));
    
    // 감성에 맞는 좋아요 수 설정
    let likes = 0;
    if (sentiment === "positive") {
      likes = Math.floor(Math.random() * 50) + 50; // 50~99
    } else if (sentiment === "negative") {
      likes = Math.floor(Math.random() * 30) + 5; // 5~34
    } else {
      likes = Math.floor(Math.random() * 40) + 20; // 20~59
    }
    
    // 댓글 내용에 맞는 키워드 선택
    const keywordPool = [];
    
    // 속성에 맞는 키워드 추가
    attributes.forEach(attr => {
      if (attributeKeywords[attr]) {
        const matchingKeywords = attributeKeywords[attr].filter(keyword => text.includes(keyword));
        if (matchingKeywords.length > 0) {
          keywordPool.push(...matchingKeywords.slice(0, 2)); // 최대 2개까지 추가
        }
      }
    });
    
    // 키워드가 없으면 기본값 추가
    if (keywordPool.length === 0) {
      keywordPool.push(sentiment === "positive" ? "긍정적" : 
                      sentiment === "negative" ? "부정적" : "중립적");
    }
    
    return {
      id: `comment-${i + 1}`,
      text,
      date,
      sentiment,
      source,
      attributes,
      likes,
      analysis: {
        sentiment_score: sentiment === "positive" ? Math.random() * 0.3 + 0.7 : // 0.7-1.0 for positive
                      sentiment === "negative" ? Math.random() * 0.3 : // 0.0-0.3 for negative
                      Math.random() * 0.4 + 0.3, // 0.3-0.7 for neutral
        attributes: attributes.reduce((acc, attr) => {
          acc[attr] = {
            mentioned: true,
            sentiment: sentiment
          };
          return acc;
        }, {} as Record<string, any>),
        keywords: [...new Set(keywordPool)], // 중복 제거
        confidence: Math.random() * 0.2 + 0.8
      }
    };
  });
};

const mockCommentsData = generateMockComments(30);

const CommentsTab: React.FC<CommentsTabProps> = ({ channel, period, dateRange }) => {
  const [selectedComment, setSelectedComment] = useState<any>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [mockComments, setMockComments] = useState(mockCommentsData);
  const [filteredComments, setFilteredComments] = useState(mockCommentsData);

  // 필터링 상태
  const [sourceFilter, setSourceFilter] = useState<string>("all");
  const [sentimentFilter, setSentimentFilter] = useState<string>("all");
  const [attributeFilter, setAttributeFilter] = useState<string>("all");
  const [sortOption, setSortOption] = useState<string>("latest");

  // 채널 변경시 필터링
  useEffect(() => {
    let filteredData = mockCommentsData;
    
    if (channel !== "전체") {
      filteredData = filteredData.filter(comment => comment.source === channel);
    }
    
    setMockComments(filteredData);
  }, [channel]);

  // 날짜 범위 필터링
  useEffect(() => {
    const filteredByDate = mockCommentsData.filter(comment => 
      comment.date >= dateRange.from && 
      (!dateRange.to || comment.date <= dateRange.to)
    );
    
    setMockComments(filteredByDate);
  }, [dateRange]);

  // 필터 변경 처리
  useEffect(() => {
    let result = mockComments;
    
    if (sourceFilter !== "all") {
      result = result.filter(comment => comment.source === sourceFilter);
    }
    
    if (sentimentFilter !== "all") {
      result = result.filter(comment => comment.sentiment === sentimentFilter);
    }
    
    if (attributeFilter !== "all") {
      result = result.filter(comment => 
        comment.attributes.includes(attributeFilter)
      );
    }
    
    // 정렬 처리
    switch (sortOption) {
      case "likesHigh":
        result = [...result].sort((a, b) => b.likes - a.likes);
        break;
      case "likesLow":
        result = [...result].sort((a, b) => a.likes - b.likes);
        break;
      case "latest":
        result = [...result].sort((a, b) => b.date.getTime() - a.date.getTime());
        break;
      case "oldest":
        result = [...result].sort((a, b) => a.date.getTime() - b.date.getTime());
        break;
      default:
        // 기본 정렬 (최신순)
        result = [...result].sort((a, b) => b.date.getTime() - a.date.getTime());
    }
    
    setFilteredComments(result);
  }, [sourceFilter, sentimentFilter, attributeFilter, sortOption, mockComments]);

  const handleViewDetails = (id: string) => {
    const comment = mockComments.find(c => c.id === id);
    if (comment) {
      setSelectedComment(comment);
      setIsDetailsOpen(true);
    }
  };
  
  const handleCloseDetails = () => {
    setIsDetailsOpen(false);
  };
  
  return (
    <div className="space-y-6">
      <Card className="shadow-sm">
        <CardContent className="p-4 space-y-4">
          <div className="flex flex-col md:flex-row gap-4 md:items-end">
            <div className="flex-1 flex gap-4 flex-wrap">
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">채널</label>
                <Select value={sourceFilter} onValueChange={setSourceFilter}>
                  <SelectTrigger className="w-[120px]">
                    <SelectValue placeholder="채널 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">전체</SelectItem>
                    <SelectItem value="유튜브">유튜브</SelectItem>
                    <SelectItem value="커뮤니티">커뮤니티</SelectItem>
                    <SelectItem value="틱톡">틱톡</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">감정</label>
                <Select value={sentimentFilter} onValueChange={setSentimentFilter}>
                  <SelectTrigger className="w-[120px]">
                    <SelectValue placeholder="감정 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">전체</SelectItem>
                    <SelectItem value="positive">긍정</SelectItem>
                    <SelectItem value="negative">부정</SelectItem>
                    <SelectItem value="neutral">중립</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">속성</label>
                <Select value={attributeFilter} onValueChange={setAttributeFilter}>
                  <SelectTrigger className="w-[150px]">
                    <SelectValue placeholder="속성 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">전체</SelectItem>
                    {snackAttributes.map((attr, index) => (
                      <SelectItem key={index} value={attr}>{attr}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">정렬</label>
                <Select value={sortOption} onValueChange={setSortOption}>
                  <SelectTrigger className="w-[150px]">
                    <SelectValue placeholder="정렬 기준" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="latest">최신 날짜 순</SelectItem>
                    <SelectItem value="oldest">오래된 날짜 순</SelectItem>
                    <SelectItem value="likesHigh">좋아요 많은 순</SelectItem>
                    <SelectItem value="likesLow">좋아요 적은 순</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <CommentsTable 
        comments={filteredComments} 
        onViewDetails={handleViewDetails} 
      />
      
      <CommentDetails 
        comment={selectedComment}
        open={isDetailsOpen}
        onClose={handleCloseDetails}
      />
    </div>
  );
};

export default CommentsTab;
