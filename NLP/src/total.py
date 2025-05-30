import argparse
import yaml
import subprocess
import time
from pathlib import Path
"""
total.py — 한 번에 파이프라인 전체 ( 텍스트 클리닝 → 문장 분리 → 감성 분류 → 키워드 분류 > 최종 결과 저장)  돌려주는 스크립트
  • 역할: 텍스트 클리닝 → 문장 분리 → 감성 분류 → 키워드 분류
  • 사용법:
      python total.py --config C:/Users/parkm/NLP/config/default.yaml
  • config에:  input/output 경로, 모델 경로, 배치 크기 
  • 중간 결과는 지정된 intermediate_dir에 step1~step3.csv로 저장됨.
"""



def run_step(script_path, args):
    """
    ▶ 주어진 스크립트를 실행하고, 소요 시간을 반환
    """
    cmd = ['python', str(script_path)] + args
    print(f"\n--- Running: {' '.join(cmd)}")
    start = time.perf_counter()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.perf_counter() - start

    if result.returncode != 0:
        print(f"[Error] {script_path.name} 실행 중 오류 발생:\n{result.stderr}")
        exit(1)
    else:
        print(result.stdout)
        print(f"[Info] {script_path.name} 완료: {elapsed:.2f}s 소요")
        return elapsed

def main(config_path: Path):
    """
    ▶ 파이프라인 메인 함수
    1) config YAML 파일 로드
    2) 설정에 맞춰 intermediate 폴더에 중간결과 저장됨
    3) 4단계 스크립트 순차적으로 실행 후 
    4) 단계별 및 총 소요 시간 + 완료 메시지 출력
    """
    #1) 설정 로드
    cfg = yaml.safe_load(config_path.read_text(encoding='utf-8'))
    data_cfg  = cfg['data']
    paths_cfg = cfg['paths']

    # 2) config에서 경로 꺼내기
    input_csv    = Path(data_cfg['input_csv'])            # 최초 원본 CSV
    intermediate = Path(data_cfg['intermediate_dir'])     # 중간 결과 폴더
    output_csv   = Path(data_cfg['output_csv'])           # 최종 저장 CSV
    scripts_dir  = Path(paths_cfg['scripts_dir'])         # 모듈(.py) 위치
    model_dir    = paths_cfg['model_dir']                 # KcELECTRA 모델 폴더 config.json 이런거 5개

    # 중간 결과 저장할 폴더없으면 자동생성
    intermediate.mkdir(parents=True, exist_ok=True)

    
    
    total_start = time.perf_counter()
    durations = {}


     # ── 1) 텍스트 클리닝 ─────────────────────────────────────────────
    clean_out = intermediate / 'step1_clean.csv'
    durations['clean']  = run_step(
        scripts_dir / 'text_cleaner.py',
        ['--input', str(input_csv), '--output', str(clean_out)]
    )

    # ── 2) 문장 분리 ────────────────────────────────────────────────
    #    ID, (작성시간), cleaned 칼럼을 받아 divided_comment로 분리
    split_out = intermediate / 'step2_split.csv'
    durations['split']  = run_step(
        scripts_dir / 'sentence_splitter.py',
        [
            '--input',      str(clean_out),
            '--output',     str(split_out),
            '--id-col',     data_cfg.get('id_col', 'ID'),
            '--time-col',   data_cfg.get('time_col', ''),
            '--text-col',   'cleaned',
            '--output-col', 'divided_comment'
        ]
    )

     # ── 3) 감성 분류 ────────────────────────────────────────────────
    senti_out = intermediate / 'step3_sentiment.csv'
    durations['sentiment'] = run_step(
        scripts_dir / 'sentiment.py',
        [
            '--input',      str(split_out),
            '--output',     str(senti_out),
            '--model-dir',  model_dir,
            '--text-col',   'divided_comment',
            '--output-col','sentiment',
            '--max-length', str(cfg['sentiment']['max_length']),
            '--batch-size', str(cfg['sentiment']['batch_size'])
        ]
    )

    # ── 4) 키워드 분류 ────────────────────────────────────────────────
    durations['keyword'] = run_step(
        scripts_dir / 'keyword_classifier.py',
        [
            '--input',     str(senti_out),
            '--output',    str(output_csv),
            '--text-col',  'divided_comment'
        ]
    )
    total_elapsed = time.perf_counter() - total_start

    print("\n=== TIME REPORT ===")
    print(f"1) 텍스트 클리닝 : {durations['clean']:.2f}s")
    print(f"2) 문장 분리     : {durations['split']:.2f}s")
    print(f"3) 감성 분류     : {durations['sentiment']:.2f}s")
    print(f"4) 키워드 분류   : {durations['keyword']:.2f}s")
    print(f"-----------------------------")
    print(f"총 소요 시간     : {total_elapsed:.2f}s")

    print(f"\n 텍스트 클리닝 → 문장 분리 → 감성 분류 → 키워드 분류 끝... Final output : {output_csv}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='한 번에 전체 파이프라인 실행하는 스크립트')
    parser.add_argument(
        '--config', '-c',
        default='C:/Users/parkm/NLP/config/default.yaml',
        help='config YAML 파일 경로 (기본: C:/Users/parkm/NLP/config/default.yaml)'
    )
    args = parser.parse_args()
    main(Path(args.config))
