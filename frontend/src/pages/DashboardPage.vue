<template>
  <div class="grid">
    <!-- Stats Cards -->
    <div class="col-12 md:col-6 lg:col-3">
        <div class="surface-card shadow-2 p-3 border-round">
            <div class="flex justify-content-between mb-3">
                <div>
                    <span class="block text-500 font-medium mb-3">Total Tokens</span>
                    <div class="text-900 font-medium text-xl">152,450</div>
                </div>
                <div class="flex align-items-center justify-content-center bg-blue-100 border-round" style="width:2.5rem;height:2.5rem">
                    <i class="pi pi-database text-blue-500 text-xl"></i>
                </div>
            </div>
            <span class="text-green-500 font-medium">24 new </span>
            <span class="text-500">since last visit</span>
        </div>
    </div>
    <div class="col-12 md:col-6 lg:col-3">
        <div class="surface-card shadow-2 p-3 border-round">
            <div class="flex justify-content-between mb-3">
                <div>
                    <span class="block text-500 font-medium mb-3">Current Cost</span>
                    <div class="text-900 font-medium text-xl">${{ currentCost }}</div>
                </div>
                <div class="flex align-items-center justify-content-center bg-orange-100 border-round" style="width:2.5rem;height:2.5rem">
                    <i class="pi pi-dollar text-orange-500 text-xl"></i>
                </div>
            </div>
             <span class="text-500">Billing cycle ends </span>
             <span class="text-green-500 font-medium">Dec 31</span>
        </div>
    </div>
    <div class="col-12 md:col-6 lg:col-3">
        <div class="surface-card shadow-2 p-3 border-round">
            <div class="flex justify-content-between mb-3">
                <div>
                    <span class="block text-500 font-medium mb-3">Active Models</span>
                    <div class="text-900 font-medium text-xl">GPT-4o</div>
                </div>
                <div class="flex align-items-center justify-content-center bg-cyan-100 border-round" style="width:2.5rem;height:2.5rem">
                    <i class="pi pi-server text-cyan-500 text-xl"></i>
                </div>
            </div>
            <span class="text-500">Status: </span>
            <span class="text-green-500 font-medium">Operational</span>
        </div>
    </div>
    <div class="col-12 md:col-6 lg:col-3">
        <div class="surface-card shadow-2 p-3 border-round">
            <div class="flex justify-content-between mb-3">
                <div>
                    <span class="block text-500 font-medium mb-3">Plan</span>
                    <div class="text-900 font-medium text-xl">{{ userPlan }}</div>
                </div>
                <div class="flex align-items-center justify-content-center bg-purple-100 border-round" style="width:2.5rem;height:2.5rem">
                    <i class="pi pi-crown text-purple-500 text-xl"></i>
                </div>
            </div>
             <span class="text-500">Upgrade for </span>
             <span class="text-blue-500 font-medium">More Features</span>
        </div>
    </div>

    <!-- Usage Chart -->
    <div class="col-12 lg:col-8">
        <div class="surface-card shadow-2 border-round p-4 h-full">
            <div class="text-xl font-bold text-900 mb-4">Azure Data Usage (Last 7 Days)</div>
            <Chart type="bar" :data="chartData" :options="chartOptions" class="h-30rem" />
        </div>
    </div>

    <!-- News & Updates -->
    <div class="col-12 lg:col-4">
        <div class="surface-card shadow-2 border-round p-4 h-full">
            <div class="flex align-items-center justify-content-between mb-4">
                <span class="text-xl font-bold text-900">Platform News</span>
            </div>

             <div class="flex flex-column gap-3">
                 <div class="bg-blue-50 p-3 border-round mb-1 text-sm">
                    <div class="font-bold text-blue-900 mb-1">New Model Support</div>
                    <div class="text-blue-700 block mb-2">GPT-4 Turbo is now available for Enterprise users. Faster and cheaper.</div>
                    <small class="text-blue-500">2 hours ago</small>
                 </div>
                 
                 <div class="border-bottom-1 surface-border pb-3">
                    <div class="font-medium text-900 mb-1">System Maintenance</div>
                    <div class="text-600 text-sm mb-2">Scheduled maintenance on Dec 25th, 2AM - 4AM UTC.</div>
                    <small class="text-500">Yesterday</small>
                 </div>

                 <div class="pb-2">
                     <div class="font-medium text-900 mb-1">Contract Assistant Update</div>
                    <div class="text-600 text-sm mb-2">Improved OCR accuracy for scanned PDFs.</div>
                    <small class="text-500">3 days ago</small>
                 </div>
             </div>
        </div>
    </div>
    
     <!-- Recent Activity -->
    <div class="col-12">
        <div class="surface-card shadow-2 border-round p-4">
            <div class="text-xl font-bold text-900 mb-4">Recent Activity</div>
            <DataTable :value="recentActivity" responsiveLayout="scroll">
                <Column field="action" header="Action"></Column>
                <Column field="app" header="Application">
                    <template #body="slotProps">
                        <Tag :value="slotProps.data.app" :severity="getAppSeverity(slotProps.data.app)" />
                    </template>
                </Column>
                <Column field="details" header="Details"></Column>
                <Column field="time" header="Time"></Column>
                 <Column field="cost" header="Estimated Cost">
                     <template #body="slotProps">
                        {{ slotProps.data.cost }}
                     </template>
                 </Column>
            </DataTable>
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import Chart from 'primevue/chart';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';

// Register ChartJS components
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const auth = useAuthStore();
const userPlan = computed(() => auth.state.user?.plan_name || 'Starter');

// Mock Cost
const currentCost = computed(() => {
    return userPlan.value === 'Starter' ? '0.00' : '15.42';
});

// Chart Data
const chartData = ref({
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
        {
            label: 'Tokens (k)',
            backgroundColor: '#10b981', // brand-green
            data: [65, 59, 80, 81, 56, 55, 40]
        },
        {
            label: 'Cost ($)',
            backgroundColor: '#3b82f6',
            data: [2.5, 1.9, 3.2, 3.5, 1.5, 1.2, 1.0]
        }
    ]
});

const chartOptions = ref({
    plugins: {
        legend: {
            labels: {
                color: '#495057'
            }
        }
    },
    scales: {
        x: {
            ticks: {
                color: '#495057'
            },
            grid: {
                color: '#ebedef'
            }
        },
        y: {
            ticks: {
                color: '#495057'
            },
            grid: {
                color: '#ebedef'
            }
        }
    }
});

// Recent Activity Data
const recentActivity = ref([
    { action: 'Analysis', app: 'Contract Assistant', details: 'NDA_Vendor_v2.pdf', time: '10 mins ago', cost: '$0.05' },
    { action: 'Extraction', app: 'Expense Helper', details: 'Uber_Receipt_Dec18.jpg', time: '2 hours ago', cost: '$0.01' },
    { action: 'Chat Query', app: 'Contract Assistant', details: 'Clause Verification', time: 'Yesterday', cost: '$0.02' },
    { action: 'Analysis', app: 'Contract Assistant', details: 'Service_Agreement_Draft.docx', time: 'Yesterday', cost: '$0.12' },
    { action: 'Bulk Process', app: 'Expense Helper', details: 'Batch_Nov_Expenses', time: '2 days ago', cost: '$0.45' },
]);

const getAppSeverity = (app: string) => {
    if (app === 'Contract Assistant') return 'info';
    if (app === 'Expense Helper') return 'warning';
    return 'success'; 
};
</script>
