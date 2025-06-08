import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const Home = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = () => {
    if (searchQuery.trim()) {
      const encodedKeyword = encodeURIComponent(searchQuery.trim());
      navigate(`/summary/${encodedKeyword}`);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="w-screen min-h-screen bg-gradient-to-br from-purple-200 via-blue-200 to-white flex justify-center items-center">
      <div className="w-full max-w-2xl px-6">
        <div className="flex flex-col items-center space-y-8">
          {/* 로고 섹션 */}
          <div className="flex justify-center">
            <img 
              src="/snatch-logo.png" 
              alt="SNATCH Logo" 
              className="w-[200px] h-auto"
            />
          </div>

          {/* 검색창 섹션 */}
          <div className="flex gap-4 w-full">
            <Input
              type="text"
              placeholder="검색어를 입력하세요"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-1 h-12 text-base bg-white/90 backdrop-blur-sm border-white/50 focus:border-blue-400 focus:ring-blue-400/20"
            />
            <Button
              onClick={handleSearch}
              className="h-12 px-6 bg-blue-500 hover:bg-blue-600 text-white font-medium transition-colors duration-200"
            >
              SEARCH
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
