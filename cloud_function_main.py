import functions_framework
import requests
import json
from datetime import datetime, timedelta

@functions_framework.http
def get_institutional_investors(request):
    # ── CORS 設定（允許所有來源）──
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json; charset=utf-8'
    }

    # 處理 OPTIONS preflight
    if request.method == 'OPTIONS':
        return ('', 204, headers)

    # 取得股票代號參數
    stock_id = request.args.get('stock', '').strip()
    if not stock_id:
        return (json.dumps({'error': '請提供股票代號，例如 ?stock=2330'}, ensure_ascii=False), 400, headers)

    # 取近30個交易日資料（抓最近45天確保有30個交易日）
    results = []
    check_date = datetime.today()
    attempts = 0

    while len(results) < 30 and attempts < 60:
        date_str = check_date.strftime('%Y%m%d')

        try:
            # 上市股票用 TWSE
            url = f'https://www.twse.com.tw/rwd/zh/fund/T86?date={date_str}&selectType=ALLBUT0999&response=json'
            resp = requests.get(url, timeout=8, headers={
                'User-Agent': 'Mozilla/5.0'
            })
            data = resp.json()

            if data.get('stat') == 'OK' and data.get('data'):
                for row in data['data']:
                    # row[0]=股票代號, row[1]=股票名稱
                    # row[2]=外資買, row[3]=外資賣, row[4]=外資淨買賣
                    # row[5]=投信買, row[6]=投信賣, row[7]=投信淨買賣
                    # row[8]=自營商買(自買), row[9]=自營商賣(自買), row[10]=自營商淨(自買)
                    # row[11]=自營商買(避險), row[12]=自營商賣(避險), row[13]=自營商淨(避險)
                    # row[14]=三大法人合計
                    if row[0].strip() == stock_id:
                        def parse_num(s):
                            try:
                                return int(s.replace(',', '').replace('+', ''))
                            except:
                                return 0

                        results.append({
                            'date': f"{check_date.strftime('%Y/%m/%d')}",
                            'foreign': parse_num(row[4]),       # 外資
                            'investment_trust': parse_num(row[7]),  # 投信
                            'dealer_self': parse_num(row[10]),  # 自營(自買)
                            'dealer_hedge': parse_num(row[13]), # 自營(避險)
                            'total': parse_num(row[14])         # 三大合計
                        })
                        break

        except Exception as e:
            pass  # 假日或無資料，繼續往前一天

        check_date -= timedelta(days=1)
        attempts += 1

    if not results:
        # 嘗試 TPEX（上櫃股票）
        check_date = datetime.today()
        attempts = 0
        while len(results) < 30 and attempts < 60:
            try:
                y = check_date.year - 1911
                date_str = f"{y}/{check_date.strftime('%m/%d')}"
                url = f'https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php?l=zh-tw&se=AL&t=D&d={date_str}&s=0,asc&o=json'
                resp = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
                data = resp.json()

                if data.get('aaData'):
                    for row in data['aaData']:
                        if row[0].strip() == stock_id:
                            def parse_num(s):
                                try:
                                    return int(str(s).replace(',','').replace('+',''))
                                except:
                                    return 0
                            results.append({
                                'date': check_date.strftime('%Y/%m/%d'),
                                'foreign': parse_num(row[4]),
                                'investment_trust': parse_num(row[7]),
                                'dealer_self': parse_num(row[10]),
                                'dealer_hedge': parse_num(row[13]),
                                'total': parse_num(row[14])
                            })
                            break
            except:
                pass
            check_date -= timedelta(days=1)
            attempts += 1

    if not results:
        return (json.dumps({
            'error': f'找不到股票代號 {stock_id} 的資料，請確認代號是否正確'
        }, ensure_ascii=False), 404, headers)

    return (json.dumps({
        'stock_id': stock_id,
        'count': len(results),
        'data': results
    }, ensure_ascii=False), 200, headers)
