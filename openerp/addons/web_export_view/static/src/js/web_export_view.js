//  @@@ web_export_view custom JS @@@
//#############################################################################
//    
//    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
//    Copyright (C) 2012 Therp BV (<http://therp.nl>)
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU Affero General Public License as published
//    by the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU Affero General Public License for more details.
//
//    You should have received a copy of the GNU Affero General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
//#############################################################################
openerp.web_export_view = function (instance) {

    var _t = instance.web._t, QWeb = instance.web.qweb;

    instance.web.Sidebar.include({
        redraw: function () {
            var self = this;
            this._super.apply(this, arguments);
            if (self.getParent().ViewManager.active_view == 'list') {
                self.$el.find('.oe_sidebar').append(QWeb.render('AddExportViewMain', {widget: self}));
                self.$el.find('.oe_sidebar_export_view_xls').on('click', self.on_sidebar_export_view_xls);
            }
        },

        on_sidebar_export_view_xls: function () {
            // Select the first list of the current (form) view
            // or assume the main view is a list view and use that
            var self = this,
            view = this.getParent(),

            children = view.getChildren();
             
            if (children) {
                children.every(function (child) {
                    if (child.field && child.field.type == 'one2many') {
                        view = child.viewmanager.views.list.controller;
                        return false; // break out of the loop
                    }
                    if (child.field && child.field.type == 'many2many') {
                        view = child.list_view;
                        return false; // break out of the loop
                    }
                    return true;
                });
            }
            export_columns_keys = [];
            export_columns_names = [];
            $.each(view.visible_columns, function () {
                if (this.tag == 'field') {
                    // non-fields like `_group` or buttons
                    export_columns_keys.push(this.id);
                    export_columns_names.push(this.string);
                }
            });
            
            rows = view.$el.find('.oe_list_content > tbody > tr');
            view_title =self.getParent().ViewManager.$el.find('.oe_view_title >span > span.oe_breadcrumb_item');
            title_cell=view_title.get(0);
            title_text = title_cell.text || title_cell.textContent || title_cell.innerHTML || "";
            export_rows = [];
            export_rows.push(export_columns_names);
            var a = new Array(export_columns_names.length); 
            for (var i=0;i<a.length;i++){a[i]=" ";}
            a[0]=_t(title_text);
            export_columns_names=a;
            $.each(rows, function () {
                $row = $(this);
                // find only rows with data
                if ($row.attr('data-id')) {
                    export_row = [];
                    checked = $row.find('th input[type=checkbox]').attr("checked");
                    if (children && checked === "checked") {
                        $.each(export_columns_keys, function () {
                            cell = $row.find('td[data-field="' + this + '"]').get(0);
                            text = cell.text || cell.textContent || cell.innerHTML || "";
                            if (cell.classList.contains("oe_list_field_float")) {
                                export_row.push(instance.web.parse_value(text, {'type': "float"}));
                            }
                            else if (cell.classList.contains("oe_list_field_boolean")) {
                                var data_id = $('<div>' + cell.innerHTML + '</div>');
                                if (data_id.find('input').get(0).checked) {
                                    export_row.push(_t("True"));
                                }
                                else {
                                    export_row.push(_t("False"));
                                }
                            }
                            else if (cell.classList.contains("oe_list_field_integer")) {
                                var tmp2 = text;
                                do {
                                    tmp = tmp2;
                                    tmp2 = tmp.replace(instance.web._t.database.parameters.thousands_sep, "");
                                } while (tmp !== tmp2);

                                export_row.push(parseInt(tmp2));
                            }
                            else {
                                export_row.push(text.trim());
                            }
                        });
                        export_rows.push(export_row);
                    }
                }
            });
             $.blockUI();
             amount = view.$el.find('.oe_list_content > tfoot > tr');
             var footer=0;
             $.each(amount, function () {
             	 $row = $(this);
             	 var export_row=[];
             	 var index=0;
             	 $.each(export_columns_keys, function () {
	             	 cell = $row.find('.oe_list_footer').get(index);
	             	 index=index+1;
	             	 text = cell.text || cell.textContent || cell.innerHTML || "";
	             	 if (text.indexOf(" ") == -1){
	             	 	footer=1;
	             	 }
	             	 if (text.indexOf(" ") == -1 ){
	             	 	export_row.push(instance.web.parse_value(text, {'type': "float"}));}
	             	 else{
	             	 	text=_t(" ");
	             	 	export_row.push(text);
	             	 }
             	 });
             	 if (footer==1){
             	 	export_row[0]=_t("合计");
             	 	export_rows.push(export_row);
             	 }
             });
          
 		var export_template = new instance.web.Model("res.users");
        var now_day;
          export_template.call('get_time',"" ,{
                    context: this.view.dataset.context
             }).done(function(data) {
                			now_day =data;
                			var date=new Date().getTime();
                	        var  operation_message=new Array(export_columns_names.length); 
                	        for (var i=0;i<operation_message.length;i++){operation_message[i]=" ";}
                	       operation_message[0]=_t( "操作人");
                	       operation_message[1]=_t(self.getParent().session.username);
                	       operation_message[2]= _t("操作时间");
                	       operation_message[3]=_t(now_day.trim());
				           export_rows.push(operation_message);
				           $.blockUI();
				           view.session.get_file({
				                url: '/web/export/xls_view',
				                data: {data: JSON.stringify({
				                    model: view.model,
				                    headers: export_columns_names,
				                    rows: export_rows
				                })},
				                complete: $.unblockUI
				            });
              });
        }
    });
};
