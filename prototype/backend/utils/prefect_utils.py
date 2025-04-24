"""
Prefect 워크플로우 관리를 위한 유틸리티 함수들

이 모듈은 Prefect 워크플로우 및 배포를 관리하기 위한 유틸리티 함수들을 제공합니다.
"""
import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime

import httpx
from prefect import flow, task
from prefect.client import get_client
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import IntervalSchedule, CronSchedule

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def get_flow_runs(
    flow_name: Optional[str] = None,
    deployment_id: Optional[str] = None,
    limit: int = 10,
    status: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    특정 조건에 맞는 플로우 실행 기록을 조회합니다.
    
    Args:
        flow_name: 플로우 이름으로 필터링
        deployment_id: 배포 ID로 필터링
        limit: 반환할 최대 결과 수
        status: 상태로 필터링 (e.g., ["COMPLETED", "FAILED"])
        
    Returns:
        플로우 실행 목록
    """
    async with get_client() as client:
        # 필터 조건 구성
        query_filters = []
        
        if flow_name:
            query_filters.append({"name": {"any_": [flow_name]}})
        
        if deployment_id:
            query_filters.append({"deployment_id": {"any_": [deployment_id]}})
        
        if status:
            query_filters.append({"state": {"type": {"any_": status}}})
        
        # API 호출
        flows = await client.read_flow_runs(
            sort="-created",
            limit=limit,
            flow_runs=query_filters
        )
        
        # 결과 가공
        result = []
        for flow_run in flows:
            result.append({
                "id": flow_run.id,
                "name": flow_run.name,
                "status": flow_run.state.type,
                "created": flow_run.created,
                "started": flow_run.start_time,
                "finished": flow_run.end_time,
                "deployment_id": flow_run.deployment_id,
            })
        
        return result


async def get_deployment_details(deployment_id: str) -> Dict[str, Any]:
    """
    특정 배포의 상세 정보를 조회합니다.
    
    Args:
        deployment_id: 배포 ID
        
    Returns:
        배포 상세 정보
    """
    async with get_client() as client:
        try:
            deployment = await client.read_deployment(deployment_id)
            
            # 스케줄 정보 가공
            schedule_info = None
            if deployment.schedule:
                if hasattr(deployment.schedule, "interval"):
                    # IntervalSchedule인 경우
                    interval_seconds = deployment.schedule.interval.total_seconds()
                    schedule_info = f"매 {int(interval_seconds // 3600)}시간 {int((interval_seconds % 3600) // 60)}분마다"
                elif hasattr(deployment.schedule, "cron"):
                    # CronSchedule인 경우
                    schedule_info = f"Cron: {deployment.schedule.cron}"
            
            return {
                "id": deployment.id,
                "name": deployment.name,
                "flow_name": deployment.flow_name,
                "schedule": schedule_info,
                "tags": deployment.tags,
                "created": deployment.created,
                "updated": deployment.updated,
                "is_schedule_active": deployment.is_schedule_active,
                "work_pool_name": deployment.work_pool_name,
            }
        except Exception as e:
            logger.error(f"배포 정보 조회 중 오류: {e}")
            return {"error": str(e)}


async def pause_deployment_schedule(deployment_id: str) -> Dict[str, Any]:
    """
    배포의 스케줄을 일시 중지합니다.
    
    Args:
        deployment_id: 배포 ID
        
    Returns:
        일시 중지 결과
    """
    async with get_client() as client:
        try:
            result = await client.set_schedule_inactive(deployment_id)
            return {
                "success": True,
                "message": f"배포 {deployment_id}의 스케줄이 일시 중지되었습니다.",
                "result": result
            }
        except Exception as e:
            logger.error(f"스케줄 일시 중지 중 오류: {e}")
            return {
                "success": False,
                "message": f"스케줄 일시 중지 중 오류: {e}"
            }


async def resume_deployment_schedule(deployment_id: str) -> Dict[str, Any]:
    """
    배포의 스케줄을 재개합니다.
    
    Args:
        deployment_id: 배포 ID
        
    Returns:
        재개 결과
    """
    async with get_client() as client:
        try:
            result = await client.set_schedule_active(deployment_id)
            return {
                "success": True,
                "message": f"배포 {deployment_id}의 스케줄이 재개되었습니다.",
                "result": result
            }
        except Exception as e:
            logger.error(f"스케줄 재개 중 오류: {e}")
            return {
                "success": False,
                "message": f"스케줄 재개 중 오류: {e}"
            }


async def run_deployment(
    deployment_id: str,
    parameters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    배포를 즉시 실행합니다.
    
    Args:
        deployment_id: 배포 ID
        parameters: 실행 시 전달할 파라미터
        
    Returns:
        실행 결과
    """
    async with get_client() as client:
        try:
            if parameters is None:
                parameters = {}
                
            flow_run = await client.create_flow_run_from_deployment(
                deployment_id=deployment_id,
                parameters=parameters
            )
            
            return {
                "success": True,
                "message": f"배포가 성공적으로 실행되었습니다.",
                "flow_run_id": flow_run
            }
        except Exception as e:
            logger.error(f"배포 실행 중 오류: {e}")
            return {
                "success": False,
                "message": f"배포 실행 중 오류: {e}"
            }


async def get_all_deployments(
    flow_name: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    모든 배포 목록을 조회합니다.
    
    Args:
        flow_name: 플로우 이름으로 필터링
        tags: 태그로 필터링
        
    Returns:
        배포 목록
    """
    async with get_client() as client:
        # 필터 조건 구성
        query_filters = []
        
        if flow_name:
            query_filters.append({"name": {"like_": f"%{flow_name}%"}})
        
        if tags:
            for tag in tags:
                query_filters.append({"tags": {"contains_": [tag]}})
        
        # API 호출
        try:
            deployments = await client.read_deployments(deployments=query_filters)
            
            # 결과 가공
            result = []
            for deployment in deployments:
                # 스케줄 정보 가공
                schedule_info = None
                if deployment.schedule:
                    if hasattr(deployment.schedule, "interval"):
                        # IntervalSchedule인 경우
                        interval_seconds = deployment.schedule.interval.total_seconds()
                        schedule_info = f"매 {int(interval_seconds // 3600)}시간 {int((interval_seconds % 3600) // 60)}분마다"
                    elif hasattr(deployment.schedule, "cron"):
                        # CronSchedule인 경우
                        schedule_info = f"Cron: {deployment.schedule.cron}"
                
                result.append({
                    "id": deployment.id,
                    "name": deployment.name,
                    "flow_name": deployment.flow_name,
                    "schedule": schedule_info,
                    "is_schedule_active": deployment.is_schedule_active,
                    "tags": deployment.tags,
                    "work_pool_name": deployment.work_pool_name,
                })
            
            return result
        
        except Exception as e:
            logger.error(f"배포 목록 조회 중 오류: {e}")
            return [{"error": str(e)}]


async def get_flow_run_logs(flow_run_id: str) -> List[Dict[str, Any]]:
    """
    특정 플로우 실행의 로그를 조회합니다.
    
    Args:
        flow_run_id: 플로우 실행 ID
        
    Returns:
        로그 목록
    """
    async with get_client() as client:
        try:
            logs = await client.read_logs(flow_run_id=flow_run_id)
            
            # 결과 가공
            result = []
            for log in logs:
                result.append({
                    "level": log.level,
                    "timestamp": log.timestamp,
                    "message": log.message,
                    "task_run_id": log.task_run_id,
                })
            
            return result
        
        except Exception as e:
            logger.error(f"로그 조회 중 오류: {e}")
            return [{"error": str(e)}]


@task
async def check_prefect_server_health() -> Dict[str, Any]:
    """
    Prefect 서버의 상태를 확인합니다.
    
    Returns:
        서버 상태 정보
    """
    prefect_api_url = os.getenv("PREFECT_API_URL", "http://127.0.0.1:4200/api")
    health_url = f"{prefect_api_url.split('/api')[0]}/health"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(health_url, timeout=5.0)
            response.raise_for_status()
            
            return {
                "status": "healthy",
                "api_url": prefect_api_url,
                "health_check_response": response.json(),
                "timestamp": datetime.now().isoformat()
            }
    
    except httpx.RequestError as e:
        return {
            "status": "unhealthy",
            "error": f"요청 오류: {str(e)}",
            "api_url": prefect_api_url,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "api_url": prefect_api_url,
            "timestamp": datetime.now().isoformat()
        }


@flow(name="check-prefect-status-flow")
async def check_prefect_status() -> Dict[str, Any]:
    """
    Prefect 상태를 확인하는 플로우
    
    Returns:
        상태 정보
    """
    # 서버 상태 확인
    server_health = await check_prefect_server_health()
    
    if server_health["status"] == "healthy":
        # 배포 목록 조회
        deployments = await get_all_deployments()
        
        # 최근 실행 목록 조회
        recent_runs = await get_flow_runs(limit=5)
        
        return {
            "server_status": server_health,
            "deployments_count": len(deployments),
            "recent_runs": recent_runs,
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "server_status": server_health,
            "error": "Prefect 서버 연결 불가",
            "timestamp": datetime.now().isoformat()
        }


def save_flow_runs_to_file(
    flow_runs: List[Dict[str, Any]],
    output_file: Optional[Union[str, Path]] = None
) -> str:
    """
    플로우 실행 기록을 파일로 저장합니다.
    
    Args:
        flow_runs: 플로우 실행 목록
        output_file: 저장할 파일 경로 (None인 경우 자동 생성)
        
    Returns:
        저장된 파일 경로
    """
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"flow_runs_{timestamp}.json")
    else:
        output_file = Path(output_file)
    
    # 디렉토리 생성
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 파일 저장
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(flow_runs, f, indent=2, default=str)
    
    logger.info(f"플로우 실행 기록이 {output_file}에 저장되었습니다.")
    return str(output_file)


if __name__ == "__main__":
    # 모듈 직접 실행 시 Prefect 상태 확인
    result = asyncio.run(check_prefect_status())
    print(json.dumps(result, indent=2, default=str)) 