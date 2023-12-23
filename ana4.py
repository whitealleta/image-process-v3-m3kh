# 对用户分级【】
#用户活跃度进行分级 近180日发布内容 < 3【不活跃】，近180日发布内容 >3 and <




import pandas as pd
from datetime import datetime, timedelta



df = pd.read_excel(r'dongchedi\user_content_clearing.xlsx')
df['发布时间'] = pd.to_datetime(df['发布时间'])
df = df.dropna(subset=['发布时间'])

# 计算用户最早和最晚的发布时间
user_dates = df.groupby('昵称')['发布时间']
user_min_date = user_dates.min()
user_max_date = user_dates.max()

# 方法1: 判断用户是否在最早和最晚日期区间内任意三个月内发布频率高于临界值
critical_frequency = 15  # 临界值
active_users_method1 = set()
high_active_users_method1 = set()

for user_id, min_date in user_min_date.items():
    # 计算最早和最晚日期之间的时间范围，以15天为步长
    date_range = pd.date_range(min_date, user_max_date[user_id], freq='15D')
    
    # 遍历时间范围，判断每个三个月的频率是否高于临界值
    for start_date in date_range:
        end_date = start_date + timedelta(days=89)  # 任意三个月
        
        # 获取在这个三个月内的数据
        user_data_three_months = df[(df['昵称'] == user_id) & (df['发布时间'] >= start_date) & (df['发布时间'] <= end_date)]
        
        # 判断频率是否高于临界值
        if len(user_data_three_months) >= critical_frequency * 3 :
            high_active_users_method1.add(user_id)
            break 
    if len(user_data_three_months) >= critical_frequency:
            active_users_method1.add(user_id)

# 分类：不活跃、活跃、高度活跃
inactive_users = set(user_min_date.index).difference(active_users_method1.union(high_active_users_method1))
active_users = active_users_method1
highly_active_users = high_active_users_method1


# 方法2: 判断用户近一个月发布内容频率大于临界值
critical_frequency2 = 10  # 临界值
current_date = datetime.now()
start_date = current_date - timedelta(days=30)
recent_users = df[df['发布时间'] >= start_date]
high_active_users_method2 = set(recent_users.groupby('昵称').filter(lambda x: len(x) >= critical_frequency2 * 3)['昵称'].unique())
active_users_method2 = set(recent_users.groupby('昵称').filter(lambda x: len(x) >= critical_frequency2)['昵称'].unique())

active_users2 = active_users_method2.difference(high_active_users_method2)
highly_active_users2 = high_active_users_method2
inactive_users2 = set(user_min_date.index).difference(active_users_method2.union(high_active_users_method2))


# 结合两种方法，只要有一个为活跃就判断为活跃
highly_active_users_combined = highly_active_users.union(highly_active_users2)
inactive_users_combined = inactive_users.intersection(inactive_users2)
active_users_combined = set(user_min_date.index).difference(inactive_users_combined.union(highly_active_users_combined))


print("不活跃用户:", inactive_users_combined)
print("活跃用户:", active_users_combined)
print("高度活跃用户:", highly_active_users_combined)


df2 = pd.read_excel('dongchedi/user_data_clearing.xlsx')

# 将映射结果添加到 df2
df2['活跃度'] = df2['昵称'].apply(lambda x: '高度活跃' if x in highly_active_users_combined else ('活跃' if x in active_users_combined else '不活跃'))

df2.to_excel('dongchedi/active.xlsx', index= False)