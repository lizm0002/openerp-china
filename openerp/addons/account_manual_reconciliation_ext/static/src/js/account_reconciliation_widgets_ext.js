openerp.account_manual_reconciliation_ext = function (instance) {

    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.account = instance.web.account || {};

    instance.web.account.ReconciliationListView.include({
        load_list: function() {
            var self = this;
            this._super.apply(this, arguments);
            if (self.partners) {
                this.$('#partners').change(function(){
                    self.current_partner = $("#partners").get(0).selectedIndex;
                    self.search_by_partner();
                });
                this.$(".oe_account_recon_reconcile").click(function() {
                    //如果存在current_partner,则保存在Local Storage中
                    if(self.current_partner) {
                        localStorage.cur_reconcilable_partner = self.current_partner;
                    }
                    self.reconcile();
                });
            }
        },

        init: function() {
            this._super.apply(this, arguments);
            var self = this;
            if(localStorage.cur_reconcilable_partner)
                this.current_partner = localStorage.cur_reconcilable_partner ;
            else
                this.current_partner = null;

        },




    });
};


