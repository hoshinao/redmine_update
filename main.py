import MySQLdb
import pymysql
import mysql.connector
import datetime
from dateutil.relativedelta import relativedelta


##sqldb接続##
conn = mysql.connector.connect(
    database="redmine",
    user="redmine",
    password="redmine",
    host="obsvrm05",
    db="mysql",
    port="3306"
)

cur = conn.cursor()

today_data = datetime.date.today()
today_year = today_data.year
last_year = today_year - 1
upd_count = 0

##前年度データ取得##
sql = """
SELECT issues.id,issues.start_date,issues.subject,issues.status_id,custom_values.value FROM custom_values 
            INNER JOIN issues ON custom_values.customized_id = issues.id where issues.tracker_id = 37 and 
            issues.start_date >= %s and custom_values.custom_field_id  = '47'
            """
cur.execute(sql, (datetime.date(last_year, 4, 1),))

rows2 = cur.fetchall()
for row in rows2:
    ##開始日に+1年##
    issue_year = row[1] + relativedelta(years=1)
    issues_subject = row[2]
    custom_values_value = row[4]

    ##新年度チケット作成処理##
    sql = """
    INSERT INTO 
    issues (
        tracker_id,project_id,subject,status_id,priority_id,author_id,lock_version,done_ratio,is_private,created_on,updated_on,start_date,root_id,lft,rgt)
    VALUES
      (37,95,%s,1,2,1,0,0,0,CURRENT_DATE ,CURRENT_DATE ,%s ,1,1,2)

    """
    datas_set = issues_subject, issue_year
    cur.execute(sql, datas_set)

    ##追加されたチケットNo取得##
    cur.execute("SELECT @@IDENTITY")
    rows = cur.fetchall()

    ##取得したチケットNoに主管課名を追加##
    sql = """
    INSERT INTO
    custom_values(
        customized_id,custom_field_id,value,customized_type)
    VALUES
        (%s,47,%s,'Issue')
        """

    ##追加行をカウント##
    sql_set_data = rows[0][0], custom_values_value
    cur.execute(sql, sql_set_data)
    upd_count += int(cur.rowcount)
    result = cur.fetchall()

print(f"{upd_count}件のチケットを追加しました。")

#conn.commit()

cur.close
conn.close
