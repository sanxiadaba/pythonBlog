"""
File description:

This file is used to initialize the mysql database

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/23
@gituhb: sanxiadaba/pythonBlog
"""
import time
import traceback

import pymysql

from common.myLog import allLogger
from common.myLog import rootDir
from common.utility import genearteMD5
from constant import mysqlPassword, mysqlPort, databaseName, mysqlUserName, mysqlUrl, adminLogin, adminPassword, \
    userLogin, userPassword, md5Salt, editorPassword, editorLogin, postArticleCredit

adminPassword = genearteMD5(adminPassword + md5Salt)
editorPassword = genearteMD5(editorPassword + md5Salt)
userPassword = genearteMD5(userPassword + md5Salt)


def ininDatabase():
    # Database connection
    con = pymysql.connect(host=mysqlUrl, user=mysqlUserName, password=mysqlPassword, database="mysql", port=mysqlPort,
                          charset='utf8mb4')
    # Creating Cursor Objects
    cur = con.cursor()

    # View Database
    sql = """
        show databases;
    """
    try:
        cur.execute(sql)
        # (('information_schema',), ('myBlog',), ('mysql',), ('performance_schema',),)
        allDatabases = cur.fetchall()
        databaseList = []
        for database in allDatabases:
            databaseList.append(database[0])
        # If there is no databasename in the original database
        # Then create it
        if databaseName not in databaseList:
            sql = f"""
            CREATE DATABASE IF NOT EXISTS {databaseName};
            """
            cur.execute(sql)
            sql = f"use {databaseName};"
            cur.execute(sql)
            with open(f"{rootDir}\\myBlog.sql") as f:
                sqls = f.read().split(";")
            print("Initializing database, please wait...")
            for sql in sqls[0:-2]:
                sql += ";"
                cur.execute(sql)
            sql = f"use {databaseName};"
            cur.execute(sql)
            cur.execute(sqls[-2])
            with open(f"{rootDir}\\templates\\exampleArticle.html") as e:
                exampleArticle = e.read()
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            sql = "insert into users (username,password,nickname,avatar,role,credit,createtime,apply) values (%s, %s, %s,%s,%s,%s,%s,%s)"
            cur.execute(sql, (adminLogin, adminPassword, "admin", "default/1.png", "admin", 1000, now, 0))
            cur.execute(sql, (editorLogin, editorPassword, "editor", "default/2.png", "editor", 1000, now, 0))
            cur.execute(sql, (userLogin, userPassword, "user", "default/3.png", "user", 1000, now, 1))
            sql = "insert into article (userid,type,headline,content,thumbnail,readcount,replycount,createtime,updatetime,recommended) values (%s, %s, %s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(sql, (2, 1, "example", exampleArticle, "default/1.jpg", 0, 1, now, now, 1))
            sql = "insert into comment (userid,articleid,content,ipaddr,agreecount,opposecount,createtime) values (%s, %s, %s,%s,%s,%s,%s)"
            cur.execute(sql, (2, 1, "this is a example comment", f"{mysqlUrl}", 0, 0, now))
            sql = "insert into articleLog (userid,articleid,type,ipaddr,info,createtime) values (%s,%s,%s,%s,%s,%s)"
            cur.execute(sql, (2, 1, "Post Article", "localhost", "This is my first article", now))
            sql = "insert into credit (userid,category,target,createtime,ipaddr,info,credit) values (%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(sql, (2, "Post Article", 1, now, "localhost", "post article successfully", postArticleCredit))
            allLogger(1, "Database initialization successful")
            print("Database initialization successful")
            print("Start the flask server...")
        else:
            pass

    except:
        e = traceback.format_exc()
        allLogger(0, e)
    finally:
        # Close cursor connections
        con.commit()
        cur.close()
        # Close the database connection
        con.close()


#  watch the version od MySql
def watchVersionOfMysql():
    con = pymysql.connect(host=mysqlUrl, user=mysqlUserName, password=mysqlPassword, database="mysql", port=mysqlPort,
                          charset='utf8mb4')
    cur = con.cursor()
    sql = """
            select version();
        """
    try:
        cur.execute(sql)
        version = cur.fetchall()[0][0]
        return version
    except:
        e = traceback.format_exc()
        allLogger(0, e)
        return 0
    finally:

        # Close cursor connections
        con.commit()
        cur.close()
        # Close the database connection
        con.close()
