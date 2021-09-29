# -*- coding: utf-8 -*-
import os
import xlrd
import re
import sys
import shutil
import io
import json

from enum import Enum
from enum import unique

# from imp import reload
# reload(sys)
# sys.setdefaultencoding("utf-8")

# reload(sys)
# sys.setdefaultencoding('utf8')

EXCEL_PATH = u'./'
DEFAULT_PATH = EXCEL_PATH + '/config'
CLIENT_PATH = DEFAULT_PATH + '/Client'
SERVER_PATH = DEFAULT_PATH + '/Server'


@unique  # 导出类型
class ExportType(Enum):
    Lua = "lua"
    Json = "json"
    Ts = "ts"


@unique
class ValueType(Enum):
    Null = 0     # 不导出

    KeyNumber = "KeyNumber"		# 数字 key
    Number = "Number"			# 数字 默认:0
    NumberOrNull = "NumberOrNull"  # 数字 默认不导出
    NumberArrays = "[Num，*]"			# 数字数组，[1,2]
    NumberMultiArrays = "[[Num，*]]"		# 数字数组，[[1,2],[3,4]]

    Enum = "Enum"				# 枚举类型，英文 如果填写，自动生成枚举文件

    KeyString = "KeyString"		# 字符串 key
    String = "String"			# 字符串 默认：""
    StringOrNull = "StringOrNull"  # 字符串 默认不导出
    StringArrays = "[String，*]"		# 字符串数组，["a","b"]

    # Native          	= "Native"			# 原样导出


@unique
class OutputType(Enum):
    All = 0   # 导出全部
    Client = 1   # 只导出客户端
    Server = 2   # 只导出服务端


def isNone(value):
    return value is None or str(value) == ""


def isNumber(value):
    return type(value) == type(1.0)


def toFloat(value):
    if value is None or value == '' or value == 'null':
        return null
    try:
        float(value)
    except BaseException:
        print("---------------请检查错误---------------")
        print("value = %s" % value)
        print("类型转换失败，这里应该填写数字")
        input("")
    value = float(value) * 100000 + 0.1
    if value > 0:
        value = int(value + 0.1) / 100000
    if value < 0:
        value = int(value - 0.1) / 100000
    return value


def toInt(value):
    if value is None or value == '' or value == 'null':
        return 'null'
    try:
        float(value)
    except BaseException:
        print("---------------请检查错误---------------")
        print("value = %s" % value)
        print("类型转换失败，这里应该填写数字")
        input("")
    intValue = int(float(value))
    floatValue = toFloat(value)
    if intValue != floatValue:
        return floatValue
    return intValue


def getTableName(sheetName):
    mm = re.findall("(\(.*?\))", sheetName)
    if(len(mm) > 0):
        mm = mm[0]
        mm = mm.replace('[', '').replace(']', '')
        mm = mm.replace('(', '').replace(')', '')
        return mm
    else:
        return


class ValueParser:
    def init(self, key, desc, valueType, output, value):
        self.key = key
        self.desc = desc
        self.valueType = valueType
        self.output = output
        self.value = value

    def toLua(self):
        # 转换数字
        if self.valueType == ValueType.KeyNumber.name:
            if isNone(self.value):
                self.value = 0
            self.value = toInt(self.value)
        if self.valueType == ValueType.Number.name:
            if isNone(self.value):
                self.value = 0
            self.value = toInt(self.value)
        if self.valueType == ValueType.NumberOrNull.name:
            if isNone(self.value):
                return
            self.value = toInt(self.value)
        if self.valueType == ValueType.NumberArrays.name or self.valueType == ValueType.NumberMultiArrays.name:
            if isNone(self.value):
                return
            self.value = self.value.replace("[", "{")
            self.value = self.value.replace("]", "}")

        # 转换字符串
        if self.valueType == ValueType.KeyString.name:
            if isNone(self.value):
                self.value = ''
            self.value = '[[' + str(self.value) + ']]'
        if self.valueType == ValueType.String.name:
            if isNone(self.value):
                self.value = ''
            if type(self.value) == type(1.0):
                if toInt(self.value) == toFloat(self.value):
                    self.value = toInt(self.value)
            self.value = '[[' + str(self.value) + ']]'
        if self.valueType == ValueType.Enum.name or self.valueType == ValueType.StringOrNull.name:
            if isNone(self.value):
                return
            if type(self.value) == type(1.0):
                if toInt(self.value) == toFloat(self.value):
                    self.value = toInt(self.value)
            self.value = '[[' + str(self.value) + ']]'
        if self.valueType == ValueType.StringArrays.name:
            if isNone(self.value):
                return
            self.value = self.value.replace('[', '{\"')
            self.value = self.value.replace(',', '\",\"')
            self.value = self.value.replace(']', '\"}')

        # 转换不做处理
        # if self.valueType == ValueType.Native.name:

        outputValue = self.key + ' = ' + str(self.value)
        return outputValue

    def toJson(self):
        # 转换数字
        if self.valueType == ValueType.KeyNumber.name or self.valueType == ValueType.Number.name or self.valueType == ValueType.NumberOrNull.name:
            if isNone(self.value):
                self.value = 'null'
            self.value = toInt(self.value)
        elif self.valueType == ValueType.NumberArrays.name or self.valueType == ValueType.NumberMultiArrays.name:
            if isNone(self.value):
                self.value = 'null'
            self.value = self.value.replace(',]', ']')
            self.value = self.value.replace(',]', ']')
        # 转换字符串
        elif self.valueType == ValueType.KeyString.name or self.valueType == ValueType.String.name or self.valueType == ValueType.Enum.name or self.valueType == ValueType.StringOrNull.name:
            if isNone(self.value):
                self.value = ''
            self.value = str(self.value)
            self.value = self.value.replace('"', '\\"')
            self.value = '"' + str(self.value) + '"'
        elif self.valueType == ValueType.StringArrays.name:
            if isNone(self.value):
                self.value = "[]"
            self.value = self.value.replace('[', '[\"')
            self.value = self.value.replace(',', '\",\"')
            self.value = self.value.replace(']', '\"]')

        else:
            if isNone(self.value):
                self.value = "null"

        # 转换不做处理
        # if self.valueType == ValueType.Native.name:

        outputValue = str(self.value)
        return outputValue


class VOParser:
    def __init__(self, fileName, tableName):
        self.keys = {}
        self.keyMap = {}
        self.fileName = fileName
        self.tableName = tableName
        print(tableName)

    def addKey(self, index, key, desc, valueType, output):
        if index == None or index in self.keys:
            return
        if key == None or key == '' or key in self.keyMap:
            return

        if valueType == "[Num，*]":
            valueType = ValueType.NumberArrays.name
        if valueType == "[[Num，*]]":
            valueType = ValueType.NumberMultiArrays.name
        if valueType == "[String，*]":
            valueType = ValueType.StringArrays.name

        if valueType == None or valueType not in ValueType.__members__:
            return
        if valueType == ValueType.KeyNumber.name or valueType == ValueType.KeyString.name:
            assert(index == 0)
        newKey = {'key': key, 'desc': desc,
                  'valueType': valueType, 'output': output}
        self.keys[index] = newKey
        self.keyMap[key] = True

    def getLuaTitle(self, output):
        title = '注释： ' + self.fileName + " > "
        for i in self.keys:
            title = title + self.keys[i]['key'] + \
                ":" + self.keys[i]['desc'] + ' '
        title = title + '\n'
        return title

    def getJsonTitle(self, output):
        title = '    ['
        for i in self.keys:
            key = self.keys[i]['key']
            if self.keys[i]['valueType'] == 4 or self.keys[i]['valueType'] == 5:
                key = '__index:' + key
            title = title + '\"' + key + \
                '(' + self.keys[i]['desc'] + ')' + '\",'
        title = title + '],\n'
        title = title.replace(',]', ']')
        return title

    def parseToLua(self, lineValues, output):
        if isNone(lineValues):
            return
        valueParser = ValueParser()
        lineStr = ''
        for i in self.keys:
            if self.keys[i] == None or lineValues[i] == None:
                continue
            key = self.keys[i]['key']
            desc = self.keys[i]['desc']
            valueType = self.keys[i]['valueType']
            value = lineValues[i]
            valueOutput = self.keys[i]['output']

            if valueOutput != OutputType.All.name and valueOutput != output:
                continue
            if isNone(value) and (valueType == ValueType.NumberOrNull.name or valueType == ValueType.Enum.name or valueType == ValueType.StringOrNull.name):
                continue

            if valueType == ValueType.KeyNumber.name:
                lineStr = '[' + str(toInt(value)) + '] = {' + lineStr
            elif valueType == ValueType.KeyString.name:
                lineStr = '[\"' + value + '\"] = {' + lineStr
            elif lineStr == '':
                lineStr = '{'

            # print("key:%s, desc:%s, valueType:%s, output:%s, value:%s" % (key, desc, valueType, output, value))
            valueParser.init(key, desc, valueType, output, value)
            outputValue = valueParser.toLua()
            if outputValue != None and outputValue != '':
                lineStr = lineStr + outputValue + ", "

        if lineStr != '':
            lineStr = '    ' + lineStr
            lineStr = lineStr + '},\n'
        lineStr = lineStr.replace(', },', '},')
        lineStr = lineStr.replace('}, },', '}},')
        return lineStr

    def parseToJson(self, rowIndex, lineValues, output):
        if isNone(lineValues):
            return
        valueParser = ValueParser()
        lineStr = ''
        lineKey = str(rowIndex)
        for i in self.keys:
            if self.keys[i] == None or lineValues[i] == None:
                continue
            key = self.keys[i]['key']
            desc = self.keys[i]['desc']
            valueType = self.keys[i]['valueType']
            value = lineValues[i]
            valueOutput = self.keys[i]['output']

            if valueOutput != OutputType.All.name and valueOutput != output:
                continue
            # json 全部空格全部导出
            # if isNone(value) and (valueType == ValueType.NumberOrNull.name or valueType == ValueType.StringOrNull.name or valueType == ValueType.ListOrNull.name or valueType == ValueType.MapOrNull.name):
            #     continue

            if valueType == ValueType.KeyNumber.name:
                lineKey = str(toInt(value))
            elif valueType == ValueType.KeyString.name:
                lineKey = value
            elif lineStr == '':
                lineStr = ''

            # print("key:%s, desc:%s, valueType:%s, output:%s, value:%s" % (key, desc, valueType, output, value))
            valueParser.init(key, desc, valueType, output, value)
            outputValue = valueParser.toJson()
            if outputValue != None and outputValue != '':
                lineStr = lineStr + outputValue + ", "

        lineStr = '    [' + lineStr + '],'
        lineStr = lineStr + '\n'
        return lineStr

    def parseToTs(self, path, output):

        # 导出VO对象
        VOName = "_" + self.tableName
        VOName = re.sub(r'(_\w)', lambda x: x.group(1)[1].upper(), VOName)
        VOName = VOName.replace('Config', '')
        VOName = VOName.replace('VO', '')
        VOName = VOName + "VO"

        fd = io.open(path + '/' + VOName + '.ts', 'w', encoding='utf-8')
        VoCode = """
/**
 * 根据配置表自动生成，禁止修改！！！
 **/
export default class %VOName% {
%EnumCode%
	constructor(data: Array<any>) {
%initMemberCode%
	};

%memberCode%
}
"""
        VoCode = VoCode.replace('%VOName%', VOName)
        initMemberCode = ""
        memberCode = ""
        index = 0
        for i in self.keys:
            valueOutput = self.keys[i]['output']
            if valueOutput != OutputType.All.name and valueOutput != output:
                continue

            initFormat = """
		this.%key% = data[%index%];"""
            initFormat = initFormat.replace("%key%", self.keys[i]['key'])
            initFormat = initFormat.replace("%index%", str(index))
            index = index + 1
            initMemberCode = initMemberCode + initFormat

            memberFormat = """
	// %desc%
	public readonly %key%: %valueType%;"""
            memberFormat = memberFormat.replace("%desc%", self.keys[i]['desc'])
            memberFormat = memberFormat.replace("%key%", self.keys[i]['key'])
            valueType = self.keys[i]['valueType']
            if valueType == ValueType.KeyNumber.name:
                valueType = "number"
            elif valueType == ValueType.Number.name:
                valueType = "number"
            elif valueType == ValueType.NumberOrNull.name:
                valueType = "number | null"
            elif valueType == ValueType.NumberArrays.name:
                valueType = "number[] | null"
            elif valueType == ValueType.NumberMultiArrays.name:
                valueType = "number[][] | null"
            elif valueType == ValueType.KeyString.name:
                valueType = "string"
            elif valueType == ValueType.String.name:
                valueType = "string"
            elif valueType == ValueType.Enum.name:
                valueType = "string | null"
            elif valueType == ValueType.StringOrNull.name:
                valueType = "string | null"
            elif valueType == ValueType.StringArrays.name:
                valueType = "string[] | null"
            else:
                valueType = "string | null"
            memberFormat = memberFormat.replace("%valueType%", valueType)
            memberCode = memberCode + memberFormat

        VoCode = VoCode.replace('%initMemberCode%', initMemberCode)
        VoCode = VoCode.replace('%memberCode%', memberCode)
        fd.write(VoCode)
        fd.close()

        # 导出Table对象
        TableName = VOName.replace('VO', '')
        TableName = TableName + "Table"
        fd = io.open(path + '/' + TableName + '.ts', 'w', encoding='utf-8')

        TableCode = """
/**
 * 根据配置表自动生成，禁止修改！！！
 */

import ResMgr from "../common/res/ResMgr";
import %ShortName%VO from "./%ShortName%VO";


export default class %ShortName%Table {
%EnumCode%
    constructor() {
        const name = "%file_name%";
        this.initVO(ResMgr.getInstance().getJson(name));
    }

	initVO(data: Array<any>): void {
		for (var i = 0, len = data.length; i < len; i++) {
			if (i == 0) continue;
			let VO = new %ShortName%VO(data[i])
			this.VOList.push(VO)
			%initKey%
		}
	}
%findByKey%

	VOList: %ShortName%VO[] = [];
    public findFirst(filter: (VO: %ShortName%VO) => boolean) {
        for (var i = 0, len = this.VOList.length; i < len; i++) {
            let VO = this.VOList[i]
            if (filter(VO)) {
                return VO
            }
        }
    }

    public findAll(filter: (VO: %ShortName%VO) => boolean) {
        let list = [];
        for (var i = 0, len = this.VOList.length; i < len; i++) {
            let VO = this.VOList[i]
            if (filter(VO)) {
                list.push(VO)
            }
        }
        return list
    }

    public forEach(filter: (VO: %ShortName%VO) => void) {
        for (var i = 0, len = this.VOList.length; i < len; i++) {
            let VO = this.VOList[i]
            filter(VO)
        }
    }
}
"""
        EnumCode = ""
        if EnumCode == "":
            TableCode = TableCode.replace('\n%EnumCode%', "")
        else:
            TableCode = TableCode.replace('%EnumCode%', EnumCode)

        TableCode = TableCode.replace("%ShortName%", VOName.replace('VO', ''))
        TableCode = TableCode.replace("%file_name%", self.tableName)

        initKey = ""
        findByKey = ""
        if 0 in self.keys and self.keys[0] != None:
            if self.keys[0]['output'] == OutputType.All.name or self.keys[0]['output'] == output:
                if self.keys[0]['valueType'] == ValueType.KeyNumber.name or self.keys[0]['valueType'] == ValueType.KeyString.name:
                    key = self.keys[0]['key']
                    valueType = "number"
                    if self.keys[0]['valueType'] == ValueType.KeyString.name:
                        valueType = "string"
                    initKey = "this.VOMap.set(VO.%key%, VO)"
                    initKey = initKey.replace("%key%", key)
                    findByKey = """
	VOMap: Map<%valueType%, %VOName%> = new Map();
	public findBy%Key%(%key%: %valueType%): %VOName% {
		return this.VOMap.get(%key%)
	}\n"""
                    findByKey = findByKey.replace("%VOName%", VOName)
                    findByKey = findByKey.replace("%Key%", key.capitalize())
                    findByKey = findByKey.replace("%key%", key)
                    findByKey = findByKey.replace("%valueType%", valueType)

        TableCode = TableCode.replace("%initKey%", initKey)
        TableCode = TableCode.replace("%findByKey%", findByKey)
        fd.write(TableCode)
        fd.close()
        return


class ExcelParser:
    def __init__(self):
        # 需要导出的类型
        self.exportList = []

    def checkExportType(self, exType):
        for v in ExportType:
            if v.name == exType:
                return True
        return False

    def addExportType(self, exType):
        if not self.checkExportType(exType):
            tmp = ""
            for v in ExportType:
                tmp = tmp + "[" + v.name + "]"
            print('>>> 导出类型错误:%s 可用导出类型:%s' % (exType, tmp))
            return False

        if self.exportList.count(exType) == 0:
            self.exportList.append(exType)

    # 检查文件夹是否存在，不存在则创建
    def checkDir(self):
        if not os.path.exists(EXCEL_PATH):
            os.makedirs(EXCEL_PATH)
        if os.path.exists(DEFAULT_PATH):
            shutil.rmtree(DEFAULT_PATH)
            # os.rename(DEFAULT_PATH, DEFAULT_PATH + "_old")
        if not os.path.exists(DEFAULT_PATH):
            os.makedirs(DEFAULT_PATH)
        if not os.path.exists(DEFAULT_PATH+"/Code"):
            os.makedirs(DEFAULT_PATH+"/Code")
        if not os.path.exists(SERVER_PATH):
            os.makedirs(SERVER_PATH)
        for exportType in self.exportList:
            if not os.path.exists(CLIENT_PATH + "/" + exportType):
                os.makedirs(CLIENT_PATH + "/" + exportType)
            if not os.path.exists(SERVER_PATH + "/" + exportType):
                os.makedirs(SERVER_PATH + "/" + exportType)

    # 读取当前路径的配置表文件夹内的所有excel
    def loadAllExcel(self):
        for fileName in os.listdir(EXCEL_PATH):
            if '~$' in fileName:
                continue
            if os.path.splitext(fileName)[1] == '.xlsx':
                self.load(fileName)

        if "Ts" in self.exportList:
            self.exportTblTs()

        if "Lua" in self.exportList:
            self.exportTblLua()

        self.exportCode()

    def exportTblTs(self):
        importCode = ""
        memberCode = ""
        initMemberCode = ""
        for fileName in os.listdir(CLIENT_PATH + "/" + ExportType.Ts.name):
            if '~$' in fileName:
                continue
            if fileName.find("Table.ts") == -1:
                continue
            ShortName = fileName.replace("Table.ts", "")
            importCode = importCode + \
                "import %ShortName%Table from \"./%ShortName%Table\";\n".replace(
                    "%ShortName%", ShortName)
            memberCode = memberCode + \
                "    public static %ShortName%Table: %ShortName%Table = null;\n".replace(
                    "%ShortName%", ShortName)
            initMemberCode = initMemberCode + \
                "        tbl.%ShortName%Table = new %ShortName%Table();\n".replace(
                    "%ShortName%", ShortName)
        TblCode = """
/**
 * 根据配置表自动生成，禁止修改！！！
 */
%importCode%

export default class tbl {
%memberCode%

    constructor() {
%initMemberCode%
    }

    public static __instance: tbl = null;
    static getInstance(): tbl {
        if (!tbl.__instance) {
            tbl.__instance = new tbl();
        }
        return tbl.__instance;
    }
}
"""
        TblCode = TblCode.replace("%importCode%", importCode)
        TblCode = TblCode.replace("%memberCode%", memberCode)
        TblCode = TblCode.replace("%initMemberCode%", initMemberCode)
        sfd = io.open(SERVER_PATH + "/Ts/Tbl.ts", 'w', encoding='utf-8')
        sfd.write(TblCode)
        sfd.close()
        cfd = io.open(CLIENT_PATH + "/Ts/Tbl.ts", 'w', encoding='utf-8')
        cfd.write(TblCode)
        cfd.close()

    def exportTblLua(self):
        configList = ""
        for fileName in os.listdir(SERVER_PATH + "/Lua"):
            if '~$' in fileName:
                continue
            if fileName.find(".lua") == -1:
                continue
            ShortName = fileName.replace(".lua", "")
            configList = configList + "config." + \
                ShortName+" = new(\""+ShortName+"\")\n"

        TblCode = """--[[
>>> 该文件由配置表导出生成，禁止手动修改！！！
]]

local conf = require("skynet.sharedata.corelib")
local pathprefix = "config."
local new = function(path)
	local cobj
	local ok, msg = pcall(function ()
		local data = require(pathprefix .. path)
		cobj = conf.host.new(data)
		package.loaded[pathprefix .. path] = nil
	end, debug.traceback)
	assert(ok, string.format("path:%s msg:%s", path, msg))
    return cobj
end

function proxyConfig(origin)
	for k, v in pairs(origin) do
		local func = load(v)
		if func then
			origin[k] = func()
		end
	end
	return origin
end

local config 				= {}

%configList%

return config
"""
        TblCode = TblCode.replace("%configList%", configList)
        sfd = io.open(SERVER_PATH + "/Lua/cache.lua", 'w', encoding='utf-8')
        sfd.write(TblCode)
        sfd.close()
        cfd = io.open(CLIENT_PATH + "/Lua/cache.lua", 'w', encoding='utf-8')
        cfd.write(TblCode)
        cfd.close()

        ConfigDbCode = """--[[
>>> 该文件由配置表导出生成，禁止手动修改！！！
]]
local conf = require("skynet.sharedata.corelib")

local configDb = {}
local configKeys = {}

setmetatable(configDb, {
    __index = function(t, k)
        local value = configKeys[k]
        if value == nil  then
            -- return require("config." .. k)
            return nil
        end
        if value[2] then
            return value[2]
        end
        local obj = conf.box(value[1])
        value[2] = obj
        return obj
    end
})

function configDb.init(configs)
    for k, p in pairs(configs) do
        configKeys[k] = {p}
    end
end

function configDb.update(configs)
    for k, p in pairs(configs) do
        local value = configKeys[k]
        if value then
            if value[2] then
                conf.update(value[2], p)
            end
            value[1] = p
        else
            configKeys[k] = {p}
        end
    end
end

function configDb.getConfig(configName)
    return configKeys[configName]
end
function configDb.getAllConfigs()
    return configKeys
end
return configDb
"""
        sfd = io.open(SERVER_PATH + "/Lua/config_db.lua",
                      'w', encoding='utf-8')
        sfd.write(ConfigDbCode)
        sfd.close()

    def exportCode(self):
        LuaErrorCode = """
--[[
>>> 该文件由配置表导出生成，禁止手动修改！！！
]]

local errors = {}

function errmsg(ec)
    if not ec then
        return "nil"
    end
    return errors[ec] or ec
end

local function add(error)
    assert(errors[error.code] == nil, string.format(
        "had the same error code[%x], msg[%s]", error.code, error.message))
    errors[error.code] = error.message
    return error.code
end

%ModuleError%

return errors
"""

        TsErrorCode = """
/**
>>> 该文件由配置表导出生成，禁止手动修改！！！
*/

%ModuleError%

export const ErrorCode = {
%ErrorList%
}

"""
        ModuleList = []
        LuaModuleIndex = {}
        TsModuleIndex = {}
        ErrorList = ""
        with open(SERVER_PATH+"/Json/error_code_config.json", 'rb') as load_f:
            load_dict = json.load(load_f)
            load_dict.pop(0)
            for info in load_dict:
                if info[1] not in LuaModuleIndex:
                    LuaModuleIndex[info[1]] = info[1]+" = {\n"
                    TsModuleIndex[info[1]] = "export const "+info[1]+" = {\n"
                    ModuleList.append(info[1])
                LuaModuleIndex[info[1]] = LuaModuleIndex[info[1]] + "    " + \
                    info[2]+" = add {code = "+info[0] + \
                    ", message = \""+info[3]+"\"},\n"
                TsModuleIndex[info[1]] = TsModuleIndex[info[1]] + \
                    "    "+info[2]+": "+info[0]+", // "+info[3]+"\n"
                ErrorList = ErrorList + "    "+info[0]+": \""+info[3]+"\",\n"

        for module in ModuleList:
            LuaErrorCode = LuaErrorCode.replace(
                "%ModuleError%", LuaModuleIndex[module]+"}\n\n%ModuleError%")
            TsErrorCode = TsErrorCode.replace(
                "%ModuleError%", TsModuleIndex[module]+"}\n\n%ModuleError%")

        LuaErrorCode = LuaErrorCode.replace("\n\n%ModuleError%", "")
        TsErrorCode = TsErrorCode.replace("%ErrorList%", ErrorList)
        TsErrorCode = TsErrorCode.replace("\n\n%ModuleError%", "")
        # print(TsErrorCode)
        sfd = io.open(DEFAULT_PATH + "/Code/LuaErrorCode.lua",
                      'w', encoding='utf-8')
        sfd.write(LuaErrorCode)
        sfd.close()
        sfd = io.open(DEFAULT_PATH + "/Code/TsErrorCode.ts",
                      'w', encoding='utf-8')
        sfd.write(TsErrorCode)
        sfd.close()

    def load(self, fileName):
        print('load ' + fileName)
        workbook = xlrd.open_workbook(EXCEL_PATH + '/' + fileName)
        if not workbook:
            print('配置表不存在:' + fileName)
            return

        for sheet in workbook.sheets():
            print(sheet.name)
            # if sheet.name != "动画列表(cc_client_config)":continue
            tableName = getTableName(sheet.name)
            if not tableName:
                continue
            self._parse(fileName, sheet, tableName)

    def _parse(self, fileName, sheet, tableName):
        nrows = sheet.nrows
        if nrows <= 4:
            print('表至少多于4行：' + sheet.name)
            return False

        # 第二行为英文key
        voParser = VOParser(fileName, tableName)
        keyLine = sheet.row_values(1)
        for i, key in enumerate(keyLine):
            desc = sheet.row_values(0)[i]
            valueType = sheet.row_values(2)[i]
            output = sheet.row_values(3)[i]
            voParser.addKey(i, key, desc, valueType, output)

        print("tableName:%s" % tableName)
        for exportType in self.exportList:
            if exportType == ExportType.Lua.name:
                self._parseToLua(tableName, sheet, voParser, CLIENT_PATH +
                                 "/" + exportType, OutputType.Client.name)
                self._parseToLua(tableName, sheet, voParser, SERVER_PATH +
                                 "/" + exportType, OutputType.Server.name)
            if exportType == ExportType.Json.name:
                self._parseToJson(
                    tableName, sheet, voParser, CLIENT_PATH + "/" + exportType, OutputType.Client.name)
                self._parseToJson(
                    tableName, sheet, voParser, SERVER_PATH + "/" + exportType, OutputType.Server.name)
            if exportType == ExportType.Ts.name:
                self._parseToTs(tableName, sheet, voParser, CLIENT_PATH +
                                "/" + exportType, OutputType.Client.name)
                self._parseToTs(tableName, sheet, voParser, SERVER_PATH +
                                "/" + exportType, OutputType.Server.name)
        return True

    def _parseToLua(self, tableName, sheet, voParser, path, output):
        luaTable = '-- ' + voParser.getLuaTitle(1)
        luaTable = luaTable + "local " + tableName + '= {\n'
        for rowIndex in range(4, sheet.nrows):
            lineValues = sheet.row_values(rowIndex)
            if isNone(lineValues[0]):
                continue
            line = voParser.parseToLua(lineValues, output)
            luaTable = luaTable + line
        luaTable = luaTable + '}\nreturn ' + tableName
        # print(luaTable)

        fd = io.open(path + '/' + tableName + '.lua', 'w', encoding='utf-8')
        fd.write(luaTable)
        fd.close()

    def _parseToJson(self, tableName, sheet, voParser, path, output):
        fd = io.open(path + '/' + tableName + '.json', 'w', encoding='utf-8')
        # fd.write("--test\n")
        jsonTable = "[\n"
        jsonTable = jsonTable + voParser.getJsonTitle(1)
        for rowIndex in range(4, sheet.nrows):
            lineValues = sheet.row_values(rowIndex)
            if isNone(lineValues[0]):
                continue
            line = voParser.parseToJson(rowIndex, lineValues, output)
            jsonTable = jsonTable + line
        jsonTable = jsonTable + ']'

        # 修正格式
        jsonTable = jsonTable.replace(', ]', ']')
        jsonTable = jsonTable.replace('],\n]', ']\n]')

        fd.write(jsonTable)
        fd.close()
        # print(jsonTable)

    def _parseToTs(self, tableName, sheet, voParser, path, output):
        voParser.parseToTs(path, output)


if __name__ == "__main__":
    # 获取导出类型
    excelParser = ExcelParser()
    for index in range(len(sys.argv)):
        if index > 0:
            exportType = sys.argv[index]
            excelParser.addExportType(exportType)

    while len(excelParser.exportList) == 0:
        exportType = input('请输入导出类型[Lua][Json][Ts]:\n')
        if exportType != '':
            excelParser.addExportType(exportType)

    print('导出 >>> %s' % excelParser.exportList)

    excelParser.checkDir()
    excelParser.loadAllExcel()
    # input("导出完成，按任意键退出")
