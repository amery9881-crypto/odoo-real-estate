/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class RealEstateDashboard extends Component {
    static template = "app_one.RealEstateDashboard";

    setup() {
        this.state = useState({
            totalProperties: 0,
            soldProperties: 0,
            draftProperties: 0,
        });

        this.rpc = useService("rpc");
        this.loadDashboardData();
    }

    async loadDashboardData() {
        this.state.totalProperties = await this.rpc("/web/dataset/call_kw", {
            model: "property",
            method: "search_count",
            args: [[]],
            kwargs: {},
        });

        this.state.soldProperties = await this.rpc("/web/dataset/call_kw", {
            model: "property",
            method: "search_count",
            args: [[['state', '=', 'sold']]],
            kwargs: {},
        });

        this.state.draftProperties = await this.rpc("/web/dataset/call_kw", {
            model: "property",
            method: "search_count",
            args: [[['state', '=', 'draft']]],
            kwargs: {},
        });
    }
}

registry.category("actions").add("app_one.action_real_estate_dashboard", RealEstateDashboard);