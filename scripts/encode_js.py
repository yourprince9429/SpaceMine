import base64
import os
import json
from pathlib import Path


def encode_js_to_base64(js_file_path, output_dir='static/js_encoded'):
    js_file_path = Path(js_file_path)
    output_dir = Path(output_dir)
    
    if not js_file_path.exists():
        print(f"文件不存在: {js_file_path}")
        return None
    
    output_dir.mkdir(exist_ok=True)
    
    with open(js_file_path, 'rb') as f:
        js_content = f.read()
    
    encoded_content = base64.b64encode(js_content).decode('utf-8')
    
    output_file = output_dir / f"{js_file_path.stem}.json"
    
    metadata = {
        'original_file': str(js_file_path),
        'encoded_content': encoded_content,
        'size': len(js_content),
        'encoded_size': len(encoded_content)
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"已编码: {js_file_path}")
    print(f"原始大小: {len(js_content)} 字节")
    print(f"编码后大小: {len(encoded_content)} 字节")
    print(f"输出文件: {output_file}")
    
    return output_file


def encode_all_js_files(static_dir='static/js', output_dir='static/js_encoded'):
    static_dir = Path(static_dir)
    output_dir = Path(output_dir)
    
    if not static_dir.exists():
        print(f"目录不存在: {static_dir}")
        return
    
    js_files = list(static_dir.glob('*.js'))
    
    if not js_files:
        print(f"未找到JS文件: {static_dir}")
        return
    
    print(f"找到 {len(js_files)} 个JS文件")
    print("=" * 50)
    
    encoded_files = []
    for js_file in js_files:
        result = encode_js_to_base64(js_file, output_dir)
        if result:
            encoded_files.append(result)
    
    print("=" * 50)
    print(f"成功编码 {len(encoded_files)} 个文件")


if __name__ == '__main__':
    encode_all_js_files()
