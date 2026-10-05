/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { FormView } from "@app_one/components/formView/formView";

export class ListViewAction extends Component {
    static template = "app_one.ListView";
    static components = { FormView };

    setup() {
        this.state = useState({
            records: [],
            showCreateForm: false,
            limit: 5,
            offset: 0,
            totalRecords: 0
        });

        this.rpc = useService("rpc");
        this.loadRecords();
        this.onRecordCreated = this.onRecordCreated.bind(this);
    }

    async loadRecords() {
        this.state.totalRecords = await this.rpc("/web/dataset/call_kw", {
            model: "property",
            method: "search_count",
            args: [[]],
            kwargs: {},
        });

        this.state.records = await this.rpc("/web/dataset/call_kw", {
            model: "property",
            method: "search_read",
            args: [[]],
            kwargs: {
                fields: ['id', 'name', 'postcode', 'date_availab'],
                limit: this.state.limit,
                offset: this.state.offset
            },
        });
    }

    nextPage() {
        if (this.state.offset + this.state.limit < this.state.totalRecords) {
            this.state.offset += this.state.limit;
            this.loadRecords();
        }
    }

    prevPage() {
        if (this.state.offset > 0) {
            this.state.offset -= this.state.limit;
            this.loadRecords();
        }
    }

    async deleteRecord(recordId) {
        await this.rpc("/web/dataset/call_kw", {
            model: "property",
            method: "unlink",
            args: [[recordId]],
            kwargs: {},
        });
        this.loadRecords();
    }

    toggleCreateForm() {
        this.state.showCreateForm = !this.state.showCreateForm;
    }

    onRecordCreated() {
        this.loadRecords();
        this.state.showCreateForm = false;
    }
}

registry.category("actions").add("app_one.action_list_view", ListViewAction);