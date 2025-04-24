#!/usr/bin/env python
"""
Prefect 모니터링 스크립트

이 스크립트는 Prefect 서버, 워크플로우, 실행 상태를 모니터링하고 보고합니다.
"""
import os
import sys
import json
import time
import asyncio
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# 상위 디렉토리를 경로에 추가하여 모듈 임포트 가능하게 함
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.prefect_utils import (
    check_prefect_status,
    get_flow_runs,
    get_all_deployments,
    get_flow_run_logs,
    save_flow_runs_to_file
)


def parse_args():
    """
    명령줄 인수를 파싱합니다.
    """
    parser = argparse.ArgumentParser(description="Prefect 워크플로우 모니터링")
    
    subparsers = parser.add_subparsers(dest="command", help="명령")
    
    # 상태 확인 명령
    status_parser = subparsers.add_parser("status", help="서버 및 워크플로우 상태 확인")
    
    # 실행 기록 조회 명령
    runs_parser = subparsers.add_parser("runs", help="플로우 실행 기록 조회")
    runs_parser.add_argument("--flow", help="플로우 이름으로 필터링")
    runs_parser.add_argument("--deployment", help="배포 ID로 필터링")
    runs_parser.add_argument("--limit", type=int, default=10, help="조회할 최대 건수")
    runs_parser.add_argument("--status", choices=["COMPLETED", "FAILED", "RUNNING", "PENDING"], 
                           help="상태로 필터링")
    runs_parser.add_argument("--save", action="store_true", help="결과를 파일로 저장")
    runs_parser.add_argument("--output", help="저장할 파일 경로")
    
    # 배포 목록 조회 명령
    deployments_parser = subparsers.add_parser("deployments", help="배포 목록 조회")
    deployments_parser.add_argument("--flow", help="플로우 이름으로 필터링")
    deployments_parser.add_argument("--tag", action="append", help="태그로 필터링 (여러 번 사용 가능)")
    
    # 로그 조회 명령
    logs_parser = subparsers.add_parser("logs", help="플로우 실행 로그 조회")
    logs_parser.add_argument("flow_run_id", help="플로우 실행 ID")
    
    # 연속 모니터링 명령
    watch_parser = subparsers.add_parser("watch", help="상태 연속 모니터링")
    watch_parser.add_argument("--interval", type=int, default=30, 
                            help="갱신 간격 (초, 기본값: 30)")
    watch_parser.add_argument("--count", type=int, default=0, 
                            help="모니터링 횟수 (0은 무제한)")
    
    return parser.parse_args()


def format_datetime(dt_str: Optional[str]) -> str:
    """
    ISO 형식 날짜/시간 문자열을 가독성 있는 형식으로 변환합니다.
    """
    if not dt_str:
        return "-"
    
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        local_dt = dt + timedelta(hours=9)  # KST로 변환
        return local_dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_str


def print_status_info(status_info: Dict[str, Any]):
    """
    상태 정보를 출력합니다.
    """
    print("\n=== Prefect 서버 상태 ===")
    server_status = status_info.get("server_status", {})
    
    if server_status.get("status") == "healthy":
        print(f"서버 상태: 정상")
        print(f"API URL: {server_status.get('api_url')}")
        print(f"배포 수: {status_info.get('deployments_count', 0)}")
        
        print("\n=== 최근 실행 목록 ===")
        runs = status_info.get("recent_runs", [])
        
        if runs:
            for run in runs:
                name = run.get("name", "알 수 없음")
                status = run.get("status", "알 수 없음")
                started = format_datetime(run.get("started"))
                finished = format_datetime(run.get("finished"))
                
                status_emoji = "✅" if status == "COMPLETED" else "❌" if status == "FAILED" else "⏳"
                print(f"{status_emoji} {name} ({status}) - 시작: {started}, 종료: {finished}")
        else:
            print("최근 실행 내역이 없습니다.")
    else:
        print(f"서버 상태: 오류 - {server_status.get('error', '알 수 없는 오류')}")


def print_flow_runs(runs: List[Dict[str, Any]]):
    """
    플로우 실행 기록을 출력합니다.
    """
    if not runs:
        print("조회된 실행 기록이 없습니다.")
        return
    
    print(f"\n=== 플로우 실행 기록 ({len(runs)}건) ===")
    print(f"{'상태':^10} {'이름':^30} {'시작 시간':^20} {'종료 시간':^20}")
    print("-" * 80)
    
    for run in runs:
        status = run.get("status", "알 수 없음")
        name = run.get("name", "알 수 없음")
        if len(name) > 28:
            name = name[:25] + "..."
            
        started = format_datetime(run.get("started"))
        finished = format_datetime(run.get("finished"))
        
        status_color = ""
        if status == "COMPLETED":
            status_color = "\033[92m"  # 초록색
        elif status == "FAILED":
            status_color = "\033[91m"  # 빨간색
        elif status == "RUNNING":
            status_color = "\033[93m"  # 노란색
            
        reset_color = "\033[0m" if status_color else ""
        
        print(f"{status_color}{status:^10}{reset_color} {name:^30} {started:^20} {finished:^20}")


def print_deployments(deployments: List[Dict[str, Any]]):
    """
    배포 목록을 출력합니다.
    """
    if not deployments:
        print("조회된 배포가 없습니다.")
        return
    
    print(f"\n=== 배포 목록 ({len(deployments)}건) ===")
    print(f"{'이름':^30} {'플로우':^30} {'스케줄':^20} {'활성화':^10}")
    print("-" * 90)
    
    for deployment in deployments:
        name = deployment.get("name", "알 수 없음")
        if len(name) > 28:
            name = name[:25] + "..."
            
        flow_name = deployment.get("flow_name", "알 수 없음")
        if len(flow_name) > 28:
            flow_name = flow_name[:25] + "..."
            
        schedule = deployment.get("schedule", "-")
        is_active = "활성" if deployment.get("is_schedule_active") else "비활성"
        
        print(f"{name:^30} {flow_name:^30} {schedule:^20} {is_active:^10}")


def print_logs(logs: List[Dict[str, Any]]):
    """
    플로우 실행 로그를 출력합니다.
    """
    if not logs:
        print("조회된 로그가 없습니다.")
        return
    
    print(f"\n=== 플로우 실행 로그 ({len(logs)}건) ===")
    
    for log in logs:
        level = log.get("level", "INFO")
        timestamp = format_datetime(log.get("timestamp"))
        message = log.get("message", "")
        
        level_color = ""
        if level == "ERROR":
            level_color = "\033[91m"  # 빨간색
        elif level == "WARNING":
            level_color = "\033[93m"  # 노란색
        elif level == "INFO":
            level_color = "\033[92m"  # 초록색
            
        reset_color = "\033[0m" if level_color else ""
        
        print(f"{timestamp} {level_color}{level:7}{reset_color} {message}")


async def handle_status_command():
    """
    status 명령을 처리합니다.
    """
    status_info = await check_prefect_status()
    print_status_info(status_info)


async def handle_runs_command(args):
    """
    runs 명령을 처리합니다.
    """
    status_list = None
    if args.status:
        status_list = [args.status]
        
    runs = await get_flow_runs(
        flow_name=args.flow,
        deployment_id=args.deployment,
        limit=args.limit,
        status=status_list
    )
    
    print_flow_runs(runs)
    
    if args.save:
        output_file = args.output
        saved_file = save_flow_runs_to_file(runs, output_file)
        print(f"\n실행 기록이 {saved_file}에 저장되었습니다.")


async def handle_deployments_command(args):
    """
    deployments 명령을 처리합니다.
    """
    deployments = await get_all_deployments(flow_name=args.flow, tags=args.tag)
    print_deployments(deployments)


async def handle_logs_command(args):
    """
    logs 명령을 처리합니다.
    """
    logs = await get_flow_run_logs(args.flow_run_id)
    print_logs(logs)


async def handle_watch_command(args):
    """
    watch 명령을 처리합니다.
    """
    count = 0
    interval = max(5, args.interval)  # 최소 5초
    max_count = args.count if args.count > 0 else float('inf')
    
    try:
        while count < max_count:
            # 화면 지우기
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # 현재 시간
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{now}] Prefect 모니터링 (간격: {interval}초, {count+1}/{args.count if args.count > 0 else '무제한'})")
            
            # 상태 확인
            status_info = await check_prefect_status()
            print_status_info(status_info)
            
            count += 1
            if count < max_count:
                print(f"\n{interval}초 후 갱신됩니다. (Ctrl+C로 종료)")
                time.sleep(interval)
    except KeyboardInterrupt:
        print("\n모니터링을 종료합니다.")


async def main():
    """
    메인 함수
    """
    args = parse_args()
    
    if args.command == "status":
        await handle_status_command()
    elif args.command == "runs":
        await handle_runs_command(args)
    elif args.command == "deployments":
        await handle_deployments_command(args)
    elif args.command == "logs":
        await handle_logs_command(args)
    elif args.command == "watch":
        await handle_watch_command(args)
    else:
        print("명령을 지정해주세요. --help 옵션으로 사용법을 확인하세요.")


if __name__ == "__main__":
    asyncio.run(main()) 