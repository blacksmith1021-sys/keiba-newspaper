"""
バックテスト: CSVデータの人気×着順分布を分析
使い方: python3 backtest.py data/keiba_enriched.csv
"""
import csv, sys
from collections import defaultdict

def load_csv(path):
    with open(path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        races = defaultdict(list)
        for row in reader:
            key = f"{row['日付']}_{row['競馬場']}_{row.get('レース番号', row.get('レース',''))}"
            races[key].append(row)
    return races

def evaluate(races):
    total = 0
    pop_top3 = defaultdict(lambda: [0,0])  # pop -> [total, in_top3]

    for key, horses in races.items():
        if len(horses) < 3: continue
        total += 1
        for h in horses:
            pop = int(float(h.get('人気','99') or '99'))
            fin = int(float(h.get('実際着順','99') or '99'))
            if pop > 0 and pop <= 18:
                pop_top3[pop][0] += 1
                if fin <= 3:
                    pop_top3[pop][1] += 1

    print(f"=== 人気別 複勝率 ===")
    print(f"レース数: {total}")
    print(f"{'人気':>4} {'出走':>6} {'3着以内':>6} {'複勝率':>7}")
    for pop in sorted(pop_top3.keys()):
        t, h = pop_top3[pop]
        print(f"{pop:>4} {t:>6} {h:>6} {h/t*100:>6.1f}%")

    # 穴馬ゾーン（7-10人気）
    ana_t = sum(pop_top3[p][0] for p in range(7,11))
    ana_h = sum(pop_top3[p][1] for p in range(7,11))
    print(f"\n穴馬ゾーン(7-10人気): {ana_h}/{ana_t} = {ana_h/ana_t*100:.1f}%" if ana_t else "")

    # CSVにスコアがある場合の分析
    scored_races = 0
    top1_in3 = 0
    for key, horses in races.items():
        scored = [(h, int(float(h.get('補正スコア','0') or '0'))) for h in horses]
        scored.sort(key=lambda x: -x[1])
        if scored[0][1] <= 0: continue
        if len(scored) < 3: continue
        scored_races += 1
        fin = int(float(scored[0][0].get('実際着順','99') or '99'))
        if fin <= 3: top1_in3 += 1

    if scored_races:
        print(f"\nスコアあり {scored_races}R: 1位3着以内率 {top1_in3/scored_races*100:.1f}%")

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'data/keiba_enriched.csv'
    races = load_csv(path)
    evaluate(races)
