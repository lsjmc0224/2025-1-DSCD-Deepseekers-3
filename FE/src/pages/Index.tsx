
import React from 'react';
import { useLocation } from 'react-router-dom';
import DashboardLayout from '../components/layout/DashboardLayout';
import SummaryTab from '../components/dashboard/tabs/SummaryTab';
import SentimentTab from '../components/dashboard/tabs/SentimentTab';
import CommentsTab from '../components/dashboard/tabs/CommentsTab';
import VideosTab from '../components/dashboard/tabs/VideosTab';
import DashboardFilters from '../components/dashboard/DashboardFilters';
import { useState } from 'react';

interface DateRange {
  from: Date;
  to?: Date;
}

const Index = () => {
  const location = useLocation();
  const currentPath = location.pathname;

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

  // Do not show channel filter on videos tab
  const showChannelFilter = currentPath !== '/videos';

  const renderTabContent = () => {
    switch (currentPath) {
      case '/summary':
        return <SummaryTab 
          channel={selectedChannel}
          period={selectedPeriod}
          dateRange={selectedDateRange}
        />;
      case '/sentiment':
        return <SentimentTab 
          channel={selectedChannel}
          period={selectedPeriod}
          dateRange={selectedDateRange}
        />;
      case '/comments':
        return <CommentsTab 
          channel={selectedChannel}
          period={selectedPeriod}
          dateRange={selectedDateRange}
        />;
      case '/videos':
        return <VideosTab 
          channel={selectedChannel}
          period={selectedPeriod}
          dateRange={selectedDateRange}
        />;
      default:
        return <SummaryTab 
          channel={selectedChannel}
          period={selectedPeriod}
          dateRange={selectedDateRange}
        />;
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
