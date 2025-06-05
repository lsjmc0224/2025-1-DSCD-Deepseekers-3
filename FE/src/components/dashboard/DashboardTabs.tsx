
import React, { useState } from 'react';
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import SummaryTab from './tabs/SummaryTab';
import SentimentTab from './tabs/SentimentTab';
import CommentsTab from './tabs/CommentsTab';
import VideosTab from './tabs/VideosTab';
import DashboardFilters from './DashboardFilters';

interface DateRange {
  from: Date;
  to?: Date;
}

const DashboardTabs: React.FC = () => {
  const [activeTab, setActiveTab] = useState("summary");
  const [selectedChannel, setSelectedChannel] = useState("전체");
  const [selectedPeriod, setSelectedPeriod] = useState("최근 7일");
  const [selectedDateRange, setSelectedDateRange] = useState<DateRange>({
    from: new Date(new Date().setDate(new Date().getDate() - 7)),
    to: new Date()
  });
  
  const handleTabChange = (value: string) => {
    setActiveTab(value);
  };
  
  const handleChannelChange = (channel: string) => {
    setSelectedChannel(channel);
  };
  
  const handlePeriodChange = (period: string) => {
    setSelectedPeriod(period);
  };
  
  const handleDateChange = (dateRange: DateRange) => {
    setSelectedDateRange(dateRange);
  };
  
  return (
    <div className="space-y-4">
      <DashboardFilters 
        onChannelChange={handleChannelChange}
        onPeriodChange={handlePeriodChange}
        onDateChange={handleDateChange}
      />
      
      <Tabs defaultValue="summary" value={activeTab} onValueChange={handleTabChange}>
        <div className="flex justify-between items-center">
          <TabsList className="grid grid-cols-4 w-fit">
            <TabsTrigger value="summary" className="px-6">통합요약</TabsTrigger>
            <TabsTrigger value="sentiment" className="px-6">감성분석</TabsTrigger>
            <TabsTrigger value="comments" className="px-6">댓글 분석기</TabsTrigger>
            <TabsTrigger value="videos" className="px-6">영상모니터링</TabsTrigger>
          </TabsList>
          
          <Button size="sm" variant="outline" className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            <span>보고서 다운로드</span>
          </Button>
        </div>
        
        <div className="mt-6 relative">
          <TabsContent 
            value="summary" 
            className={`tab-transition ${activeTab === "summary" ? "tab-active" : "tab-inactive"}`}
          >
            <SummaryTab 
              channel={selectedChannel} 
              period={selectedPeriod} 
              dateRange={selectedDateRange} 
            />
          </TabsContent>
          
          <TabsContent 
            value="sentiment" 
            className={`tab-transition ${activeTab === "sentiment" ? "tab-active" : "tab-inactive"}`}
          >
            <SentimentTab 
              channel={selectedChannel} 
              period={selectedPeriod} 
              dateRange={selectedDateRange} 
            />
          </TabsContent>
          
          <TabsContent 
            value="comments" 
            className={`tab-transition ${activeTab === "comments" ? "tab-active" : "tab-inactive"}`}
          >
            <CommentsTab 
              channel={selectedChannel} 
              period={selectedPeriod} 
              dateRange={selectedDateRange} 
            />
          </TabsContent>
          
          <TabsContent 
            value="videos" 
            className={`tab-transition ${activeTab === "videos" ? "tab-active" : "tab-inactive"}`}
          >
            <VideosTab 
              channel={selectedChannel} 
              period={selectedPeriod} 
              dateRange={selectedDateRange} 
            />
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
};

export default DashboardTabs;
