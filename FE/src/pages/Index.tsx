import React, { useState } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import DashboardLayout from '../components/layout/DashboardLayout';
import SummaryTab from '../components/dashboard/tabs/SummaryTab';
import SentimentTab from '../components/dashboard/tabs/SentimentTab';
import CommentsTab from '../components/dashboard/tabs/CommentsTab';
import VideosTab from '../components/dashboard/tabs/VideosTab';
import DashboardFilters from '../components/dashboard/DashboardFilters';

interface DateRange {
  from: Date;
  to?: Date;
}

const Index = () => {
  const location = useLocation();
  const { keyword } = useParams<{ keyword: string }>(); // ← URL 파라미터에서 키워드 가져오기

  const [selectedChannel, setSelectedChannel] = useState("전체");
  const [selectedPeriod, setSelectedPeriod] = useState("최근 7일");
  const [selectedDateRange, setSelectedDateRange] = useState<DateRange>({
    from: new Date(new Date().setDate(new Date().getDate() - 7)),
    to: new Date()
  });

  const handleChannelChange = (channel: string) => {
    setSelectedChannel(channel);
  };
  
  const handlePeriodChange = (period: string) => {
    setSelectedPeriod(period);
  };
  
  const handleDateChange = (dateRange: DateRange) => {
    setSelectedDateRange(dateRange);
  };

  // 현재 경로에 따라 탭 판별
  const currentPath = location.pathname;
  const isSummary = currentPath.startsWith('/summary');
  const isSentiment = currentPath.startsWith('/sentiment');
  const isComments = currentPath.startsWith('/comments');
  const isVideos = currentPath.startsWith('/videos');

  // '영상' 탭에서는 채널 필터 숨김
  const showChannelFilter = !isVideos;

  const renderTabContent = () => {
    if (!keyword) {
      return <div className="text-center text-gray-500">검색 키워드가 없습니다.</div>;
    }

    if (isSummary) {
      return <SummaryTab keyword={keyword} channel={selectedChannel} period={selectedPeriod} dateRange={selectedDateRange} />;
    } else if (isSentiment) {
      return <SentimentTab keyword={keyword} channel={selectedChannel} period={selectedPeriod} dateRange={selectedDateRange} />;
    } else if (isComments) {
      return <CommentsTab keyword={keyword} channel={selectedChannel} period={selectedPeriod} dateRange={selectedDateRange} />;
    } else if (isVideos) {
      return <VideosTab keyword={keyword} channel={selectedChannel} period={selectedPeriod} dateRange={selectedDateRange} />;
    } else {
      return <SummaryTab keyword={keyword} channel={selectedChannel} period={selectedPeriod} dateRange={selectedDateRange} />;
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-4">
        <DashboardFilters 
          onChannelChange={handleChannelChange}
          onPeriodChange={handlePeriodChange}
          onDateChange={handleDateChange}
          showChannelFilter={showChannelFilter}
        />
        <div>
          {renderTabContent()}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Index;
