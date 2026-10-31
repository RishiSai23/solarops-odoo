/** @odoo-module **/

import { Component } from "@odoo/owl";

export class EmptyState extends Component {
    static template = "sunflow_web.EmptyState";
    static props = ["title", "description"];
}
