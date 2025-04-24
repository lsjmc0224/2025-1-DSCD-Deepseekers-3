#!/usr/bin/env python
"""
SNATCH 프로젝트 패키지 설치 스크립트

이 스크립트는 프로젝트에 필요한 모든 Python 패키지를 설치합니다.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# 필수 패키지 목록
REQUIRED_PACKAGES = [
    "fastapi>=0.95.0",
    "uvicorn>=0.21.1",
    "sqlalchemy>=2.0.9",
    "alembic>=1.10.3",
    "pydantic>=1.10.7",
    "httpx>=0.24.0",
    "python-dotenv>=1.0.0",
    "asyncpg>=0.27.0",
    "psycopg2-binary>=2.9.6",
    "backoff>=2.2.1",
    "prefect>=2.10.5",
    "youtube-transcript-api>=0.6.0",
    "nltk>=3.8.1",
    "scikit-learn>=1.2.2",
    "pandas>=2.0.0",
    "numpy>=1.24.3",
    "matplotlib>=3.7.1",
    "google-api-python-client>=2.86.0",
    "google-auth>=2.17.3",
    "google-auth-httplib2>=0.1.0",
    "google-auth-oauthlib>=1.0.0",
]

# 개발용 패키지 목록
DEV_PACKAGES = [
    "pytest>=7.3.1",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.3.0",
    "isort>=5.12.0",
    "mypy>=1.2.0",
    "flake8>=6.0.0",
    "pre-commit>=3.3.1",
]


def parse_arguments():
    """
    명령줄 인수를 파싱합니다.
    """
    parser = argparse.ArgumentParser(description="SNATCH 프로젝트 패키지 설치")
    
    parser.add_argument(
        "--dev",
        action="store_true",
        help="개발용 패키지도 함께 설치합니다"
    )
    
    parser.add_argument(
        "--upgrade",
        action="store_true",
        help="이미 설치된 패키지도 최신 버전으로 업그레이드합니다"
    )
    
    return parser.parse_args()


def install_packages(packages, upgrade=False):
    """
    패키지 목록을 설치합니다.
    
    Args:
        packages: 설치할 패키지 목록
        upgrade: 패키지 업그레이드 여부
    """
    # pip 업그레이드
    print("pip 최신 버전 확인 중...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"pip 업그레이드 중 오류 발생: {e}")
    
    # 패키지 설치
    pip_cmd = [sys.executable, "-m", "pip", "install"]
    if upgrade:
        pip_cmd.append("--upgrade")
    
    print(f"\n{len(packages)}개 패키지 설치 중...")
    
    for package in packages:
        try:
            print(f"패키지 설치 중: {package}")
            subprocess.run(pip_cmd + [package], check=True)
        except subprocess.CalledProcessError as e:
            print(f"패키지 {package} 설치 중 오류 발생: {e}")
    
    print("\n패키지 설치 완료!")


def generate_requirements_file(packages, filename="requirements.txt"):
    """
    requirements.txt 파일을 생성합니다.
    
    Args:
        packages: 패키지 목록
        filename: 파일명
    """
    filepath = Path(__file__).parent.parent / filename
    
    with open(filepath, "w") as f:
        for package in packages:
            f.write(f"{package}\n")
    
    print(f"\n{filepath} 파일 생성 완료!")


def main():
    """
    메인 함수
    """
    args = parse_arguments()
    
    # 설치할 패키지 목록 준비
    packages_to_install = REQUIRED_PACKAGES.copy()
    
    if args.dev:
        packages_to_install.extend(DEV_PACKAGES)
        print("필수 패키지와 개발용 패키지를 설치합니다.")
    else:
        print("필수 패키지만 설치합니다.")
    
    # 패키지 설치
    install_packages(packages_to_install, args.upgrade)
    
    # requirements.txt 파일 생성
    if args.dev:
        # requirements-dev.txt 파일 생성
        all_packages = REQUIRED_PACKAGES + DEV_PACKAGES
        generate_requirements_file(all_packages, "requirements-dev.txt")
        # requirements.txt 파일 생성
        generate_requirements_file(REQUIRED_PACKAGES, "requirements.txt")
    else:
        # requirements.txt 파일만 생성
        generate_requirements_file(REQUIRED_PACKAGES)


if __name__ == "__main__":
    main() 