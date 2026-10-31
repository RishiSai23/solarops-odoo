/** @odoo-module **/

import { Component } from "@odoo/owl";
import { Sidebar } from "../navigation/Sidebar";
import { Header } from "../navigation/Header";

export class WorkspaceLayout extends Component {
    static template = "sunflow_web.WorkspaceLayout";
    static components = { Sidebar, Header };
}

