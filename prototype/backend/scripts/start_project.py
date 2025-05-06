#!/usr/bin/env python
"""
SNATCH 프로젝트 시작 스크립트

이 스크립트는 프로젝트 환경을 설정하고 필요한 서비스를 시작합니다.
- 필요한 패키지 설치
- Prefect 서버 시작
- Prefect 워크플로우 설정
- YouTube ETL 파이프라인 실행
"""
import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

# 스크립트 디렉토리
SCRIPT_DIR = Path(__file__).parent
# 프로젝트 루트 디렉토리
PROJECT_ROOT = SCRIPT_DIR.parent


def parse_arguments():
    """
    명령줄 인수를 파싱합니다.
    """
    parser = argparse.ArgumentParser(description="SNATCH 프로젝트 시작")
    
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="환경 설정만 하고 서비스는 시작하지 않습니다"
    )
    
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="패키지 설치 단계를 건너뜁니다"
    )
    
    parser.add_argument(
        "--skip-prefect",
        action="store_true",
        help="Prefect 서버 설정 단계를 건너뜁니다"
    )
    
    parser.add_argument(
        "--run-pipeline",
        action="store_true",
        help="YouTube ETL 파이프라인을 즉시 실행합니다"
    )
    
    parser.add_argument(
        "--deploy-only",
        action="store_true",
        help="파이프라인을 배포만 하고 실행하지 않습니다"
    )
    
    return parser.parse_args()


def run_script(script_name, args=None):
    """
    다른 Python 스크립트를 실행합니다.
    
    Args:
        script_name: 실행할 스크립트 이름
        args: 명령줄 인수
    """
    if args is None:
        args = []
    
    script_path = SCRIPT_DIR / script_name
    
    try:
        subprocess.run(
            [sys.executable, str(script_path)] + args,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"{script_name} 실행 중 오류 발생: {e}")
        return False


def check_env_file():
    """
    .env 파일이 있는지 확인하고, 없으면 .env.example을 복사합니다.
    """
    env_file = PROJECT_ROOT / ".env"
    env_example_file = PROJECT_ROOT / ".env.example"
    
    if not env_file.exists() and env_example_file.exists():
        print("\n.env 파일이 없습니다. .env.example을 복사합니다.")
        with open(env_example_file, "r") as src, open(env_file, "w") as dst:
            dst.write(src.read())
        print(".env 파일 생성 완료. API 키와 데이터베이스 정보를 설정해주세요.")
        return False
    elif not env_file.exists():
        print("\n.env 파일과 .env.example 파일이 모두 없습니다.")
        print("환경 변수 파일을 생성해주세요.")
        return False
    
    return True


def start_prefect_server():
    """
    Prefect 서버를 시작합니다.
    """
    print("\n=== Prefect 서버 시작 ===")
    
    # Prefect 서버 관리 스크립트 실행
    server_started = run_script("setup_prefect_server.py", ["--start-server"])
    
    if not server_started:
        print("Prefect 서버 시작에 실패했습니다.")
        return False
    
    # 서버가 실행 중인지 확인
    time.sleep(5)  # 서버 시작을 기다림
    
    try:
        result = subprocess.run(
            ["prefect", "config", "view"],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except:
        print("Prefect 서버가 실행되지 않았습니다.")
        return False


def setup_environment(skip_install=False):
    """
    환경을 설정합니다.
    
    Args:
        skip_install: 패키지 설치 단계 건너뛰기 여부
    """
    print("\n=== 환경 설정 시작 ===")
    
    # .env 파일 확인
    if not check_env_file():
        return False
    
    # 패키지 설치
    if not skip_install:
        print("\n=== 패키지 설치 ===")
        packages_installed = run_script("install_requirements.py")
        if not packages_installed:
            print("패키지 설치에 실패했습니다.")
            return False
    
    return True


def setup_prefect_workflow():
    """
    Prefect 워크플로우를 설정합니다.
    """
    print("\n=== Prefect 워크플로우 설정 ===")
    
    # Prefect 워크풀 생성
    pool_created = run_script("setup_prefect_server.py", ["--create-pool"])
    if not pool_created:
        print("Prefect 워크풀 생성에 실패했습니다.")
        return False
    
    # Prefect 워크플로우 설정
    workflow_setup = run_script("prefect_setup.py")
    if not workflow_setup:
        print("Prefect 워크플로우 설정에 실패했습니다.")
        return False
    
    return True


def run_youtube_pipeline():
    """
    YouTube ETL 파이프라인을 실행합니다.
    """
    print("\n=== YouTube ETL 파이프라인 실행 ===")
    
    return run_script("run_youtube_pipeline.py")


def main():
    """
    메인 함수
    """
    args = parse_arguments()
    
    # 환경 설정
    if not setup_environment(args.skip_install):
        print("환경 설정에 실패했습니다.")
        sys.exit(1)
    
    # 설정만 하고 종료
    if args.setup_only:
        print("환경 설정이 완료되었습니다.")
        sys.exit(0)
    
    # Prefect 서버 설정
    if not args.skip_prefect:
        if not start_prefect_server():
            print("Prefect 서버 설정에 실패했습니다.")
            sys.exit(1)
        
        if not setup_prefect_workflow():
            print("Prefect 워크플로우 설정에 실패했습니다.")
            sys.exit(1)
    
    # 배포만 하고 종료
    if args.deploy_only:
        print("파이프라인 배포가 완료되었습니다.")
        sys.exit(0)
    
    # 파이프라인 실행
    if args.run_pipeline:
        if not run_youtube_pipeline():
            print("YouTube ETL 파이프라인 실행에 실패했습니다.")
            sys.exit(1)
    
    print("\n모든 설정이 완료되었습니다. 프로젝트가 성공적으로 시작되었습니다.")


if __name__ == "__main__":
    main() 