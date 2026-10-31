/** @odoo-module **/

import { Component } from "@odoo/owl";

export class StatusBadge extends Component {
    static template = "sunflow_web.StatusBadge";
    static props = ["text", "type"];
}
