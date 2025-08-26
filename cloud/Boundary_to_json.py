import pandas as pd
import json
from flask import Flask, jsonify

app = Flask(__name__)
# 读取Excel文件
df = pd.read_excel('协同驾驶ODC边界表2.xlsx', sheet_name='Sheet1')
version='协同驾驶ODC边界表2'
# 忽略第一行
df['一级分类'] = df['一级分类'].fillna(method='ffill')
df['二级分类'] = df['二级分类'].fillna(method='ffill')
df['二级分类'] = df['二级分类'].fillna("")
df['三级分类'] = df['三级分类'].fillna("")
# 将前三列连接成一个名称，格式为 '一级分类.二级分类.三级分类'
df['name'] = df['一级分类'] + '.' + df['二级分类'] + '.' + df['三级分类']
def process_value(value):
    if isinstance(value, str):
        value = value.strip()
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        elif value.startswith('(') and value.endswith(')'):
            # 保持元组形式
            return tuple(v.strip().strip('\'').strip('’') for v in value[1:-1].split(','))
        elif value.startswith('（') and value.endswith('）'):
            # 保持元组形式
            return tuple(v.strip().strip('\'').strip('’') for v in value[1:-1].split(','))
        elif value.startswith('[') and value.endswith(']'):
            range_values = value[1:-1].split(',')
            return [float(range_values[0].strip()), float(range_values[1].strip())]
    return value

df['value'] = df['边界值（只允许的状态）'].apply(process_value)
    # 选择需要的列
result_df = df[['name', 'value']]
json_data = result_df.to_dict(orient='records')
#formatted_data = json.dumps(json_data, indent=4, ensure_ascii=False)

@app.route('/get_data', methods=['GET'])
def get_data():
    # 返回JSON响应
    return jsonify(json_data)

if __name__ == '__main__':
    #print(formatted_data)
    app.run(host='127.0.0.1',port=5001,debug=True)
# 应用处理函数
