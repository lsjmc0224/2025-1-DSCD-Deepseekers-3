export const parseLikesFilter = (filter: string): number => {
  const match = filter.match(/(\d+)%/);
  return match ? parseInt(match[1]) : 10; // 기본값 10%
};