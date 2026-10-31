/** @odoo-module **/

import { Component } from "@odoo/owl";

export class DataTable extends Component {
    static template = "sunflow_web.DataTable";
    static props = ["columns", "rows"];
}
