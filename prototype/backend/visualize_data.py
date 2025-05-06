#!/usr/bin/env python
"""
유튜브 데이터 분석 결과를 시각화하는 스크립트
"""
import os
import json
import sys
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from wordcloud import WordCloud
import numpy as np
from typing import Dict, Any, List, Tuple

def load_data(file_path: str) -> Dict[str, Any]:
    """
    JSON 파일에서 데이터를 로드합니다.
    
    Args:
        file_path: 데이터 파일 경로
        
    Returns:
        로드된 데이터
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"데이터 로드 오류: {e}")
        sys.exit(1)

def visualize_sentiment(sentiment_analysis: Dict[str, Any], ax: plt.Axes) -> None:
    """
    감성 분석 결과를 시각화합니다.
    
    Args:
        sentiment_analysis: 감성 분석 결과
        ax: 그래프를 그릴 Axes 객체
    """
    # 데이터 준비
    dist = sentiment_analysis["sentiment_distribution"]
    labels = ['긍정적', '중립적', '부정적']
    values = [dist['positive'], dist['neutral'], dist['negative']]
    colors = ['#4CAF50', '#FFC107', '#F44336']
    
    # 원형 그래프 생성
    wedges, texts, autotexts = ax.pie(
        values, 
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        wedgeprops={'edgecolor': 'w', 'linewidth': 1}
    )
    
    # 그래프 스타일 설정
    ax.set_title('댓글 감성 분석 결과', fontsize=14, pad=20)
    plt.setp(autotexts, size=10, weight='bold')
    
    # 평균 감성 점수 표시
    avg_score = sentiment_analysis["average_score"]
    score_text = f"평균 감성 점수: {avg_score:.2f}"
    ax.text(0, -1.2, score_text, ha='center', fontsize=12, 
            bbox=dict(boxstyle="round,pad=0.3", fc='#E8F5E9', ec="green", alpha=0.8))

def visualize_keywords(keywords: List[Tuple[str, int]], ax: plt.Axes) -> None:
    """
    키워드 빈도를 시각화합니다.
    
    Args:
        keywords: (키워드, 빈도) 튜플의 리스트
        ax: 그래프를 그릴 Axes 객체
    """
    words = [word for word, _ in keywords]
    counts = [count for _, count in keywords]
    
    # 그래프 생성
    colors = plt.cm.viridis(np.linspace(0.3, 0.8, len(words)))
    bars = ax.barh(words, counts, color=colors)
    
    # 그래프 스타일 설정
    ax.set_title('주요 키워드 빈도', fontsize=14)
    ax.set_xlabel('빈도', fontsize=12)
    ax.invert_yaxis()  # 가장 빈도가 높은 항목이 위에 오도록 순서 반전
    
    # 빈도 숫자 표시
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.3, bar.get_y() + bar.get_height()/2, 
                str(int(width)), ha='left', va='center', fontsize=10)

def create_wordcloud(keywords: List[Tuple[str, int]], ax: plt.Axes) -> None:
    """
    워드클라우드를 생성합니다.
    
    Args:
        keywords: (키워드, 빈도) 튜플의 리스트
        ax: 그래프를 그릴 Axes 객체
    """
    # 워드클라우드용 데이터 준비
    word_freq = {word: count for word, count in keywords}
    
    # 워드클라우드 생성
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        colormap='viridis',
        max_words=50,
        contour_width=1,
        contour_color='steelblue'
    ).generate_from_frequencies(word_freq)
    
    # 워드클라우드 표시
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_title('키워드 워드클라우드', fontsize=14)
    ax.axis('off')

def main():
    """메인 함수"""
    # 분석 결과 파일 확인
    data_dir = os.path.join(os.getcwd(), "data")
    result_path = os.path.join(data_dir, "analysis_result.json")
    
    if not os.path.exists(result_path):
        print(f"분석 결과 파일이 존재하지 않습니다: {result_path}")
        sys.exit(1)
    
    # 데이터 로드
    analysis_data = load_data(result_path)
    print("분석 데이터를 로드했습니다.")
    
    # 원본 데이터 파일 찾기
    data_files = [f for f in os.listdir(data_dir) if f.endswith("_test_data.json")]
    if data_files:
        latest_file = sorted(data_files)[-1]
        video_data = load_data(os.path.join(data_dir, latest_file))
        video_title = video_data.get("title", "알 수 없는 비디오")
        channel_title = video_data.get("channel_title", "알 수 없는 채널")
    else:
        video_title = "알 수 없는 비디오"
        channel_title = "알 수 없는 채널"
    
    # 그림 설정
    plt.figure(figsize=(14, 10))
    plt.style.use('ggplot')
    
    # 그리드 레이아웃 설정
    gs = GridSpec(3, 2, figure=plt.gcf())
    
    # 제목 영역
    title_ax = plt.subplot(gs[0, :])
    title_ax.axis('off')
    title_ax.text(0.5, 0.5, f"유튜브 영상 분석 대시보드\n'{video_title}'", 
                 ha='center', va='center', fontsize=18, fontweight='bold')
    title_ax.text(0.5, 0.2, f"채널: {channel_title}", 
                 ha='center', va='center', fontsize=14)
    
    # 감성 분석 그래프
    sentiment_ax = plt.subplot(gs[1, 0])
    visualize_sentiment(analysis_data["sentiment_analysis"], sentiment_ax)
    
    # 키워드 빈도 그래프
    keywords_ax = plt.subplot(gs[1, 1])
    visualize_keywords(analysis_data["keywords"], keywords_ax)
    
    # 워드클라우드
    wordcloud_ax = plt.subplot(gs[2, :])
    create_wordcloud(analysis_data["keywords"], wordcloud_ax)
    
    # 그래프 간격 조정
    plt.tight_layout()
    
    # 결과 파일 저장
    output_path = os.path.join(data_dir, "analysis_dashboard.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"대시보드 이미지가 저장되었습니다: {output_path}")
    
    # 그래프 표시
    plt.show()

if __name__ == "__main__":
    main() 