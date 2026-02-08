import pandas as pd
import re
from pathlib import Path

def parse_pgn(val):
    if pd.isna(val): return None
    try:
        if isinstance(val, str) and (val.startswith('0x') or val.startswith('0X')):
            return int(val, 16)
        return int(float(val))
    except:
        return None

def main():
    da_path = '/home/ubuntu/workspace/SDM-VSS/data_sources/J1939DA_201710.xls'
    sig_path = '/home/ubuntu/workspace/SDM-VSS/data_sources/under_construction/j1939_signal_spec.csv'
    
    print("Loading J1939DA...")
    # Use SPNs & PGNs sheet for PGN definitions
    df_da = pd.read_excel(da_path, sheet_name='SPNs & PGNs', header=3)
    
    pgn_map = {}
    for _, row in df_da.iterrows():
        pgn = parse_pgn(row['PGN'])
        if pgn is not None:
            acronym = str(row['Acronym']).strip() if pd.notna(row['Acronym']) else ""
            label = str(row['Parameter Group Label']).strip() if pd.notna(row['Parameter Group Label']) else ""
            if pgn not in pgn_map:
                pgn_map[pgn] = {'acronym': acronym, 'label': label}

    print("Loading signal spec...")
    df_sig = pd.read_csv(sig_path)
    
    def normalize_pgn_hex(pgn_hex):
        try:
            return int(pgn_hex, 16)
        except:
            return None

    update_count = 0
    unique_pgns_updated = set()

    print("Improving standard PGNs based on J1939DA...")
    
    for idx, row in df_sig.iterrows():
        pgn_val = normalize_pgn_hex(row['pgn_hex'])
        
        if pgn_val in pgn_map:
            da_info = pgn_map[pgn_val]
            
            # Skip if it's a generic "Proprietary" label in DA
            if "Proprietary" in da_info['label']:
                continue
                
            new_acronym = da_info['acronym']
            new_desc = da_info['label']
            
            # Only update if DA info is meaningful
            if new_acronym and new_desc:
                # Update Acronym column
                # Wait, our CSV has 'message_acronym'
                df_sig.at[idx, 'message_acronym'] = new_acronym
                df_sig.at[idx, 'message_desc'] = new_desc
                
                # Update Message Name: {Acronym}_{Node}
                parts = str(row['message_name']).split('_')
                node = parts[-1] if len(parts) >= 2 else "Unknown"
                df_sig.at[idx, 'message_name'] = f"{new_acronym}_{node}"
                
                update_count += 1
                unique_pgns_updated.add(pgn_val)

    # Save
    df_sig.to_csv(sig_path, index=False)
    print(f"\n[결과 요약]")
    print(f"  업데이트된 행 수: {update_count}")
    print(f"  업데이트된 고유 PGN 수: {len(unique_pgns_updated)}")
    print(f"  대상 파일: {sig_path.split('/')[-1]}")

if __name__ == "__main__":
    main()

