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

// 2024년 10월 1일~31일 사이 랜덤 날짜 생성 함수
function getRandomOctoberDate() {
  const start = new Date(2024, 9, 1).getTime();
  const end = new Date(2024, 9, 31, 23, 59, 59).getTime();
  return new Date(start + Math.floor(Math.random() * (end - start)));
}

// 실제 데이터 기반 더미 댓글 100개 (content_analysis.csv, instiz_posts.csv, youtube_comments.csv 활용)
const realCommentsData = [
  {
    id: 'comment-393',
    text: 'CU 밤티라미수 맛있어?3 CU 밤티라미수 맛있어?',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-394',
    text: '애초에 달달한 디저트인데ㅋㅋ성공해서 기분좋게 올렸는데 꼭 사회성 결여된것마냥 초치는것들은 왜그러는걸ㄲㅏ 난 걍 부러워죽겠는데..!',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['달달'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '달달' }
  },
  {
    id: 'comment-395',
    text: '긍데 밤티라미수 ㄹㅇ 구하기 어려워?4 나 걍 11시에 시간 맞춰 들어가서 얼떨결에 세개 샀는데 편의점 디저트 만오천원 주고 사려니 뭔가 아까워서 ㅎㅎ..',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['편의점'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '편의점' }
  },
  {
    id: 'comment-396',
    text: '밤티라미수 맛있어??',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-397',
    text: '4 회사주변에 몇개 있길래 하나 사서 냉장고에 넣어뒀는데맛있었으면 좋겠다!',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-398',
    text: '씨유 편순이 살려...',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '씨유' }
  },
  {
    id: 'comment-399',
    text: '밤티라미수 마싯당1 달고 맛없다는 후기만 봐서 괜히 샀나 싶었는데 맛있음ㅋㅋ',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-400',
    text: '9 카페 가면 6-7천원대로 팔만한 케이크 맛임 이정도면 가성비 굿생각보다 더 티라미수 맛이 강해서 커피도 사올 걸 후회중...그냥 먹으면 크림이 많아서 좀 물려',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛임'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛임' }
  },
  {
    id: 'comment-401',
    text: 'Cu 밤티라미수 후기 ...11 1. 밤 맛이 거의 안 난다 ...?',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['Cu'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: 'Cu' }
  },
];

const mockCommentsData = realCommentsData;

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
