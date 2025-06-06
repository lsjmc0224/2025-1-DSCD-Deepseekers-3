// dummySentimentData.ts

export const dummyOverviewData = {
  summary: "밤티라미수는 전반적으로 맛있다는 평가가 많았으며, 가격에 대한 의견은 엇갈렸습니다. 일부 사용자는 식감이 독특하다고 표현했습니다.",
  positive_keywords: ["달콤함", "부드러움", "풍미", "맛", "디저트"],
  negative_keywords: ["비쌈", "느끼함", "질림", "가성비", "양"],
  attribute_sentiment: [
    { name: "맛", 긍정: 7, 부정: 1, 중립: 1 },
    { name: "식감", 긍정: 5, 부정: 2, 중립: 2 },
    { name: "가격", 긍정: 3, 부정: 4, 중립: 2 },
    { name: "주관적 평가", 긍정: 8, 부정: 1, 중립: 2 },
    { name: "기타", 긍정: 4, 부정: 2, 중립: 3 }
  ]
};

export const dummyDetailsData = {
  positive: {
    summary: "대체로 맛있고 만족스럽다는 반응이 많습니다. 특히 달콤한 맛과 부드러운 식감이 인상적이라는 평이 주를 이룹니다.",
    comments: [
      {
        id: "comment-1",
        text: "밤티라미수 진짜 부드럽고 달달해서 너무 맛있어요!",
        date: new Date("2025-10-12T14:00:00"),
        sentiment: "positive",
        source: "유튜브",
        likes: 15,
      },
      {
        id: "comment-2",
        text: "진한 커피향이 살아있네요. 단 거 좋아하면 강추!",
        date: new Date("2025-10-10T09:20:00"),
        sentiment: "positive",
        source: "커뮤니티",
        likes: 8,
      }
    ]
  },
  negative: {
    summary: "맛은 있지만 너무 달고 느끼하다는 반응도 일부 있었습니다. 가격이 비싸다는 의견이 자주 등장합니다.",
    comments: [
      {
        id: "comment-3",
        text: "솔직히 비싸고 생각보다 별로였음. 한 번 먹고 안 살 듯.",
        date: new Date("2025-10-13T18:45:00"),
        sentiment: "negative",
        source: "틱톡",
        likes: 4,
      },
      {
        id: "comment-4",
        text: "좀 느끼해서 반도 못 먹었어요. 제 입맛엔 안 맞네요.",
        date: new Date("2025-10-11T12:00:00"),
        sentiment: "negative",
        source: "커뮤니티",
        likes: 3,
      }
    ]
  }
};
