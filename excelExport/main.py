# -*- coding: utf-8 -*-
import os
import sys
import shutil
import math
import time
import configparser

from multiprocessing import Process

from ExcelParser import ExcelParser
from Exporter.JsonExporter import JsonExporter
from Exporter.TsExporter import TsExporter
from Exporter.LuaExporter import LuaExporter
from Exporter.ErrorCodeExporter import ErrorCodeExporter


def parserExcel(filePath):
    ExcelParser(filePath)


if __name__ == "__main__":
    beginAt = time.time()

    # 加载配置文件
    config = configparser.ConfigParser()
    config.read('config.ini')

    # 单/多进程导出（部分机器多进程有问题）
    useMultiprocessing = config.getboolean('Path', 'multiprocessing')
    if useMultiprocessing == True:
        print("[多进程模式]")
    else:
        print("[单进程模式]")

    # 清理导出目录
    output_path = config.get('Path', 'output_path')
    print("清理导出目录 >>> %s" % output_path)
    if os.path.exists(output_path):
        shutil.rmtree(output_path)

    # 获取配置表目录
    excel_path = config.get('Path', 'excel_path')
    print("准备加载配置表 >>>  %s" % excel_path)

    processMap = {}
    for fileName in os.listdir(excel_path):
        if '~$' in fileName:
            continue
        if os.path.splitext(fileName)[1] == '.xlsx':
            if useMultiprocessing == True:
                # 多进程模式，存在一些问题不建议使用
                process = Process(target=parserExcel, args=(
                    excel_path + '/' + fileName,))
                process.start()
                processMap[fileName] = process
            else:
                # 单进程模式
                parserExcel(excel_path + '/' + fileName)

    # 等待所有进程执行完毕
    for fileName in processMap:
        process = processMap[fileName]
        if process.is_alive:
            process.join()

    # 检查子进程状态
    for fileName in processMap:
        process = processMap[fileName]
        if process.exitcode != 0:
            print('------------------------------------------')
            print('------------------------------------------')
            print('导表出错：%s exitcode:%s' % (fileName, process.exitcode))
            print('错误信息在上边，自查解决不了再问技术！！！')
            print('------------------------------------------')
            print('------------------------------------------')
            sys.exit(1)

    # *********特殊需求*********
    LuaExporter().exportOther()
    TsExporter().exportOther()
    ErrorCodeExporter().exportOther()

    useTime = time.time() - beginAt
    useTime = math.floor(useTime * 1000) / 1000
    print('导出完成，耗时：%s 秒' % str(useTime))
    # input("按任意键退出")
