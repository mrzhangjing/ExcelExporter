# -*- coding: utf-8 -*-
import os
from Enum import ValueType, OutputType
from Exporter.Exporter import Exporter


class LuaExporter(Exporter):
    def __init__(self, fileName="", tableName=""):
        Exporter.__init__(self, fileName, tableName)
        self.server_path = self.config.get('Lua', 'server_path')
        self.client_path = self.config.get('Lua', 'client_path')

    def exportOther(self):
        # 导出 cache.lua
        self._exportConfigCache()
        # 导出 config_db.lua
        self.writeFile(self.server_path, 'config_db.lua',
                       self.readTemplet("config_db.lua.tmp"))

    def exportConfig(self, VOParser):
        self._exportLuaConfig(VOParser)

    # 导出 Lua 配置表
    def _exportLuaConfig(self, VOParser):
        lineStrList = []

        def func(lineValues):
            lineStr = "    "
            firstTitle = VOParser.titleIndex[0]
            if firstTitle["valueType"] is ValueType.KeyNumber:
                templet = "[%value%] = {"
                templet = templet.replace(
                    '%value%', str(lineValues[firstTitle["key"]]))
                lineStr = lineStr + templet
            elif firstTitle["valueType"] is ValueType.KeyString:
                templet = "[\"%value%\"] = {"
                templet = templet.replace(
                    '%value%', str(lineValues[firstTitle["key"]]))
                lineStr = lineStr + templet
            else:
                lineStr = lineStr + "{"

            for i in VOParser.titleIndex:
                title = VOParser.titleIndex[i]
                key = title["key"]
                if key in lineValues:
                    if key not in lineValues:
                        continue
                    value = lineValues[key]
                    if value == None:
                        continue

                    if title['valueType'] is ValueType.Enum or title['valueType'] is ValueType.KeyString or title['valueType'] is ValueType.String or title['valueType'] is ValueType.StringOrNull:
                        value = '[[' + value + ']]'
                    elif title['valueType'] is ValueType.NumberArrays \
                            or title['valueType'] is ValueType.NumberMultiArrays:
                        value = value.replace('[', '{')
                        value = value.replace(']', '}')
                    elif title['valueType'] is ValueType.StringArrays:
                        value = value.replace('[', '{\"')
                        value = value.replace(',', '\",\"')
                        value = value.replace(']', '\"}')

                    templet = "%key% = %value%, "
                    templet = templet.replace('%key%', key)
                    templet = templet.replace('%value%', value)
                    lineStr = lineStr + templet

            lineStr = lineStr + "},\n"
            lineStrList.append(lineStr)

        VOParser.forEachLine(func)

        if len(lineStrList) == 0:
            return

        luaTable = '-- 注释： ' + self.fileName + " > "
        for i in VOParser.titleIndex:
            luaTable = luaTable + VOParser.titleIndex[i]['key'] + \
                ":" + VOParser.titleIndex[i]['desc'] + ' '
        luaTable = luaTable + '\n'

        luaTable = luaTable + "local " + self.tableName + ' = {\n'
        for lineStr in lineStrList:
            luaTable = luaTable + lineStr
        luaTable = luaTable + '}\nreturn ' + self.tableName

        luaTable = luaTable.replace(', },\n', "},\n")
        # print(luaTable)

        self.writeFile(self.server_path, self.tableName + '.lua', luaTable)
        # self.writeFile(self.client_path, self.tableName + '.lua', luaTable)

    # 导出 cache.lua
    def _exportConfigCache(self):
        print("生成：> cache.lua")
        cache = self.readTemplet("cache.lua.tmp")

        configList = ""
        for fileName in os.listdir(self.server_path):
            if '~$' in fileName:
                continue
            if fileName.find(".lua") == -1:
                continue
            ShortName = fileName.replace(".lua", "")
            configList = configList + "config." + \
                ShortName+" = new(\""+ShortName+"\")\n"

        cache = cache.replace("%configList%", configList)
        self.writeFile(self.server_path, 'cache.lua', cache)
