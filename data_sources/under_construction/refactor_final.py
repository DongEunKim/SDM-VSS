import pandas as pd
from pathlib import Path

def main():
    encoder_path = Path('/home/ubuntu/workspace/SDM-VSS/data_sources/2025.11.19/J1939_Encoder.csv')
    spec_path = Path('/home/ubuntu/workspace/SDM-VSS/data_sources/under_construction/j1939_signal_spec.csv')
    
    if not encoder_path.exists() or not spec_path.exists():
        print("Error: 필요한 파일을 찾을 수 없습니다.")
        return

    # 1. 원본 인코더 데이터 로드 및 매핑 생성
    print("원본 인코더 데이터 로드 중...")
    df_enc = pd.read_csv(encoder_path)
    
    # SPN + NAME(signal_name) -> {PGN_ACYM, PGN_COMMENT, NODE} 맵 생성
    # 인코더의 NODE가 전송노드명임
    enc_map = {}
    for _, row in df_enc.iterrows():
        key = (int(row['SPN']), str(row['NAME']).strip())
        enc_map[key] = {
            'acronym': str(row['PGN_ACYM']).strip(),
            'desc': str(row['PGN_COMMENT']).strip() if pd.notna(row['PGN_COMMENT']) else "",
            'node': str(row['NODE']).strip()
        }

    # 2. 대상 시그널 스펙 로드
    print("대상 시그널 스펙 리팩토링 중...")
    df_sig = pd.read_csv(spec_path)
    
    new_names = []
    acronyms = []
    descs = []
    
    for _, row in df_sig.iterrows():
        key = (int(row['spn']), str(row['signal_name']).strip())
        
        if key in enc_map:
            info = enc_map[key]
            # {PGN약어}_{전송노드명}
            new_names.append(f"{info['acronym']}_{info['node']}")
            acronyms.append(info['acronym'])
            descs.append(info['desc'])
        else:
            # 매칭 실패 시 (이론적으로 발생하면 안됨)
            new_names.append(row['message_name'])
            acronyms.append("")
            descs.append("")

    # 3. 데이터 업데이트 및 컬럼 순서 조정
    df_sig['message_name'] = new_names
    df_sig['message_acronym'] = acronyms
    df_sig['message_desc'] = descs
    
    # 헤더 순서 재배치 (bus 뒤에 신규 컬럼 배치)
    cols = df_sig.columns.tolist()
    # 신규 컬럼들 위치 조정
    cols.remove('message_acronym')
    cols.remove('message_desc')
    
    # message_name 바로 뒤에 삽입
    idx = cols.index('message_name') + 1
    cols.insert(idx, 'message_acronym')
    cols.insert(idx + 1, 'message_desc')
    
    df_sig = df_sig[cols]
    
    # 4. 저장
    df_sig.to_csv(spec_path, index=False)
    
    print("\n[리팩토링 완료]")
    print(f"  총 {len(df_sig)}개 신호 업데이트 완료")
    print("\n데이터 샘플 확인:")
    print(df_sig[['bus', 'message_name', 'message_acronym', 'message_desc']].head(10))

if __name__ == '__main__':
    main()

