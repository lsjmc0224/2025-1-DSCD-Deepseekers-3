#!/usr/bin/env python
"""
Prefect 서버 설치 및 실행 스크립트

이 스크립트는 Prefect 서버를 설치하고 실행하는 데 필요한 단계를 자동화합니다.
"""
import os
import sys
import subprocess
import time
import argparse
from pathlib import Path

# 상위 디렉토리를 경로에 추가하여 모듈 임포트 가능하게 함
sys.path.insert(0, str(Path(__file__).parent.parent))


def parse_arguments():
    """
    명령줄 인수를 파싱합니다.
    """
    parser = argparse.ArgumentParser(description="Prefect 서버 설치 및 실행")
    
    parser.add_argument(
        "--install-only",
        action="store_true",
        help="Prefect만 설치하고 서버는 실행하지 않습니다"
    )
    
    parser.add_argument(
        "--start-server",
        action="store_true",
        help="Prefect 서버만 시작합니다 (설치 과정 생략)"
    )
    
    parser.add_argument(
        "--create-pool",
        action="store_true",
        help="워크풀을 생성합니다"
    )
    
    parser.add_argument(
        "--pool-name",
        type=str,
        default="sweetspot-pool",
        help="생성할 워크풀 이름 (기본값: sweetspot-pool)"
    )
    
    return parser.parse_args()


def check_prefect_installed():
    """
    Prefect가 설치되어 있는지 확인합니다.
    """
    try:
        result = subprocess.run(
            ["prefect", "--version"], 
            capture_output=True, 
            text=True, 
            check=False
        )
        if result.returncode == 0:
            print(f"Prefect {result.stdout.strip()} 설치되어 있습니다.")
            return True
        return False
    except FileNotFoundError:
        return False


def install_prefect():
    """
    Prefect를 설치합니다.
    """
    if check_prefect_installed():
        print("Prefect가 이미 설치되어 있습니다.")
        return
    
    print("Prefect 설치 중...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "prefect>=2.0.0"],
            check=True
        )
        print("Prefect 설치 완료!")
    except subprocess.CalledProcessError as e:
        print(f"Prefect 설치 중 오류 발생: {e}")
        sys.exit(1)


def install_dependencies():
    """
    필요한 추가 패키지를 설치합니다.
    """
    print("필요한 패키지 설치 중...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "httpx", "python-dotenv"],
            check=True
        )
        print("패키지 설치 완료!")
    except subprocess.CalledProcessError as e:
        print(f"패키지 설치 중 오류 발생: {e}")
        sys.exit(1)


def start_prefect_server():
    """
    Prefect 서버를 시작합니다.
    """
    print("Prefect 서버 시작 중...")
    try:
        # 서버 실행을 위한 프로세스 시작 (백그라운드로 실행)
        server_process = subprocess.Popen(
            ["prefect", "server", "start"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 서버가 시작될 때까지 기다림
        print("Prefect 서버가 시작되기를 기다리는 중...")
        time.sleep(5)  # 서버 시작 대기
        
        # 서버 상태 확인
        for _ in range(5):  # 최대 5번 시도
            try:
                result = subprocess.run(
                    ["prefect", "config", "view"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print("Prefect 서버가 성공적으로 시작되었습니다!")
                print("\n서버를 종료하려면 Ctrl+C를 누르세요.\n")
                break
            except subprocess.CalledProcessError:
                print("서버 상태 확인 중... 잠시 기다려주세요.")
                time.sleep(2)
        
        # 서버 프로세스가 계속 실행되도록 유지
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\nPrefect 서버를 종료합니다...")
            server_process.terminate()
            server_process.wait()
            print("Prefect 서버가 종료되었습니다.")
        
    except Exception as e:
        print(f"Prefect 서버 시작 중 오류 발생: {e}")
        sys.exit(1)


def create_work_pool(pool_name):
    """
    워크풀을 생성합니다.
    """
    print(f"'{pool_name}' 워크풀 생성 중...")
    try:
        # 기존 워크풀 확인
        result = subprocess.run(
            ["prefect", "work-pool", "ls"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # 워크풀이 이미 존재하는지 확인
        if pool_name in result.stdout:
            print(f"'{pool_name}' 워크풀이 이미 존재합니다.")
            return
        
        # 워크풀 생성
        subprocess.run(
            ["prefect", "work-pool", "create", pool_name, "--type", "process"],
            check=True
        )
        print(f"'{pool_name}' 워크풀 생성 완료!")
        
    except subprocess.CalledProcessError as e:
        print(f"워크풀 생성 중 오류 발생: {e}")
        sys.exit(1)


def main():
    """
    메인 함수
    """
    args = parse_arguments()
    
    if args.start_server:
        # 서버만 시작
        start_prefect_server()
    elif args.create_pool:
        # 워크풀만 생성
        create_work_pool(args.pool_name)
    else:
        # 설치 및 서버 시작
        install_prefect()
        install_dependencies()
        
        if not args.install_only:
            start_prefect_server()


if __name__ == "__main__":
    main() 