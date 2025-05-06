import re
import json

def parse_jsonpair_file(file_path):
    """Parse the jsonPair.ini file and convert it to JSONL format."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 각 Pair 블록 찾기
    pair_pattern = r'Pair \d+\s*(?:\(.*?\))?\s*\n(.*?)(?=Pair \d+|$)'
    pair_matches = re.finditer(pair_pattern, content, re.DOTALL)
    
    jsonl_lines = []
    pair_count = 0
    error_count = 0
    
    for match in pair_matches:
        pair_count += 1
        block = match.group(1).strip()
        
        # Extract text_input
        text_input_match = re.search(r'text_input:(.*?)output:', block, re.DOTALL)
        if not text_input_match:
            print(f"Cannot find text_input in pair {pair_count}")
            continue
            
        text_input = text_input_match.group(1).strip()
        
        # Extract output JSON - 더 정확한 패턴으로 수정
        output_start = block.find('output:')
        if output_start == -1:
            print(f"Cannot find output section in pair {pair_count}")
            continue
            
        json_text = block[output_start + len('output:'):].strip()
        
        # IGNORE_WHEN_COPYING_START까지의 텍스트를 추출
        ignore_start = json_text.find('IGNORE_WHEN_COPYING_START')
        if ignore_start != -1:
            json_text = json_text[:ignore_start].strip()
        
        # JSON 객체 찾기
        json_match = re.search(r'(\{.*\})', json_text, re.DOTALL)
        if not json_match:
            print(f"Cannot find valid JSON in pair {pair_count}")
            continue
            
        output_json_str = json_match.group(1).strip()
        
        try:
            # JSON 유효성 검사 및 처리
            output_json = json.loads(output_json_str)
            
            # JSONL 항목 생성
            jsonl_entry = {
                "text_input": text_input,
                "output": json.dumps(output_json, ensure_ascii=False)
            }
            
            # 목록에 추가
            jsonl_lines.append(json.dumps(jsonl_entry, ensure_ascii=False))
        except json.JSONDecodeError as e:
            error_count += 1
            print(f"Error parsing JSON in pair {pair_count}: {e}")
            print(f"Problematic JSON: {output_json_str[:100]}...")
    
    print(f"Total pairs found: {pair_count}, Successful conversions: {len(jsonl_lines)}, Errors: {error_count}")
    return jsonl_lines

def save_jsonl(jsonl_lines, output_file):
    """Save the JSONL lines to a file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in jsonl_lines:
            f.write(line + '\n')

if __name__ == "__main__":
    input_file = "jsonPair.ini"
    output_file = "converted_data.jsonl"
    
    jsonl_lines = parse_jsonpair_file(input_file)
    save_jsonl(jsonl_lines, output_file)
    
    print(f"Conversion complete. {len(jsonl_lines)} pairs converted to {output_file}") 