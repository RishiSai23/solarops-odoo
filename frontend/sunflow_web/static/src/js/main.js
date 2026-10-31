/** @odoo-module **/

import { Component, xml } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { WorkspaceLayout } from "../components/layout/WorkspaceLayout";
import { KpiCard } from "../components/common/KpiCard";
import { DataTable } from "../components/common/DataTable";
import { DirectorDashboard } from "../components/dashboard/director_dashboard/DirectorDashboard";

export class SunflowTestScreen extends Component {
    static template = xml`
        <WorkspaceLayout>
            <div class="o_sunflow_content">
                <h2 style="margin-top: 0;">SunFlow Web UI Test</h2>
                <p style="color: var(--sunflow-text-secondary);">Shared layout foundation demonstration with reusable components.</p>
                <div class="o_sunflow_kpi_grid">
                    <KpiCard label="Active Projects" value="12" delta="+2 this month"/>
                    <KpiCard label="Installations Today" value="3" delta="On schedule"/>
                    <KpiCard label="Pending Surveys" value="5" delta="Awaiting review"/>
                    <KpiCard label="Open Service Tickets" value="2" delta="Needs attention"/>
                </div>
                <DataTable columns="props.columns" rows="props.rows"/>
            </div>
        </WorkspaceLayout>
    `;
    static components = { WorkspaceLayout, KpiCard, DataTable };
    setup() {
        this.columns = [
            { key: "project", label: "Project" },
            { key: "customer", label: "Customer" },
            { key: "capacity", label: "Capacity" },
            { key: "status", label: "Status" },
            { key: "stage", label: "Stage" },
        ];
        this.rows = [
            { id: 1, project: "SPF-0001", customer: "Acme Industries", capacity: "5.0 kW", status: "Active", stage: "Installation" },
            { id: 2, project: "SPF-0002", customer: "Green Homes Ltd", capacity: "3.0 kW", status: "Active", stage: "Survey" },
            { id: 3, project: "SPF-0003", customer: "Sunrise Retail", capacity: "4.0 kW", status: "Pending", stage: "Quotation" },
        ];
    }
}

registry.category("actions").add("sunflow_web.test_screen", SunflowTestScreen);

registry.category("actions").add("sunflow_web.director_dashboard", DirectorDashboard);
