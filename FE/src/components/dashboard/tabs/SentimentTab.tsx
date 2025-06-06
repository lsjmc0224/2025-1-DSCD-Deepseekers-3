import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Bot, Smile, Frown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { dummyOverviewData, dummyDetailsData } from './dummySentimentData';

import CommentsList from '../CommentsList';
import SentimentKeywordsSummary from '../SentimentKeywordsSummary';
import AttributeSentimentChart from '../charts/AttributeSentimentChart';

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
  const [overviewData, setOverviewData] = useState<any>(null);
  const [detailsData, setDetailsData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [positiveLikesFilter, setPositiveLikesFilter] = useState("좋아요 상위 10%");
  const [negativeLikesFilter, setNegativeLikesFilter] = useState("좋아요 상위 10%");

  const fetchSentimentOverview = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/sentiment/overview?...`);
      if (!res.ok) throw new Error("Failed to fetch overview");
      return await res.json();
    } catch (e) {
      console.error("Overview API 실패, fallback 사용");
      return dummyOverviewData;
    }
  };

  const fetchSentimentDetails = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/sentiment/details?...`);
      if (!res.ok) throw new Error("Failed to fetch details");
      return await res.json();
    } catch (e) {
      console.error("Details API 실패, fallback 사용");
      return dummyDetailsData;
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      const [overview, details] = await Promise.all([
        fetchSentimentOverview(),
        fetchSentimentDetails()
      ]);
      setOverviewData(overview);
      setDetailsData(details);
      setLoading(false);
    };

    loadData();
  }, [channel, period, dateRange]);

  const handlePositiveLikesFilterChange = (val: string) => setPositiveLikesFilter(val);
  const handleNegativeLikesFilterChange = (val: string) => setNegativeLikesFilter(val);

  if (loading) return <p>로딩 중...</p>;

  return (
    <div className="space-y-8">
      {/* AI 요약 */}
      <Card>
        <CardHeader className="flex items-start gap-3">
          <Bot className="h-6 w-6 text-primary mt-1" />
          <div>
            <CardTitle>🤖 AI 분석 요약</CardTitle>
            <CardDescription>
              {channel !== "전체" ? `${channel} 기준 분석 결과` : "모든 채널 종합 분석"}
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-32 rounded-md border p-4">
            <p className="text-sm">{overviewData.summary}</p>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* 감성 분석 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 긍정 */}
        <Card className="bg-green-50 border-l-4 border-green-300">
          <CardHeader className="flex gap-3">
            <Smile className="h-6 w-6 text-green-500 mt-1" />
            <div className="flex-1">
              <CardTitle>😊 긍정 감성 분석</CardTitle>
              <CardDescription>긍정 키워드 및 댓글 요약</CardDescription>
            </div>
            <Select value={positiveLikesFilter} onValueChange={handlePositiveLikesFilterChange}>
              <SelectTrigger className="min-w-[140px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="좋아요 상위 5%">좋아요 상위 5%</SelectItem>
                <SelectItem value="좋아요 상위 10%">좋아요 상위 10%</SelectItem>
                <SelectItem value="좋아요 상위 20%">좋아요 상위 20%</SelectItem>
              </SelectContent>
            </Select>
          </CardHeader>
          <CardContent>
            <p className="text-sm mb-4">{detailsData.positive.summary}</p>
            <CommentsList title="최신 긍정 댓글" comments={detailsData.positive.comments} />
          </CardContent>
        </Card>

        {/* 부정 */}
        <Card className="bg-red-50 border-l-4 border-red-300">
          <CardHeader className="flex gap-3">
            <Frown className="h-6 w-6 text-red-500 mt-1" />
            <div className="flex-1">
              <CardTitle>🙁 부정 감성 분석</CardTitle>
              <CardDescription>부정 키워드 및 댓글 요약</CardDescription>
            </div>
            <Select value={negativeLikesFilter} onValueChange={handleNegativeLikesFilterChange}>
              <SelectTrigger className="min-w-[140px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="좋아요 상위 5%">좋아요 상위 5%</SelectItem>
                <SelectItem value="좋아요 상위 10%">좋아요 상위 10%</SelectItem>
                <SelectItem value="좋아요 상위 20%">좋아요 상위 20%</SelectItem>
              </SelectContent>
            </Select>
          </CardHeader>
          <CardContent>
            <p className="text-sm mb-4">{detailsData.negative.summary}</p>
            <CommentsList title="최신 부정 댓글" comments={detailsData.negative.comments} />
          </CardContent>
        </Card>
      </div>

      {/* 키워드 요약 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
        <SentimentKeywordsSummary title="긍정 키워드" description="긍정적인 평가에서 자주 등장한 키워드" keywords={overviewData.positive_keywords} />
        <SentimentKeywordsSummary title="부정 키워드" description="부정적인 평가에서 자주 등장한 키워드" keywords={overviewData.negative_keywords} />
      </div>

      {/* 속성 기반 감성 분포 */}
      <div className="pt-12 pb-8">
        <AttributeSentimentChart data={overviewData.attribute_sentiment ?? []} />
      </div>
    </div>
  );
};

export default SentimentTab;
