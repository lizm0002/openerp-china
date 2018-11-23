# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2015 上海开阖软件有限公司 (http://www.osbzr.com). 
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
{
    'name': '形态转换单',
    'category': 'osbzr',
    'summary': '库存中的一种或几种产品转换成另一种或几种产品的处理方法',
    'description': '''形态转换：某种存货在存储过程中，由于环境或本身原因，使其形态发生变化，由一种形态转化为另一形态，从而引起存货规格和成本的变化，在库存管理中需对此进行管理记录。
例如特种烟丝变为普通烟丝、煤块由于风吹、雨淋，天长日久变成了煤渣；活鱼由于缺氧变成了死鱼等等。
库管员需根据存货的实际状况创建形态转换单，报请财务批准后进行调账处理。''',
    'version': '1.0',
    'author': 'jeff@osbzr.com,flora@osbzr.com',
    'website': "http://www.osbzr.com",
    'depends': ['base','stock'],
    'data': [
             'security/groups.xml',
             'security/ir.model.access.csv',
             'osbzr_stock_change_view.xml',
             'osbzr_stock_change_data.xml',
             ],
    'installable': True,
}

