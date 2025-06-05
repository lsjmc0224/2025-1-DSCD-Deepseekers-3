import React, { useState, useEffect } from 'react';
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

interface DateRange {
  from: Date;
  to?: Date;
}

interface CommentsTabProps {
  channel: string;
  period: string;
  dateRange: DateRange;
}

// 밤 티라미수 관련 댓글 데이터 - 정제된 버전
const snackComments = {
  positive: [
    "밤 티라미수 먹어봤는데 진짜 크림이 부드럽고 맛있어요!",
    "밤 맛이 은은해서 너무 달지 않아 좋네요. 완벽한 달콤함이에요.",
    "크림이 정말 부드럽고 밤 맛이 진해요. 디저트로 딱!",
    "밤 티라미수의 촉촉한 식감이 정말 좋아요. 다음에도 꼭 구매할 거예요.",
    "디저트로 먹기에 완벽해요. 밤향이 은은해서 좋네요.",
    "크림과 밤의 조화가 환상적이에요. 친구들에게도 추천하고 싶은 맛이에요!"
  ],
  negative: [
    "가격 대비 양이 너무 적어요. 이 가격이면 좀 더 푸짐했으면 좋겠어요.",
    "너무 달아서 몇 입 먹고 질려서 못 먹겠어요.",
    "인공적인 밤 맛이 좀 아쉬워요. 자연스러운 밤 맛이 아니에요.",
    "가격에 비해 양이 좀 적은 느낌이에요. 실망스러웠습니다.",
    "유통기한이 짧아서 빨리 먹어야 해요. 신선도 유지가 어렵네요.",
    "밤 티라미수가 너무 느끼고 단맛만 강해요. 밤의 고소함이 안 느껴져요."
  ],
  neutral: [
    "밤 티라미수는 달콤하지만 가격이 좀 있는 편이에요.",
    "크림은 부드럽지만 밤 맛은 약간 인공적인 느낌도 있네요.",
    "디저트로는 괜찮은데 유통기한이 짧아서 빨리 먹어야 해요.",
    "일반 티라미수보다는 특별하지만 가격 대비 만족도는 보통이에요.",
    "밤 향이 은은하게 나고 단맛은 적당해요. 개인 취향에 따라 호불호가 갈릴 것 같네요."
  ]
};

// 수정된 속성 목록 - 요청에 따라 고정
const snackAttributes = ["맛", "식감", "가격", "주관적 평가", "기타"];

// 속성별 매칭 키워드 정의
const attributeKeywords = {
  "맛": ["달콤", "맛있", "단맛", "고소", "인공적인 맛", "밤 맛", "밤향", "달지 않", "진해요"],
  "식감": ["부드럽", "촉촉", "질감", "크림", "폭신", "식감"],
  "가격": ["가격", "비싸", "저렴", "가성비", "양이", "푸짐"],
  "주관적 평가": ["좋네요", "좋아요", "추천", "만족", "실망", "아쉬워", "호불호", "완벽"],
  "기타": ["유통기한", "신선도", "포장"]
};

// 2024년 10월 1일~31일 사이 랜덤 날짜 생성 함수
function getRandomOctoberDate() {
  const start = new Date(2024, 9, 1).getTime();
  const end = new Date(2024, 9, 31, 23, 59, 59).getTime();
  return new Date(start + Math.floor(Math.random() * (end - start)));
}

// 실제 데이터 기반 더미 댓글 100개 (content_analysis.csv, instiz_posts.csv, youtube_comments.csv 활용)
const realCommentsData = [
  {
    id: 'comment-393',
    text: 'CU 밤티라미수 맛있어?3 CU 밤티라미수 맛있어?',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-394',
    text: '애초에 달달한 디저트인데ㅋㅋ성공해서 기분좋게 올렸는데 꼭 사회성 결여된것마냥 초치는것들은 왜그러는걸ㄲㅏ 난 걍 부러워죽겠는데..!',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['달달'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '달달' }
  },
  {
    id: 'comment-395',
    text: '긍데 밤티라미수 ㄹㅇ 구하기 어려워?4 나 걍 11시에 시간 맞춰 들어가서 얼떨결에 세개 샀는데 편의점 디저트 만오천원 주고 사려니 뭔가 아까워서 ㅎㅎ..',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['편의점'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '편의점' }
  },
  {
    id: 'comment-396',
    text: '밤티라미수 맛있어??',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-397',
    text: '4 회사주변에 몇개 있길래 하나 사서 냉장고에 넣어뒀는데맛있었으면 좋겠다!',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-398',
    text: '씨유 편순이 살려...',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '씨유' }
  },
  {
    id: 'comment-399',
    text: '밤티라미수 마싯당1 달고 맛없다는 후기만 봐서 괜히 샀나 싶었는데 맛있음ㅋㅋ',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-400',
    text: '9 카페 가면 6-7천원대로 팔만한 케이크 맛임 이정도면 가성비 굿생각보다 더 티라미수 맛이 강해서 커피도 사올 걸 후회중...그냥 먹으면 크림이 많아서 좀 물려',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛임'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛임' }
  },
  {
    id: 'comment-401',
    text: 'Cu 밤티라미수 후기 ...11 1. 밤 맛이 거의 안 난다 ...?',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['Cu'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: 'Cu' }
  },
  {
    id: 'comment-402',
    text: '씨유 밤티라미수 리뉴얼 되고나서 왜 칼로리가 더 높아졌을까',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유', '리뉴얼'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '씨유' }
  },
  {
    id: 'comment-403',
    text: '밤티라미수 후기36 맛있긴 한데 또 찾아 먹을 맛은 아니지만 누가 주면 다 먹을 듯',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-404',
    text: '씨유 밤티라미수 이제 예약 잘되네???',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '씨유' }
  },
  {
    id: 'comment-405',
    text: '씨유 지금가면 밤티라미수 받을 수 있나..',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '씨유' }
  },
  {
    id: 'comment-406',
    text: '씨유앱 왜 재고없으면서 있다고 뜨냐4 밤티라미수먹겠다고 3군데 돌았는데 1이라고 떠있었으면서 없대',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '씨유' }
  },
  {
    id: 'comment-407',
    text: '다화나네 두번다시 저런거 먹겠다고 편의점 돌지 않겠어.....',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['편의점'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '편의점' }
  },
  {
    id: 'comment-408',
    text: '1 얼른 리뉴얼 한 거 내줘요...',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['리뉴얼'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '리뉴얼' }
  },
  {
    id: 'comment-409',
    text: '두입 먹고 아 이거 못먹겠다 싶어서 걍 버림 두개 살까 하다가 한개 샀는데 두개 샀으면 후회할뻔리뉴얼 돼서 나오는거 반응보고 사야지 ㅜ',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['리뉴얼'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '리뉴얼' }
  },
  {
    id: 'comment-410',
    text: '씨유 밤티라미수 먹었는데 엄..',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '씨유' }
  },
  {
    id: 'comment-411',
    text: '흑백요리사에서 나온 거라는 건 앎 그렇게 맛있음?',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-412',
    text: 'Cu 사장님한테 밤티라미수 챙겨달라는 거 오바야??',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['Cu'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: 'Cu' }
  }, 
  {
    id: 'comment-413',
    text: '씨유 알바생인데 다 포켓씨유 상품으로 빠져있더라고 ㅠㅠ',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '씨유' }
  },
  {
    id: 'comment-414',
    text: '사장님한테 1개만 포켓씨유 등록 안하고 나한테 팔라고 하면 오반가.... 애초에 포켓씨유 등록안할 수 있는지도 잘 모르겠긴 해...',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '씨유' }
  },
  {
    id: 'comment-415',
    text: '밤티라미수 티켓팅해야하는ㄱ ㄴ아 나 그냥 편의점 가면 있늘 줄 쉽지안ㄹ다',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['편의점'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '편의점' }
  },
  {
    id: 'comment-416',
    text: '밤티라미수 후기 한입 먹었을 땐 오 맛있는데?',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-417',
    text: '나두 밤티라미수 먹고 싶어 ㅠ 씨유 투어 햇다',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '씨유' }
  },
  {
    id: 'comment-418',
    text: '낼 밤티라미수 팝업 갈까 말까 고민이야2 가격이 생각보다 비싸서 ㅠ',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['팝업'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '팝업' }
  },
  {
    id: 'comment-419',
    text: '아 씨유 알바 관둬서 다행이다 밤티라미수 엄청 찾겠넼ㅋㅋㅋ',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '씨유' }
  },
  {
    id: 'comment-420',
    text: '밤티라미수 지에스에는 없어?3 ㅈㄱㄴ',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['지에스'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '지에스' }
  },
  {
    id: 'comment-421',
    text: '19일 수령했으면 리뉴얼이야?',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['리뉴얼'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '리뉴얼' }
  },
  {
    id: 'comment-422',
    text: '흑백요리사 맛피아 밤티라미수 후기 21 첫날 예약성공해서 2개주문하고 오늘찾아옴생각보다 더 티라미수맛이고 밤+커피향남맛있는데 진짜 달긴하다빵이 아니라 다이제종류다보니 티라미수 생각했을때 퐁신함은 없고 크림이 많음냉장이다보니 그래놀라가',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-423',
    text: '눅눅해져서 씹는데 바삭함은 없고 눅눅하긴함ㅜ',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['바삭'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '바삭' }
  },
  {
    id: 'comment-424',
    text: '쓰다보니 맛없는줄알겠는데 맛있음!',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-425',
    text: '편의점디저트 늘 기대이하였는데 얘는 맛있다!!',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-426',
    text: '떼랑 먹는데 아메리카노랑 먹어야될듯맛피아 인스타보니 달기 줄이고 그래놀라 식감개선하겠다던데 딱 그럼 더 맛있을듯!!',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-427',
    text: '큐ㅠㅠ 맛있었으면 좋았을것을... 또르르',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '맛' }
  },
  {
    id: 'comment-428',
    text: '매장에 재고가 있나포켓씨유로 보니까 매장졀 재고에는 상품 이름조차 안 뜨길래ㅠㅠㅠ',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '씨유' }
  },
  {
    id: 'comment-429',
    text: '밤티라미수같은 디저트 맛있어??',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-430',
    text: '씨유 밤티라미수 예약 서버 따로 만들면 안됨..?',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '씨유' }
  },
  {
    id: 'comment-431',
    text: 'GS 밤티라미수 먹어봤는데8 너무 달아서 세 입 먹고 다 버림',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['GS'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: 'GS' }
  },
  {
    id: 'comment-432',
    text: '진한 몽블랑 크림 먹는느낌',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['느낌'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '느낌' }
  },
  {
    id: 'comment-433',
    text: '밤티라미수 오늘 픽업날짠데 낼 아침에 가서 픽업 가능해??1 ㅈㄱㄴ!',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['짠'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '짠' }
  },
  {
    id: 'comment-434',
    text: '근데 맛있긴 함',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-435',
    text: '밤티라미수 지금 나오는 건 리뉴얼 된 거지??',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['리뉴얼'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '리뉴얼' }
  },
  {
    id: 'comment-436',
    text: 'Cu알바생익 잇닝 ㅜ3 밤티라미수 예약구매하고12일 2시이후 픽업가능이라고 돼있는거 보고샀는데..',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['Cu'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: 'Cu' }
  },
  {
    id: 'comment-437',
    text: '를 카페st로 변형해서 푸딩으로 출시하심디저트에 진심이신 사장님이 가까이 있어서 햄볶',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['진심'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '진심' }
  },
  {
    id: 'comment-438',
    text: '4 CU 어플 어디서 봐야 확인할수있어...?',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['CU'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: 'CU' }
  },
  {
    id: 'comment-439',
    text: 'CU 나폴리맛피아 밤티라미수 후기5 맛있음!!!',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-440',
    text: '밤크림이랑 초코의 조화가 굿근데 한개 다 먹으면 물려티라미수로 나온 편의점 디저트 중에 젤 맛난듯거의 크림이 95 절여진 빵 5촉촉 축축사이의 그래놀라',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['촉촉'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '촉촉' }
  },
  {
    id: 'comment-441',
    text: '한번정도 맛본걸로 만족',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['만족'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '만족' }
  },
  {
    id: 'comment-442',
    text: '씨유 밤티라미수 한시간만에 성공ㅋㅋ4 열버승리다 하',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '씨유' }
  },
  {
    id: 'comment-443',
    text: '밤티라미수 새로 리뉴얼 되자나 그건 아직 안 나왔지?',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['리뉴얼'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '리뉴얼' }
  },
  {
    id: 'comment-444',
    text: '밤티라미수 리뉴얼 잘됐네',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['리뉴얼'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '리뉴얼' }
  },
  {
    id: 'comment-445',
    text: '밤티라미수 맛있을까',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-446',
    text: '씨유 밤티라미수 예약한 거 언제 픽업할 수 있어?2 픽업일자는 오늘인데 구매내역 들어가면 상품준비중이라고 뜨거든?',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '씨유' }
  },
  {
    id: 'comment-447',
    text: '씨유 밤티라미수 예약했당1 꺄악',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '씨유' }
  },
  {
    id: 'comment-448',
    text: '6 나 약속 늦게 끝나면 12시 넘어서 편의점 도착할 수도 있는데....',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['편의점'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '편의점' }
  },
  {
    id: 'comment-449',
    text: '밤티라미수 맛있어???',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-450',
    text: '집주변에 재고많은데22 맛있나??',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-451',
    text: 'cu 밤티라미수 사왔당ㅎㅎ',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['cu'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: 'cu' }
  },
  {
    id: 'comment-452',
    text: '씨유 밤티라미수 진짜 왜 이렇게 냈냐2 기대를 하고말고의 문제가 아니라 그냥 편의점 디저트라고 쳐도 버리는 사람이 많은 맛인데 맛피아 이름 걸고...ㅠ',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['편의점', '씨유'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '편의점' }
  },
  {
    id: 'comment-453',
    text: '리뉴얼이 확실히 돼야할듯',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['리뉴얼'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '리뉴얼' }
  },
  {
    id: 'comment-454',
    text: '밤티라미수 지금 사는건 리뉴얼 된건가??',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['리뉴얼'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '리뉴얼' }
  },
  {
    id: 'comment-455',
    text: '누가 편의점 밤티라미수 안 달다고 그랬냐2 개달아...',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['편의점'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '편의점' }
  },
  {
    id: 'comment-456',
    text: '밤티라미수 드디어 삼6 맛은.. 기대를 안해서 그런가 생각보다 맛있었음근데 달아서 한번에 다 먹진 못할듯',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-457',
    text: '남친한테 지나가다 밤티라미수 맛있겠다 했는데 이거 찾으려고 편의점 돌아다녔다네..?',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-458',
    text: '..1 편의점 어플까지 깔아서 찾아다녔다는데 뭔가 되게 미안해짐리뉴얼 됐대~',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['편의점', '리뉴얼'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '편의점' }
  },
  {
    id: 'comment-459',
    text: '맛있겠다~',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-460',
    text: '미국익 밤티라미수 먹는데 너무 행복해46 한인이 운영하는 카페에 밤티라미수 팔길래 먹어봤는데 장담하는데 한국씨유거보다 몇천배는 맛있음ㅋㅋ 나폴리 맛피아가 만든거보다 더 맛있는 맛일듯와 진짜 개맛있다',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-461',
    text: '하나 먹어보고 너무 맛있어서 바로 하나 더 테이크아웃 해서 집에 가져옴..',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-462',
    text: '근데 하나 더 사올걸 후회중이야..와 진짜 내가 먹어본 모든 케이크종류중에 이게 최고다',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['최고'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '최고' }
  },
  {
    id: 'comment-463',
    text: 'cu 알바익있어??',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['cu'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: 'cu' }
  },
  {
    id: 'comment-464',
    text: '밤티라미수 너무.... 너무 느끼해9 크림만 있어서 그런지 너무.... 너무 너무 느끼해맛있긴 했는데 느끼한걸 못먹는 나는 별루였당...',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['느끼', '맛있'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '느끼' }
  },
  {
    id: 'comment-465',
    text: '난 밤티라미수 맛있더라',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['맛'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-466',
    text: '리뉴얼 전에 먹어봤는데냉동실에 얼려먹으니까단맛도 적고 아이스크림같아서 되게 맛있게먹음근데 밤맛이 너무 안나...',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['맛있', '단맛'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '맛있' }
  },
  {
    id: 'comment-467',
    text: '그리고 티라미수라는 느낌이 없어...',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['느낌'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '느낌' }
  },
  {
    id: 'comment-468',
    text: '밤티라미수 이젠 구하기 쉽나?1 씨유 갔는데 있어서 놀람',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '씨유' }
  },
  {
    id: 'comment-469',
    text: '6 편의점 갔는데 1개 있길래 신나서 사왔는데 인티에 쳐보니까 다 너무 달다고 별로래 ㅠㅠㅋㅋ',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['편의점'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '편의점' }
  },
  {
    id: 'comment-470',
    text: '씨유에서 못찾겠다,,,',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '씨유' }
  },
  {
    id: 'comment-471',
    text: '씨유 밤티라미수 내일 및시에 열려..? ㅠㅠ',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '씨유' }
  },
  {
    id: 'comment-472',
    text: '1 포켓씨유 들어가도 그냥 내일 다시 열린다는 말만 있어,, ㅠㅠ',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 0, aspect: '씨유' }
  },
  {
    id: 'comment-473',
    text: '밤티라미수 포켓씨유 달려가 예약판매중!',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '씨유' }
  },
  {
    id: 'comment-474',
    text: 'CU 흑백요리사 밤티라미수 예약함 16 2개만 했당ㅋㅋ',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['CU'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: 'CU' }
  },
  {
    id: 'comment-475',
    text: '진심 씨유는 밤티라미수 얼른 출시해야 한다1 어제 흑백요리사 보니까 다 씨유 제품으로 만들었던데밤티라미스 출시할 명분이 너무 확실하지 않니????!!!!',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '커뮤니티' as const,
    attributes: ['씨유'],
    likes: 0,
    analysis: { sentiment_score: 1, aspect: '씨유' }
  },
  {
    id: 'comment-477',
    text: 'ㅋㅋ 리뉴얼된 밤티라미수 바밤바맛도 기대할께요',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['리뉴얼'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '리뉴얼' }
  },
  {
    id: 'comment-478',
    text: '이거 보는 데 너무 맛있어 보이더라구요 ㅠㅠ',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['맛'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-479',
    text: '헉 너무 맛있어보여요',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['맛'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-480',
    text: '미쳤다 대박이에요',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['대박'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '대박' }
  },
  {
    id: 'comment-481',
    text: '수요일, cu 편의점에서 권성준의 밤 티라미스가 여러분을 기다립니다.',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['편의점', 'cu'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '편의점' }
  },
  {
    id: 'comment-482',
    text: '퀄리티 미쳣다 그저 빛',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['퀄리티'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '퀄리티' }
  },
  {
    id: 'comment-483',
    text: '재품이없으면 gs가면되고 없으면 세븐을 가면되지 카피할려면 똑같이 만들어야지',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '유튜브' as const,
    attributes: ['세븐', 'gs'],
    likes: null,
    analysis: { sentiment_score: 0, aspect: '세븐' }
  },
  {
    id: 'comment-484',
    text: '나 자신을 대접하는 느낌',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['느낌'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '느낌' }
  },
  {
    id: 'comment-485',
    text: '0:16 스팸과 리챔 사이에있는 빽햄ㅋㅋ 그런데 원래 빽햄이 CU에도있었나요?',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '유튜브' as const,
    attributes: ['CU'],
    likes: null,
    analysis: { sentiment_score: 0, aspect: 'CU' }
  },
  {
    id: 'comment-487',
    text: '저 너무 행복했어요, 기억해주셔서 감사해요',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['행복'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '행복' }
  },
  {
    id: 'comment-488',
    text: '근데 저 빵이 진짜 맛있긴 함',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['맛'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-489',
    text: '언니 영상보고 편의점 가서 도시락 사서 먹으려고 했는데 다 팔리고 없더라고요~~ㅠ.ㅠ',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '유튜브' as const,
    attributes: ['편의점'],
    likes: null,
    analysis: { sentiment_score: 0, aspect: '편의점' }
  },
  {
    id: 'comment-491',
    text: 'CU 편의점 대결이 엄청난 행운이었던거지',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['편의점', 'CU'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '편의점' }
  },
  {
    id: 'comment-493',
    text: 'cu 도시락 퀄 뭔가요 대박이네요ㅠㅋㅋㅋ',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['cu'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: 'cu' }
  },
  {
    id: 'comment-495',
    text: '대박',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['대박'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '대박' }
  },
  {
    id: 'comment-496',
    text: '연차 갈기고 빵먹으면서 햇님웅니 빵먹는거 보기.....행복하다',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['행복'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '행복' }
  },
  {
    id: 'comment-499',
    text: '앜ㅋㅋ 편의점 달려가야겠네요..!!!',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['편의점'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '편의점' }
  },
  {
    id: 'comment-500',
    text: '1:46:33 모든게 다 짜고 달아 ㅋㅋ 편의점 디저트의 결론',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '유튜브' as const,
    attributes: ['편의점'],
    likes: null,
    analysis: { sentiment_score: 0, aspect: '편의점' }
  },
  {
    id: 'comment-502',
    text: '대리만족 장난없다 과자 너무 먹고 싶다ㅠㅠ',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['만족'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '만족' }
  },
  {
    id: 'comment-503',
    text: '가격으로 따지면 몇만원해여 ㅋㅋ',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['가격'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '가격' }
  },
  {
    id: 'comment-505',
    text: '너무 느끼해요..ㅠㅠ',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '유튜브' as const,
    attributes: ['느끼'],
    likes: null,
    analysis: { sentiment_score: 0, aspect: '느끼' }
  },
  {
    id: 'comment-506',
    text: '맛있는 거 박박 긁어 모아서 만든 건데 왜요? ㅠㅠ',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['맛'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-507',
    text: '디저트러버라 다이어트 디저트 최고네요오 ㅠㅠㅠ 감사해유',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['최고'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '최고' }
  },
  {
    id: 'comment-508',
    text: '와 직접 해먹어봤는데 이거 너무 맛있어요ㅠㅜ',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['맛'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-509',
    text: '다른사람들은 대체로 라면을 써서 맛이 짜고 맵고 자극적이었는데 그 맛을 중화시켜주도록 시원하고 달달한 음식을 만들어서 냈으니 무조건 이기지',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['달달'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '달달' }
  },
  {
    id: 'comment-511',
    text: '편의점에서 예약판매 하던데 그것도 구하기가 어렵더라구요',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '유튜브' as const,
    attributes: ['편의점'],
    likes: null,
    analysis: { sentiment_score: 0, aspect: '편의점' }
  },
  {
    id: 'comment-512',
    text: '티라미수는 물론 라떼 너무맛있을거같아요!!',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['맛'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '맛' }
  },
  {
    id: 'comment-513',
    text: '씨유가 좀 짜더라구요',
    date: getRandomOctoberDate(),
    sentiment: 'negative' as const,
    source: '유튜브' as const,
    attributes: ['씨유'],
    likes: null,
    analysis: { sentiment_score: 0, aspect: '씨유' }
  },
  {
    id: 'comment-514',
    text: '오트밀 대박!!!',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['대박'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '대박' }
  },
  {
    id: 'comment-515',
    text: '겁나 똑똑한 놈임 씨유하고 협업까지 생각하고 노린거네',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['씨유'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '씨유' }
  },
  {
    id: 'comment-516',
    text: '맛있겠다...',
    date: getRandomOctoberDate(),
    sentiment: 'positive' as const,
    source: '유튜브' as const,
    attributes: ['맛'],
    likes: null,
    analysis: { sentiment_score: 1, aspect: '맛' }
  }
];

const mockCommentsData = realCommentsData;

const CommentsTab: React.FC<CommentsTabProps> = ({ channel, period, dateRange }) => {
  const [selectedComment, setSelectedComment] = useState<any>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [mockComments, setMockComments] = useState(mockCommentsData);
  const [filteredComments, setFilteredComments] = useState(mockCommentsData);

  // 필터링 상태
  const [sourceFilter, setSourceFilter] = useState<string>("all");
  const [sentimentFilter, setSentimentFilter] = useState<string>("all");
  const [attributeFilter, setAttributeFilter] = useState<string>("all");
  const [sortOption, setSortOption] = useState<string>("latest");

  // 채널 변경시 필터링
  useEffect(() => {
    let filteredData = mockCommentsData;
    
    if (channel !== "전체") {
      filteredData = filteredData.filter(comment => comment.source === channel);
    }
    
    setMockComments(filteredData);
  }, [channel]);

  // 날짜 범위 필터링
  useEffect(() => {
    const filteredByDate = mockCommentsData.filter(comment => 
      comment.date >= dateRange.from && 
      (!dateRange.to || comment.date <= dateRange.to)
    );
    
    setMockComments(filteredByDate);
  }, [dateRange]);

  // 필터 변경 처리
  useEffect(() => {
    let result = mockComments;
    
    if (sourceFilter !== "all") {
      result = result.filter(comment => comment.source === sourceFilter);
    }
    
    if (sentimentFilter !== "all") {
      result = result.filter(comment => comment.sentiment === sentimentFilter);
    }
    
    if (attributeFilter !== "all") {
      result = result.filter(comment => 
        comment.attributes.includes(attributeFilter)
      );
    }
    
    // 정렬 처리
    switch (sortOption) {
      case "likesHigh":
        result = [...result].sort((a, b) => b.likes - a.likes);
        break;
      case "likesLow":
        result = [...result].sort((a, b) => a.likes - b.likes);
        break;
      case "latest":
        result = [...result].sort((a, b) => b.date.getTime() - a.date.getTime());
        break;
      case "oldest":
        result = [...result].sort((a, b) => a.date.getTime() - b.date.getTime());
        break;
      default:
        // 기본 정렬 (최신순)
        result = [...result].sort((a, b) => b.date.getTime() - a.date.getTime());
    }
    
    setFilteredComments(result);
  }, [sourceFilter, sentimentFilter, attributeFilter, sortOption, mockComments]);

  const handleViewDetails = (id: string) => {
    const comment = mockComments.find(c => c.id === id);
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
      
      <CommentsTable 
        comments={filteredComments} 
        onViewDetails={handleViewDetails} 
      />
      
      <CommentDetails 
        comment={selectedComment}
        open={isDetailsOpen}
        onClose={handleCloseDetails}
      />
    </div>
  );
};

export default CommentsTab;
