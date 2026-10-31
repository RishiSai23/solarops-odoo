/** @odoo-module **/

import { Component } from "@odoo/owl";

export class LoadingState extends Component {
    static template = "sunflow_web.LoadingState";
    static props = ["message"];
}
