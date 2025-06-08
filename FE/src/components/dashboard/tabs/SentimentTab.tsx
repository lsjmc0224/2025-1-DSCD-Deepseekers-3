import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Bot, Smile, Frown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { dummyOverviewData, dummyDetailsData } from './dummySentimentData';
import { parseLikesFilter } from "@/utils/parseLikesFilter"; // 유틸로 분리 권장
import { useParams } from "react-router-dom";
import { Skeleton } from "@/components/ui/skeleton";

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
  const { keyword } = useParams<{ keyword: string }>(); // ✅ URL에서 product(keyword) 추출

  const [overviewData, setOverviewData] = useState<any>(null);
  const [detailsData, setDetailsData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [detailsError, setDetailsError] = useState<string | null>(null);
  const [positiveLikesFilter, setPositiveLikesFilter] = useState("좋아요 상위 10%");
  const [negativeLikesFilter, setNegativeLikesFilter] = useState("좋아요 상위 10%");

  const fetchSentimentOverview = async ({
    product,
    from,
    to,
  }: {
    product: string;
    from: string;
    to: string;
  }) => {
    try {
      const params = new URLSearchParams({ product, from, to });
      const res = await fetch(`http://localhost:8000/sentiment/overview?${params}`);
      if (!res.ok) throw new Error("Failed to fetch overview");
      return await res.json();
    } catch (e) {
      console.error("Overview API 실패, fallback 사용");
      return dummyOverviewData;
    }
  };

  const fetchSentimentDetails = async ({
    product,
    from,
    to,
    top = 10,
  }: {
    product: string;
    from: string;
    to: string;
    top?: number;
  }) => {
    try {
      const params = new URLSearchParams({ product, from, to, top: top.toString() });
      const res = await fetch(`http://localhost:8000/sentiment/details?${params}`);

      if (!res.ok) {
        const errorBody = await res.json();
        const detail = errorBody?.detail || "알 수 없는 오류가 발생했습니다.";

        if (res.status === 404) {
          throw new Error("등록된 키워드가 아닙니다.");
        }
        if (res.status === 400) {
          throw new Error("해당 기간에는 좋아요 수가 집계된 콘텐츠가 없습니다.");
        }

        throw new Error(detail);
      }

      return await res.json();
    } catch (e: any) {
      console.error("Details API 실패", e.message);
      // 사용자 친화적 오류 메시지 표시를 위해 throw 유지
      throw e;
    }
  };


  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setDetailsError(null);

      const product = keyword || "전체";
      const from = dateRange.from.toISOString().split("T")[0];
      const to = (dateRange.to ?? dateRange.from).toISOString().split("T")[0];
      const top = Math.max(
        parseLikesFilter(positiveLikesFilter),
        parseLikesFilter(negativeLikesFilter)
      );

      try {
        const overview = await fetchSentimentOverview({ product, from, to });
        setOverviewData(overview);
      } catch (e) {
        console.error("Overview 실패");
        // 전체 실패 시 fallback 가능
      }

      try {
        const details = await fetchSentimentDetails({ product, from, to, top });
        setDetailsData(details);
      } catch (e: any) {
        setDetailsError(e.message || "상세 감성 데이터를 불러오는 중 오류가 발생했습니다.");
      }

      setLoading(false);
    };

    loadData();
  }, [channel, period, dateRange, positiveLikesFilter, negativeLikesFilter]);

  const handlePositiveLikesFilterChange = (val: string) => setPositiveLikesFilter(val);
  const handleNegativeLikesFilterChange = (val: string) => setNegativeLikesFilter(val);


  if (loading) {
    return (
      <div className="space-y-8">
        {/* AI 분석 요약 스켈레톤 */}
        <Card>
          <CardHeader className="flex items-start gap-3">
            <Skeleton className="h-6 w-6 rounded-full mt-1" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-40" />
              <Skeleton className="h-3 w-56" />
            </div>
          </CardHeader>
          <CardContent>
            <Skeleton className="h-24 w-full rounded-md" />
          </CardContent>
        </Card>

        {/* 감성 분석 스켈레톤 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[...Array(2)].map((_, i) => (
            <Card key={i}>
              <CardHeader className="flex gap-3">
                <Skeleton className="h-6 w-6 rounded-full mt-1" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-3 w-48" />
                </div>
                <Skeleton className="h-8 w-36 rounded-md" />
              </CardHeader>
              <CardContent className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-5/6" />
                <Skeleton className="h-4 w-4/6" />
              </CardContent>
            </Card>
          ))}
        </div>

        {/* 키워드 요약 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
          {[...Array(2)].map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-4 w-32 mb-2" />
                <Skeleton className="h-3 w-48" />
              </CardHeader>
              <CardContent className="flex flex-wrap gap-2">
                {[...Array(6)].map((_, j) => (
                  <Skeleton key={j} className="h-6 w-16 rounded-full" />
                ))}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* 속성 차트 */}
        <div className="pt-12 pb-8">
          <Skeleton className="h-[240px] w-full rounded-md" />
        </div>
      </div>
    );
  }
  
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
        {detailsError || !detailsData ? (
          <div className="col-span-2 text-center text-sm text-muted-foreground border border-dashed rounded-md p-8">
            ⚠️ 감성 분석 상세 데이터를 불러오는 데 실패했습니다.
            <br />
            <span className="text-red-500">{detailsError ?? "데이터를 불러올 수 없습니다."}</span>
          </div>
        ) : (
          <>
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
          </>
        )}
      </div>

      {/* 키워드 요약 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
        <SentimentKeywordsSummary
          title="긍정 키워드"
          description="긍정적인 평가에서 자주 등장한 키워드"
          keywords={overviewData.positive_keywords}
        />
        <SentimentKeywordsSummary
          title="부정 키워드"
          description="부정적인 평가에서 자주 등장한 키워드"
          keywords={overviewData.negative_keywords}
        />
      </div>

      {/* 속성 기반 감성 분포 */}
      <div className="pt-12 pb-8">
        <AttributeSentimentChart data={overviewData.attribute_sentiment ?? []} />
      </div>
    </div>
  );
};

export default SentimentTab;
