#!/usr/bin/env python
"""
Prefect 워크플로우 설정 및 배포 스크립트

이 스크립트는 SNATCH 프로젝트의 Prefect 워크플로우를 설정하고 배포합니다.
- Prefect API 연결 설정
- 파이프라인 배포 생성
- 워크 풀 및 에이전트 설정
"""
import os
import sys
from pathlib import Path

# 상위 디렉토리를 경로에 추가하여 모듈 임포트 가능하게 함
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import subprocess
from datetime import timedelta

from prefect import flow, task, get_run_logger
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import IntervalSchedule
from prefect.infrastructure.docker import DockerContainer

# 파이프라인 모듈 임포트
from pipelines.youtube import youtube_etl_pipeline


def setup_prefect_connection():
    """
    Prefect API 연결을 설정합니다.
    로컬 개발 환경에서는 로컬 Prefect 서버를, 
    프로덕션 환경에서는 환경 변수로 지정된 API URL을 사용합니다.
    """
    prefect_api_url = os.getenv("PREFECT_API_URL", "http://127.0.0.1:4200/api")
    
    print(f"Prefect API URL 설정: {prefect_api_url}")
    
    try:
        # Prefect API URL 설정
        subprocess.run(["prefect", "config", "set", "PREFECT_API_URL=" + prefect_api_url], check=True)
        print("Prefect API URL 설정 완료")
    except subprocess.CalledProcessError as e:
        print(f"Prefect API URL 설정 중 오류 발생: {e}")
        sys.exit(1)


def create_work_pool():
    """
    Prefect 워크 풀을 생성합니다.
    """
    try:
        # 기존 워크 풀 확인
        result = subprocess.run(["prefect", "work-pool", "ls"], capture_output=True, text=True, check=True)
        
        # sweetspot-pool이 이미 존재하는지 확인
        if "sweetspot-pool" not in result.stdout:
            print("'sweetspot-pool' 워크 풀 생성 중...")
            subprocess.run(["prefect", "work-pool", "create", "sweetspot-pool", "--type", "process"], check=True)
            print("'sweetspot-pool' 워크 풀 생성 완료")
        else:
            print("'sweetspot-pool' 워크 풀이 이미 존재합니다.")
            
    except subprocess.CalledProcessError as e:
        print(f"워크 풀 생성 중 오류 발생: {e}")
        sys.exit(1)


def deploy_youtube_pipeline():
    """
    YouTube ETL 파이프라인을 배포합니다.
    """
    try:
        print("YouTube ETL 파이프라인 배포 중...")
        
        # 배포 생성
        deployment = Deployment.build_from_flow(
            flow=youtube_etl_pipeline,
            name="youtube-etl-scheduled",
            schedule=IntervalSchedule(interval=timedelta(hours=12)),
            work_pool_name="sweetspot-pool",
            tags=["sweetspot", "youtube", "etl", "dessert"]
        )
        
        # 배포 적용
        deployment_id = deployment.apply()
        print(f"YouTube ETL 파이프라인 배포 완료 (ID: {deployment_id})")
        
    except Exception as e:
        print(f"파이프라인 배포 중 오류 발생: {e}")
        sys.exit(1)


def start_agent():
    """
    Prefect 에이전트를 시작합니다.
    """
    try:
        print("Prefect 에이전트 시작 중...")
        # 에이전트 시작 (별도 프로세스로)
        subprocess.Popen(["prefect", "agent", "start", "-p", "sweetspot-pool"])
        print("Prefect 에이전트가 시작되었습니다.")
        
    except Exception as e:
        print(f"에이전트 시작 중 오류 발생: {e}")
        sys.exit(1)


@flow(name="prefect-setup-flow")
def setup_flow():
    """
    Prefect 설정 플로우
    """
    logger = get_run_logger()
    logger.info("Prefect 설정 시작")
    
    # Prefect API 연결 설정
    setup_prefect_connection()
    
    # 워크 풀 생성
    create_work_pool()
    
    # YouTube ETL 파이프라인 배포
    deploy_youtube_pipeline()
    
    # 에이전트 시작 (선택 사항)
    if "--start-agent" in sys.argv:
        start_agent()
    
    logger.info("Prefect 설정 완료")
    return "Prefect 설정 완료"


if __name__ == "__main__":
    print("SNATCH 프로젝트 Prefect 설정 시작")
    setup_flow() 