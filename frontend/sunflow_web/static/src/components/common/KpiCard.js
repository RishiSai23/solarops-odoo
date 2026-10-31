/** @odoo-module **/

import { Component } from "@odoo/owl";

export class KpiCard extends Component {
    static template = "sunflow_web.KpiCard";
    static props = ["label", "value", "delta"];
}
