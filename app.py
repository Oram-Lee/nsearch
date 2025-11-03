"""
네이버 부동산 크롤러 Flask API
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import pandas as pd
import time
import random
from datetime import datetime
import urllib3
import io
import os

# SSL 경고 메시지 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)  # CORS 허용

# ============================================
# 유틸리티 함수
# ============================================

PYEONG_TO_SQM = 3.3058

def pyeong_to_sqm(pyeong):
    """평을 제곱미터로 변환"""
    return round(pyeong * PYEONG_TO_SQM, 2)

def sqm_to_pyeong(sqm):
    """제곱미터를 평으로 변환"""
    return round(sqm / PYEONG_TO_SQM, 2)

# 지역 코드 및 좌표 정보
REGION_COORDS = {
    "1168000000": {"name": "강남구", "lat": 37.5172, "lon": 127.0473},
    "1171000000": {"name": "송파구", "lat": 37.5145, "lon": 127.1059},
    "1165000000": {"name": "서초구", "lat": 37.4837, "lon": 127.0324},
    "1174000000": {"name": "강동구", "lat": 37.5301, "lon": 127.1238},
    "1156000000": {"name": "영등포구", "lat": 37.5264, "lon": 126.8962},
    "1150000000": {"name": "강서구", "lat": 37.5509, "lon": 126.8495},
    "1144000000": {"name": "마포구", "lat": 37.5663, "lon": 126.9019},
    "1141000000": {"name": "서대문구", "lat": 37.5791, "lon": 126.9368},
    "1120000000": {"name": "성동구", "lat": 37.5634, "lon": 127.0368},
    "1121500000": {"name": "광진구", "lat": 37.5384, "lon": 127.0822},
    "1123000000": {"name": "동대문구", "lat": 37.5744, "lon": 127.0396},
    "1126000000": {"name": "중랑구", "lat": 37.6063, "lon": 127.0925},
    "1129000000": {"name": "성북구", "lat": 37.5894, "lon": 127.0167},
    "1130500000": {"name": "강북구", "lat": 37.6397, "lon": 127.0256},
    "1132000000": {"name": "도봉구", "lat": 37.6688, "lon": 127.0471},
    "1135000000": {"name": "노원구", "lat": 37.6542, "lon": 127.0568},
    "1138000000": {"name": "은평구", "lat": 37.6027, "lon": 126.9291},
    "1147000000": {"name": "양천구", "lat": 37.5170, "lon": 126.8664},
    "1153000000": {"name": "구로구", "lat": 37.4954, "lon": 126.8874},
    "1154500000": {"name": "금천구", "lat": 37.4519, "lon": 126.8955},
    "1159000000": {"name": "동작구", "lat": 37.5124, "lon": 126.9393},
    "1162000000": {"name": "관악구", "lat": 37.4784, "lon": 126.9516},
    "1111000000": {"name": "종로구", "lat": 37.5735, "lon": 126.9788},
    "1114000000": {"name": "중구", "lat": 37.5641, "lon": 126.9979},
    "1117000000": {"name": "용산구", "lat": 37.5324, "lon": 126.9905},
}

def get_region_bounds(region_code):
    """지역 코드로부터 좌표 범위 계산"""
    if region_code in REGION_COORDS:
        coord = REGION_COORDS[region_code]
        lat = coord["lat"]
        lon = coord["lon"]
        
        delta = 0.05
        
        return {
            "lat": lat,
            "lon": lon,
            "btm": lat - delta,
            "lft": lon - delta,
            "top": lat + delta,
            "rgt": lon + delta,
            "z": 14
        }
    return None

# ============================================
# 크롤링 함수
# ============================================

def crawl_naver_land_v1(region_code, property_types, trade_types, min_area_sqm, max_area_sqm, page=1):
    """방법 1: cortarNo 기반 검색"""
    url = "https://m.land.naver.com/cluster/ajax/articleList"
    
    rlet_tp_cd = ":".join(property_types)
    trad_tp_cd = ":".join(trade_types)
    
    params = {
        "rletTpCd": rlet_tp_cd,
        "tradTpCd": trad_tp_cd,
        "cortarNo": region_code,
        "sort": "dates",
        "page": str(page)
    }
    
    if min_area_sqm:
        params["spcMin"] = str(int(min_area_sqm))
    if max_area_sqm:
        params["spcMax"] = str(int(max_area_sqm))
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://m.land.naver.com/",
        "Accept": "application/json, text/plain, */*",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        time.sleep(random.uniform(1, 2))
        
        data = response.json()
        return data.get('body', [])
    
    except Exception as e:
        print(f"방법1 오류: {e}")
        return None

def crawl_naver_land_v2(region_code, property_types, trade_types, min_area_sqm, max_area_sqm, page=1):
    """방법 2: 좌표 기반 검색"""
    url = "https://m.land.naver.com/cluster/ajax/articleList"
    
    bounds = get_region_bounds(region_code)
    if not bounds:
        return None
    
    rlet_tp_cd = ":".join(property_types)
    trad_tp_cd = ":".join(trade_types)
    
    params = {
        "rletTpCd": rlet_tp_cd,
        "tradTpCd": trad_tp_cd,
        "z": str(bounds["z"]),
        "lat": str(bounds["lat"]),
        "lon": str(bounds["lon"]),
        "btm": str(bounds["btm"]),
        "lft": str(bounds["lft"]),
        "top": str(bounds["top"]),
        "rgt": str(bounds["rgt"]),
        "sort": "dates",
        "page": str(page)
    }
    
    if min_area_sqm:
        params["spcMin"] = str(int(min_area_sqm))
    if max_area_sqm:
        params["spcMax"] = str(int(max_area_sqm))
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://m.land.naver.com/",
        "Accept": "application/json, text/plain, */*",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        time.sleep(random.uniform(1, 2))
        
        data = response.json()
        return data.get('body', [])
    
    except Exception as e:
        print(f"방법2 오류: {e}")
        return None

def crawl_naver_land(region_code, property_types, trade_types, min_area_sqm, max_area_sqm, page=1):
    """통합 크롤링 함수"""
    result = crawl_naver_land_v1(region_code, property_types, trade_types, min_area_sqm, max_area_sqm, page)
    
    if result is not None and len(result) > 0:
        return result
    
    result = crawl_naver_land_v2(region_code, property_types, trade_types, min_area_sqm, max_area_sqm, page)
    
    if result is not None and len(result) > 0:
        return result
    
    return []

def parse_article_data(articles, filter_property_types=None):
    """매물 데이터 파싱"""
    results = []
    
    property_type_map = {
        "사무실": ["D01"],
        "상가": ["D02"],
        "건물": ["D03"],
        "지식산업센터": ["E04"]
    }
    
    for article in articles:
        try:
            article_no = article.get('atclNo', '')
            article_name = article.get('atclNm', '')
            
            cortar_name = article.get('cortarName', '')
            cortar_parts = cortar_name.split() if cortar_name else ['', '', '']
            region1 = cortar_parts[0] if len(cortar_parts) > 0 else ''
            region2 = cortar_parts[1] if len(cortar_parts) > 1 else ''
            region3 = cortar_parts[2] if len(cortar_parts) > 2 else ''
            
            property_type = article.get('rletTpNm', '')
            
            if filter_property_types:
                is_match = False
                for target_type, codes in property_type_map.items():
                    if target_type in property_type:
                        if any(code in filter_property_types for code in codes):
                            is_match = True
                            break
                
                if not is_match:
                    continue
            
            spc1 = article.get('spc1', 0)
            spc2 = article.get('spc2', 0)
            area1_pyeong = sqm_to_pyeong(float(spc1)) if spc1 else 0
            area2_pyeong = sqm_to_pyeong(float(spc2)) if spc2 else 0
            
            price_info = article.get('prc', 0)
            deal_type = article.get('tradTpNm', '')
            
            deposit = price_info if '전세' in deal_type or '월세' in deal_type else 0
            contract = price_info if '매매' in deal_type else 0
            monthly_rent = article.get('rentPrc', 0) if '월세' in deal_type else 0
            
            floor_info = article.get('flrInfo', '')
            build_year = article.get('bildYear', '')
            description = article.get('atclFetrDesc', '')
            
            tag_list = article.get('tagList', [])
            
            results.append({
                '매물번호': article_no,
                '시도': region1,
                '시군구': region2,
                '읍면동': region3,
                '부동산구분': property_type,
                '면적1(평)': area1_pyeong,
                '면적2(평)': area2_pyeong,
                '거래유형': deal_type,
                '보증금/전세금(만원)': deposit,
                '매매가(만원)': contract,
                '월세(만원)': monthly_rent,
                '층수': floor_info,
                '건축년도': build_year,
                '매물명': article_name,
                '설명': description[:100] if description else '',
                '태그': ', '.join(tag_list) if tag_list else ''
            })
            
        except Exception as e:
            print(f"데이터 파싱 오류: {e}")
            continue
    
    return results

# ============================================
# API 엔드포인트
# ============================================

@app.route('/')
def index():
    """메인 페이지"""
    return send_file('static/index.html')

@app.route('/api/regions', methods=['GET'])
def get_regions():
    """지역 목록 반환"""
    regions = [
        {"code": code, "name": info["name"]} 
        for code, info in REGION_COORDS.items()
    ]
    return jsonify(sorted(regions, key=lambda x: x['name']))

@app.route('/api/search', methods=['POST'])
def search():
    """부동산 검색"""
    try:
        data = request.json
        
        region_code = data.get('region_code')
        property_types = data.get('property_types', ['D01'])
        trade_types = data.get('trade_types', ['B2'])
        min_area = float(data.get('min_area', 0))
        max_area = float(data.get('max_area', 1000))
        max_results = int(data.get('max_results', 50))
        
        min_sqm = pyeong_to_sqm(min_area) if min_area > 0 else None
        max_sqm = pyeong_to_sqm(max_area) if max_area > 0 else None
        
        all_results = []
        page = 1
        
        while len(all_results) < max_results and page <= 10:
            articles = crawl_naver_land(
                region_code=region_code,
                property_types=property_types,
                trade_types=trade_types,
                min_area_sqm=min_sqm,
                max_area_sqm=max_sqm,
                page=page
            )
            
            if not articles:
                break
            
            parsed_data = parse_article_data(articles, filter_property_types=property_types)
            
            if not parsed_data:
                page += 1
                continue
            
            remaining = max_results - len(all_results)
            if remaining < len(parsed_data):
                parsed_data = parsed_data[:remaining]
            
            all_results.extend(parsed_data)
            
            if len(all_results) >= max_results:
                break
            
            page += 1
        
        return jsonify({
            'success': True,
            'count': len(all_results),
            'data': all_results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download', methods=['POST'])
def download():
    """엑셀 다운로드"""
    try:
        data = request.json.get('data', [])
        
        if not data:
            return jsonify({'error': '데이터가 없습니다'}), 400
        
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='매물목록')
        
        output.seek(0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"상업용부동산_{timestamp}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
