/** @odoo-module **/

import { Component } from "@odoo/owl";
import { WorkspaceLayout } from "../../layout/WorkspaceLayout";
import { KpiCard } from "../../common/KpiCard";
import { DataTable } from "../../common/DataTable";
import { StatusBadge } from "../../common/StatusBadge";
import { directorDemoData } from "./director_dashboard_data";

export class DirectorDashboard extends Component {
    static template = "sunflow_web.DirectorDashboard";
    static components = { WorkspaceLayout, KpiCard, DataTable, StatusBadge };

    setup() {
        this.data = directorDemoData;
        this.columns = [
            { key: "project", label: "Project ID" },
            { key: "customer", label: "Customer" },
            { key: "capacity", label: "System Capacity" },
            { key: "type", label: "System Type" },
            { key: "stage", label: "Project Stage" },
            { key: "technician", label: "Assigned Technician" },
        ];
    }
}
