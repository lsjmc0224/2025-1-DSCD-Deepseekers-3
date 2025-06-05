
import React, { ReactNode } from 'react';
import { 
  Sidebar, 
  SidebarContent, 
  SidebarTrigger, 
  SidebarMenu, 
  SidebarMenuItem, 
  SidebarMenuButton,
  useSidebar
} from "@/components/ui/sidebar";
import { cn } from "@/lib/utils";
import Header from './Header';
import { BarChart3, MessagesSquare, Smile, Video, ChevronLeft, ChevronRight } from 'lucide-react';
import { useLocation, Link } from "react-router-dom";

interface DashboardLayoutProps {
  children: ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const location = useLocation();
  const path = location.pathname;
  const { state } = useSidebar();
  const isCollapsed = state === "collapsed";

  const navItems = [
    { label: '통합요약', icon: BarChart3, path: '/summary' },
    { label: '감성분석', icon: Smile, path: '/sentiment' },
    { label: '댓글 분석기', icon: MessagesSquare, path: '/comments' },
    { label: '영상모니터링', icon: Video, path: '/videos' },
  ];

  const getNavCls = (itemPath: string) => {
    const isActive = path === itemPath;
    return isActive ? "bg-primary/10 text-primary font-medium" : "hover:bg-primary/5";
  };

  return (
    <div className={cn(
      "min-h-screen flex w-full bg-secondary/20",
      isCollapsed ? "sidebar-collapsed" : "sidebar-expanded"
    )}>
      <Sidebar 
        className={cn(
          "hidden md:block border-r sidebar-transition",
          isCollapsed ? "w-16" : "w-64"
        )}
        collapsible="icon"
      >
        <SidebarContent className="py-4 flex flex-col h-full">
          <div className={cn(
            "transition-all duration-300 px-4 mb-6 relative",
            isCollapsed ? "flex justify-center" : "flex items-center"
          )}>
            {!isCollapsed && (
              <img 
                src="/snatch-logo.png" 
                alt="SNATCH Logo" 
                className="h-7 object-contain" 
              />
            )}
            
            <SidebarTrigger 
              className={cn(
                "h-8 w-8 rounded-full flex items-center justify-center transition-all duration-200 hover:bg-primary/10",
                isCollapsed ? "mx-auto" : "absolute right-3 top-0"
              )}
            >
              {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
            </SidebarTrigger>
          </div>
          
          <SidebarMenu className={cn(
            "transition-all duration-300",
            isCollapsed ? "px-0 space-y-5 flex flex-col items-center pt-4" : "px-3 space-y-2"
          )}>
            {navItems.map((item) => (
              <SidebarMenuItem key={item.label} className={isCollapsed ? "flex justify-center w-full" : ""}>
                <SidebarMenuButton
                  asChild
                  isActive={path === item.path}
                  tooltip={item.label}
                  className={isCollapsed ? "flex justify-center" : ""}
                >
                  <Link 
                    to={item.path} 
                    className={cn(
                      "flex items-center px-3 py-2 rounded-md text-sm font-medium transition-all duration-200",
                      getNavCls(item.path),
                      isCollapsed ? "justify-center mx-auto" : ""
                    )}
                  >
                    <item.icon className={cn("h-5 w-5 flex-shrink-0")} />
                    {!isCollapsed && <span className="ml-3 truncate">{item.label}</span>}
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarContent>
      </Sidebar>

      <div className="flex flex-col flex-1 overflow-hidden content-transition">
        <Header />
        <main className="flex-1 overflow-y-auto p-6 main-content">
          <div className="dashboard-content">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
