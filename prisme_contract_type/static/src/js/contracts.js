openerp.prisme_contract_type = function (instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    instance.web.prisme_contract_type = instance.web.prisme_contract_type || {};
    instance.web.views.add('tree_contracts', 'instance.web.prisme_contract_type.ContractsListView');
    instance.web.prisme_contract_type.ContractsListView = instance.web.ListView.extend({
	//init: function() {
	//	 this._super.apply(this, arguments);
	//},
        load_list: function() {
            var self = this;
            var tmp = this._super.apply(this, arguments);
            this.$el.prepend(QWeb.render("ContractsWizard", {widget: this}));
	    this.$(".oe_contracts_compute").click(function(){
		self.rpc("/web/action/load", { action_id: "prisme_contract_type.action_contract_simplified_wizard" }).done(function(result) {
			self.getParent().do_action(result,{additional_context:{},});
			var v = new instance.web.View;
			v.reload();

		});   
		var v = new instance.web.View;
		v.reload();
	    });
            return tmp;
        },
    });    
};

