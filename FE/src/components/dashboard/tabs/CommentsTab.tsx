import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
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
import { Loader2 } from 'lucide-react';

interface DateRange {
  from: Date;
  to?: Date;
}

interface CommentsTabProps {
  channel: string;
  period: string;
  dateRange: DateRange;
}

export interface Comment {
  id: string;
  text: string;
  date: Date;
  sentiment: 'positive' | 'negative' | 'neutral';
  source: string;
  likes: number | null;
  attributes: string[];
  analysis: {
    sentiment_score: number;
    aspect: string;
  };
}

const dummyComments: Comment[] = [
  {
    id: 'comment-1',
    text: '이 편의점 과자 너무 맛있어요!',
    date: new Date('2025-10-01'),
    sentiment: 'positive',
    source: '유튜브',
    likes: 12,
    attributes: ['맛'],
    analysis: {
      sentiment_score: 0.85,
      aspect: '맛',
    },
  },
  {
    id: 'comment-2',
    text: '가격 대비 별로네요...',
    date: new Date('2025-10-03'),
    sentiment: 'negative',
    source: '커뮤니티',
    likes: null,
    attributes: ['가격'],
    analysis: {
      sentiment_score: -0.7,
      aspect: '가격',
    },
  },
  {
    id: 'comment-3',
    text: '식감은 괜찮았지만 맛은 별로였어요.',
    date: new Date('2025-10-05'),
    sentiment: 'neutral',
    source: '틱톡',
    likes: 6,
    attributes: ['식감', '맛'],
    analysis: {
      sentiment_score: 0.1,
      aspect: '식감',
    },
  },
];


const snackAttributes = ["맛", "식감", "기타", "가격", "주관적 평가"];

const CommentsTab: React.FC<CommentsTabProps> = ({ channel, period, dateRange }) => {
  const { keyword } = useParams<{ keyword: string }>();
  const [allComments, setAllComments] = useState<Comment[]>([]);
  const [filteredComments, setFilteredComments] = useState<Comment[]>([]);
  const [selectedComment, setSelectedComment] = useState<Comment | null>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const [sourceFilter, setSourceFilter] = useState<string>("all");
  const [sentimentFilter, setSentimentFilter] = useState<string>("all");
  const [attributeFilter, setAttributeFilter] = useState<string>("all");
  const [sortOption, setSortOption] = useState<string>("latest");

  // ✅ API 요청
  useEffect(() => {
    if (!keyword) return;

    const fetchComments = async () => {
      try {
        setLoading(true);
        const response = await axios.get("http://localhost:8000/api/comments", {
          params: {
            from: dateRange.from.toISOString().split("T")[0],
            to: dateRange.to?.toISOString().split("T")[0],
            keyword: keyword
          }
        });

        const parsed = response.data.map((item: any) => ({
          ...item,
          date: new Date(item.date)
        }));

        setAllComments(parsed);
      } catch (error) {
        console.error("댓글 데이터 불러오기 실패:", error);

        // ✅ 더미 데이터 삽입
        setAllComments(dummyComments);
      } finally {
        setLoading(false);
      }
    };

    fetchComments();
  }, [dateRange, keyword]);

  // ✅ 필터링 & 정렬
  useEffect(() => {
    let result = [...allComments];

    if (channel !== "전체") {
      result = result.filter(comment => comment.source === channel);
    }

    if (sourceFilter !== "all") {
      result = result.filter(comment => comment.source === sourceFilter);
    }

    if (sentimentFilter !== "all") {
      result = result.filter(comment => comment.sentiment === sentimentFilter);
    }

    if (attributeFilter !== "all") {
      result = result.filter(comment => comment.attributes.includes(attributeFilter));
    }

    switch (sortOption) {
      case "likesHigh":
        result.sort((a, b) => (b.likes ?? 0) - (a.likes ?? 0));
        break;
      case "likesLow":
        result.sort((a, b) => (a.likes ?? 0) - (b.likes ?? 0));
        break;
      case "latest":
        result.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
        break;
      case "oldest":
        result.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
        break;
    }

    setFilteredComments(result);
  }, [allComments, channel, sourceFilter, sentimentFilter, attributeFilter, sortOption]);

  const handleViewDetails = (id: string) => {
    const comment = allComments.find(c => c.id === id);
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

      {loading ? (
        <div className="w-full flex justify-center items-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <CommentsTable
          comments={filteredComments}
          onViewDetails={handleViewDetails}
        />
      )}

      <CommentDetails
        comment={selectedComment}
        open={isDetailsOpen}
        onClose={handleCloseDetails}
      />
    </div>
  );
};

export default CommentsTab;
