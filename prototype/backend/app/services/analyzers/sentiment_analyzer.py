"""
KR-BERT 기반 감성 분석 모듈

텍스트 데이터에서 긍정/부정/중립 감성을 분석하는 모듈입니다.
KR-BERT 모델을 사용하여 텍스트의 감성을 분류하고, 
90% 이상의 정확도를 목표로 합니다.
"""

import os
import json
import logging
import numpy as np
from typing import Dict, List, Any, Union, Optional, Tuple
from datetime import datetime
from collections import Counter

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AdamW
from transformers import get_linear_schedule_with_warmup
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from app.core.config import settings

logger = logging.getLogger(__name__)

# 기본 모델 이름 (SNS 텍스트에 특화된 한국어 감성 분석 모델)
DEFAULT_MODEL_NAME = "snunlp/KR-BERT-small"
SENTIMENT_MODEL_PATH = os.path.join(settings.MODEL_DIR, "sentiment_model")


class SentimentAnalyzer:
    """
    KR-BERT 기반 감성 분석기 클래스
    
    텍스트에서 긍정, 부정, 중립 감성을 분석합니다.
    미세 조정된 모델을 사용하여 편의점 디저트 관련 텍스트에 특화된 분석을 수행합니다.
    """
    
    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
        """
        감성 분석기 초기화
        
        Args:
            model_path: 사용할 모델 경로 (없으면 기본 모델 사용)
            device: 사용할 디바이스 ('cuda' 또는 'cpu', None이면 자동 감지)
        """
        self.model_path = model_path or DEFAULT_MODEL_NAME
        
        # 로컬 미세 조정 모델이 있으면 그것을 사용
        if os.path.exists(SENTIMENT_MODEL_PATH):
            self.model_path = SENTIMENT_MODEL_PATH
            logger.info(f"로컬 미세 조정 모델을 사용합니다: {SENTIMENT_MODEL_PATH}")
        
        # 디바이스 설정 (GPU 사용 가능 시 사용)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"감성 분석에 {self.device} 디바이스 사용")
        
        # 토크나이저 및 모델 로드
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
        self.model.to(self.device)
        self.model.eval()
        
        # 감성 레이블 매핑
        self.id2label = {0: "negative", 1: "neutral", 2: "positive"}
        self.label2id = {"negative": 0, "neutral": 1, "positive": 2}
        
        logger.info("감성 분석기 초기화 완료")
    
    async def analyze(self, text: str) -> Dict[str, Any]:
        """
        텍스트의 감성을 분석합니다.
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            Dict[str, Any]: 분석 결과 (감성 점수, 신뢰도 등)
        """
        # 텍스트가 비어있는 경우
        if not text or len(text.strip()) == 0:
            return {
                "sentiment": "neutral",
                "positive": 0.0,
                "neutral": 1.0,
                "negative": 0.0,
                "confidence": 1.0
            }
        
        try:
            # 텍스트 전처리 및 토큰화
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)
            
            # 추론 모드
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # 소프트맥스로 확률 변환
            probs = torch.nn.functional.softmax(outputs.logits, dim=1).cpu().numpy()[0]
            
            # 결과 해석
            sentiment_id = np.argmax(probs)
            sentiment = self.id2label[sentiment_id]
            confidence = float(probs[sentiment_id])
            
            # 결과 반환
            result = {
                "sentiment": sentiment,
                "positive": float(probs[2]),
                "neutral": float(probs[1]),
                "negative": float(probs[0]),
                "confidence": confidence,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"감성 분석 중 오류 발생: {str(e)}")
            # 오류 발생 시 중립으로 반환
            return {
                "sentiment": "neutral",
                "positive": 0.0,
                "neutral": 1.0,
                "negative": 0.0,
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def analyze_batch(self, texts: List[str], batch_size: int = 16) -> List[Dict[str, Any]]:
        """
        여러 텍스트의 감성을 배치로 분석합니다.
        
        Args:
            texts: 분석할 텍스트 목록
            batch_size: 배치 크기
            
        Returns:
            List[Dict[str, Any]]: 각 텍스트의 분석 결과 목록
        """
        results = []
        
        # 빈 입력 처리
        if not texts:
            return results
        
        try:
            # 데이터 로더 설정
            dataset = SentimentDataset(texts, self.tokenizer, max_length=512)
            dataloader = DataLoader(dataset, batch_size=batch_size)
            
            # 배치 처리
            for batch in dataloader:
                # 배치 데이터를 디바이스로 이동
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                
                # 추론
                with torch.no_grad():
                    outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                
                # 소프트맥스로 확률 변환
                probs = torch.nn.functional.softmax(outputs.logits, dim=1).cpu().numpy()
                
                # 배치 결과 처리
                for prob in probs:
                    sentiment_id = np.argmax(prob)
                    sentiment = self.id2label[sentiment_id]
                    confidence = float(prob[sentiment_id])
                    
                    results.append({
                        "sentiment": sentiment,
                        "positive": float(prob[2]),
                        "neutral": float(prob[1]),
                        "negative": float(prob[0]),
                        "confidence": confidence,
                        "analyzed_at": datetime.utcnow().isoformat()
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"배치 감성 분석 중 오류 발생: {str(e)}")
            # 오류 발생 시 모든 텍스트에 대해 중립으로 반환
            return [
                {
                    "sentiment": "neutral",
                    "positive": 0.0,
                    "neutral": 1.0,
                    "negative": 0.0,
                    "confidence": 0.0,
                    "error": str(e)
                }
                for _ in texts
            ]
    
    async def fine_tune(
        self,
        train_texts: List[str],
        train_labels: List[str],
        val_texts: Optional[List[str]] = None,
        val_labels: Optional[List[str]] = None,
        epochs: int = 3,
        batch_size: int = 16,
        learning_rate: float = 2e-5,
        save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        감성 분석 모델을 미세 조정합니다.
        
        Args:
            train_texts: 학습 텍스트 목록
            train_labels: 학습 레이블 목록 ("positive", "neutral", "negative")
            val_texts: 검증 텍스트 목록
            val_labels: 검증 레이블 목록
            epochs: 학습 에포크 수
            batch_size: 배치 크기
            learning_rate: 학습률
            save_path: 모델 저장 경로 (None이면 기본 경로)
            
        Returns:
            Dict[str, Any]: 학습 결과 (정확도, 손실 등)
        """
        # 저장 경로 설정
        save_path = save_path or SENTIMENT_MODEL_PATH
        
        # 모델을 학습 모드로 전환
        self.model.train()
        
        # 레이블 변환
        train_label_ids = [self.label2id[label] for label in train_labels]
        
        # 학습 데이터셋 및 데이터로더 생성
        train_dataset = SentimentDataset(
            texts=train_texts,
            tokenizer=self.tokenizer,
            labels=train_label_ids,
            max_length=512
        )
        train_dataloader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True
        )
        
        # 검증 데이터셋 및 데이터로더 생성 (제공된 경우)
        val_dataloader = None
        if val_texts and val_labels:
            val_label_ids = [self.label2id[label] for label in val_labels]
            val_dataset = SentimentDataset(
                texts=val_texts,
                tokenizer=self.tokenizer,
                labels=val_label_ids,
                max_length=512
            )
            val_dataloader = DataLoader(
                val_dataset,
                batch_size=batch_size
            )
        
        # 옵티마이저 및 스케줄러 설정
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        total_steps = len(train_dataloader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=0,
            num_training_steps=total_steps
        )
        
        # 학습 지표 저장용
        training_stats = []
        best_accuracy = 0.0
        
        # 학습 루프
        logger.info(f"모델 미세 조정 시작: {epochs} 에포크, {len(train_texts)} 샘플")
        for epoch in range(epochs):
            # 학습 단계
            total_loss = 0
            self.model.train()
            
            for batch in train_dataloader:
                # 배치 데이터를 디바이스로 이동
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["labels"].to(self.device) if "labels" in batch else None
                
                # 그래디언트 초기화
                optimizer.zero_grad()
                
                # 순전파
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                total_loss += loss.item()
                
                # 역전파
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
            
            avg_train_loss = total_loss / len(train_dataloader)
            logger.info(f"에포크 {epoch+1}/{epochs} 완료 | 평균 학습 손실: {avg_train_loss:.4f}")
            
            # 검증 단계
            if val_dataloader:
                val_accuracy, val_metrics = await self._evaluate(val_dataloader)
                logger.info(f"검증 정확도: {val_accuracy:.4f} | 검증 F1: {val_metrics['f1']:.4f}")
                
                # 최고 성능 모델 저장
                if val_accuracy > best_accuracy:
                    best_accuracy = val_accuracy
                    
                    # 저장 디렉토리 생성
                    os.makedirs(save_path, exist_ok=True)
                    
                    # 모델 저장
                    self.model.save_pretrained(save_path)
                    self.tokenizer.save_pretrained(save_path)
                    
                    # 메타데이터 저장
                    metadata = {
                        "accuracy": val_accuracy,
                        "precision": val_metrics["precision"],
                        "recall": val_metrics["recall"],
                        "f1": val_metrics["f1"],
                        "fine_tuned_at": datetime.utcnow().isoformat(),
                        "epochs": epoch + 1,
                        "base_model": DEFAULT_MODEL_NAME
                    }
                    
                    with open(os.path.join(save_path, "metadata.json"), "w") as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"모델이 {save_path}에 저장되었습니다 (정확도: {val_accuracy:.4f})")
                
                # 에포크 통계 저장
                training_stats.append({
                    "epoch": epoch + 1,
                    "train_loss": avg_train_loss,
                    "val_accuracy": val_accuracy,
                    "val_precision": val_metrics["precision"],
                    "val_recall": val_metrics["recall"],
                    "val_f1": val_metrics["f1"]
                })
        
        # 평가 결과
        final_results = {
            "epochs_completed": epochs,
            "train_samples": len(train_texts),
            "val_samples": len(val_texts) if val_texts else 0,
            "best_accuracy": best_accuracy,
            "training_stats": training_stats,
            "model_path": save_path
        }
        
        # 모델을 다시 평가 모드로 전환
        self.model.eval()
        
        return final_results
    
    async def _evaluate(self, dataloader: DataLoader) -> Tuple[float, Dict[str, float]]:
        """
        모델을 평가합니다.
        
        Args:
            dataloader: 평가 데이터로더
            
        Returns:
            Tuple[float, Dict[str, float]]: (정확도, 기타 메트릭)
        """
        self.model.eval()
        
        all_preds = []
        all_labels = []
        
        for batch in dataloader:
            # 배치 데이터를 디바이스로 이동
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)
            labels = batch["labels"].to(self.device) if "labels" in batch else None
            
            # 추론
            with torch.no_grad():
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
            
            # 예측 및 레이블 수집
            preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()
            all_preds.extend(preds)
            
            if labels is not None:
                all_labels.extend(labels.cpu().numpy())
        
        # 정확도 계산
        accuracy = accuracy_score(all_labels, all_preds)
        
        # 기타 메트릭 계산
        precision, recall, f1, _ = precision_recall_fscore_support(
            all_labels, all_preds, average="weighted"
        )
        
        # 결과 반환
        metrics = {
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1)
        }
        
        return float(accuracy), metrics


class SentimentDataset(Dataset):
    """
    감성 분석용 데이터셋 클래스
    """
    
    def __init__(
        self,
        texts: List[str],
        tokenizer,
        labels: Optional[List[int]] = None,
        max_length: int = 512
    ):
        """
        데이터셋 초기화
        
        Args:
            texts: 텍스트 목록
            tokenizer: 토크나이저
            labels: 레이블 목록 (없으면 추론 모드)
            max_length: 최대 시퀀스 길이
        """
        self.texts = texts
        self.tokenizer = tokenizer
        self.labels = labels
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        
        # 텍스트 토큰화
        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        # 텐서 크기 조정 (배치 차원 제거)
        item = {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze()
        }
        
        # 레이블이 있으면 추가
        if self.labels is not None:
            item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        
        return item


# 싱글톤 인스턴스 생성
_sentiment_analyzer = None

async def get_analyzer() -> SentimentAnalyzer:
    """
    감성 분석기의 싱글톤 인스턴스를 반환합니다.
    
    Returns:
        SentimentAnalyzer: 감성 분석기 인스턴스
    """
    global _sentiment_analyzer
    
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    
    return _sentiment_analyzer 


class SimpleSentimentAnalyzer:
    """
    매우 간단한 감성 분석기.
    SentimentAnalyzer의 간소화 버전으로, 최소한의 기능만 제공합니다.
    """
    
    def __init__(self):
        """간단한 감성 분석기를 초기화합니다."""
        # 기본 감성 단어 목록
        self.positive_words = [
            "좋아요", "멋져요", "훌륭해요", "최고", "감사", "행복", "아름다운", 
            "맛있", "추천", "최애", "존맛", "완벽"
        ]
        
        self.negative_words = [
            "별로", "싫어요", "최악", "실망", "후회", "불만", "불편", "나쁜", 
            "비추", "형편없", "안좋", "다신안"
        ]
    
    def analyze(self, text: str) -> Dict[str, str]:
        """
        텍스트의 감성을 간단히 분석합니다.
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            감성 분석 결과 (positive, negative, neutral)
        """
        if not text:
            return {"sentiment": "neutral"}
        
        text = text.lower()
        
        # 감성 단어 카운트
        positive_count = sum(1 for word in self.positive_words if word in text)
        negative_count = sum(1 for word in self.negative_words if word in text)
        
        # 감성 판단
        if positive_count > negative_count:
            return {"sentiment": "positive"}
        elif negative_count > positive_count:
            return {"sentiment": "negative"}
        else:
            return {"sentiment": "neutral"} 