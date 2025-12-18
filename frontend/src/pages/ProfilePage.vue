<template>
  <div class="grid">
    <!-- User Card -->
    <div class="col-12 md:col-4">
      <div class="card flex flex-column align-items-center text-center p-5">
        <div class="relative mb-4">
            <Avatar :label="userInitials" class="w-8rem h-8rem text-4xl bg-green-500 text-white shadow-2" shape="circle" v-if="!auth.state.avatarUrl" />
            <img v-else :src="auth.state.avatarUrl" class="w-8rem h-8rem border-circle shadow-2 object-cover" />
            
            <FileUpload mode="basic" name="avatar" accept="image/*" :maxFileSize="1000000" @select="onAvatarUpload" :auto="true" chooseLabel="" class="absolute bottom-0 right-0 p-button-rounded p-button-secondary p-button-sm opacity-80" icon="pi pi-camera" />
        </div>
        
        <h2 class="text-900 font-bold m-0 mb-2">{{ auth.state.user?.full_name || 'User' }}</h2>
        <Tag :value="auth.state.isSuperuser ? 'Administrator' : 'Standard Member'" :severity="auth.state.isSuperuser ? 'success' : 'info'" class="px-3" />
        
        <!-- Subscription Card -->
        <div class="mt-4 flex flex-column gap-2 w-full text-left surface-50 p-3 border-round border-1 surface-border">
            <div class="flex align-items-center justify-content-between mb-2">
                <div class="text-sm font-bold text-500 uppercase">Current Subscription</div>
                <Tag :value="currentPlanName" :severity="getPlanSeverity(currentPlanName)" rounded></Tag>
            </div>
            
            <div class="flex align-items-end gap-2 mb-2">
                <span class="text-3xl font-bold text-900">{{ currentPlanPrice }}</span>
                <span class="text-600 mb-1">/ year</span>
            </div>

            <div class="text-xs text-600 flex align-items-center gap-2">
                <i class="pi pi-calendar"></i>
                <span>Expires: <strong>{{ currentPlanExpiry ? formatDate(currentPlanExpiry) : 'No Expiry' }}</strong></span>
            </div>
            
             <div class="flex gap-2 mt-3 text-white">
                <Button label="Renew" size="small" icon="pi pi-refresh" class="flex-1 p-button-outlined" @click="renewSubscription" :loading="renewing" />
                <Button label="Upgrade" size="small" icon="pi pi-arrow-up" class="flex-1" @click="showPricing" />
            </div>
        </div>
      </div>
      
       <div class="card p-3 mt-3">
            <div class="text-lg font-bold text-900 mb-3">Enabled Features</div>
            <div v-if="enabledFeatures.length === 0" class="text-600 text-sm">
                No advanced features enabled on the Starter plan. Upgrade to access AI tools.
            </div>
            <ul v-else class="list-none p-0 m-0 flex flex-column gap-3">
                <li v-for="(feature, index) in enabledFeatures" :key="index" class="flex align-items-center p-2 surface-50 border-round">
                    <i class="pi pi-check-circle text-green-500 mr-3 text-xl"></i>
                    <div>
                        <div class="font-medium text-900">{{ feature.name }}</div>
                        <div class="text-sm text-600">{{ feature.desc }}</div>
                    </div>
                </li>
            </ul>
       </div>
    </div>

    <!-- Edit Form -->
    <div class="col-12 md:col-8">
      <div class="card p-5 h-full">
        <h3 class="text-900 font-bold mb-4">Profile Settings</h3>
        
        <div class="flex flex-column gap-4">
             <div class="flex flex-column gap-2">
                <label for="email" class="font-bold text-900">Email Address</label>
                <InputText id="email" v-model="form.email" disabled class="p-inputtext-filled" />
                <small class="text-500">Email cannot be changed directly for security.</small>
            </div>
            
            <div class="flex flex-column gap-2">
                <label for="fullname" class="font-bold text-900">Full Name</label>
                <InputText id="fullname" v-model="form.full_name" />
            </div>

            <Divider />

            <h4 class="text-900 font-bold m-0">Change Password</h4>
            <div class="flex flex-column gap-2">
                <label for="password" class="font-bold text-900">New Password</label>
                <Password id="password" v-model="form.password" :feedback="true" toggleMask />
                <small class="text-500">Leave blank to keep current password.</small>
            </div>
            
            <div class="flex justify-content-end mt-4">
                <Button label="Save Changes" icon="pi pi-check" @click="saveProfile" :loading="loading" />
            </div>
        </div>
      </div>
    </div>

    <!-- Pricing Dialog -->
    <Dialog v-model:visible="pricingDialog" modal header="Choose Your Plan" :style="{ width: '80vw', maxWidth: '1000px' }" :draggable="false">
        <div class="grid p-4">
            <div class="col-12 md:col-4" v-for="plan in plans" :key="plan.id">
                <div class="surface-card p-4 shadow-2 border-round h-full flex flex-column text-center hover:shadow-4 transition-all transition-duration-300 transform hover:-translate-y-1 cursor-pointer" 
                    :class="{ 'border-green-500 border-2': currentPlanName === plan.name, 'surface-b ground': currentPlanName !== plan.name }">
                    
                    <div class="text-xl font-medium text-900 mb-2">{{ plan.name }}</div>
                    <div class="text-4xl font-bold text-900 mb-4">{{ plan.price }}<span class="text-base text-500 font-normal"> / year</span></div>
                    
                    <ul class="list-none p-0 m-0 mb-5 text-left flex-1">
                        <li v-for="feature in plan.features" :key="feature" class="flex align-items-center mb-2">
                            <i class="pi pi-check-circle text-green-500 mr-2"></i>
                            <span class="text-700">{{ feature }}</span>
                        </li>
                    </ul>

                    <Button :label="currentPlanName === plan.name ? 'Current Plan' : 'Select Plan'" 
                        :class="currentPlanName === plan.name ? 'p-button-success' : 'p-button-outlined'" 
                        :disabled="currentPlanName === plan.name"
                        @click="selectPlan(plan)"
                        class="w-full mt-auto" />
                </div>
            </div>
        </div>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { updateMe } from '../api/users';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Avatar from 'primevue/avatar';
import Tag from 'primevue/tag';
import FileUpload from 'primevue/fileupload';
import Divider from 'primevue/divider';
import Dialog from 'primevue/dialog';

const auth = useAuthStore();
const loading = ref(false);
const renewing = ref(false);
const pricingDialog = ref(false);

const form = ref({
    email: auth.state.user?.email || '',
    full_name: auth.state.user?.full_name || '',
    password: ''
});

// Plans Data
const plans = [
    {
        id: 'starter',
        name: 'Starter',
        price: 'Free',
        features: ['Basic Support', '1 User', 'Limited Access']
    },
    {
        id: 'pro',
        name: 'Professional',
        price: '$499',
        features: ['Priority Support', '5 Users', 'Contract Assistant', 'Expense Helper']
    },
    {
        id: 'enterprise',
        name: 'Enterprise AI',
        price: '$999',
        features: ['24/7 Dedicated Support', 'Unlimited Users', 'All AI Features', 'Custom Integrations']
    }
];

// Computed properties to read from store (Database)
const currentPlanName = computed(() => auth.state.user?.plan_name || 'Starter');
const currentPlanPrice = computed(() => auth.state.user?.plan_price || 'Free');
const currentPlanExpiry = computed(() => auth.state.user?.plan_expiry || null);

const enabledFeatures = computed(() => {
    const plan = currentPlanName.value;
    const features = [];
    
    // Logic for features based on plan (Name matching)
    if (plan.includes('Professional') || plan.includes('Enterprise')) {
        features.push({ name: 'Contract Assistant', desc: 'AI OCR Analysis' });
        features.push({ name: 'Expense Helper', desc: 'Smart Reimbursement' });
    }
    
    if (plan.includes('Enterprise')) {
        features.push({ name: 'Custom Integrations', desc: 'API Access' });
    }
    
    return features;
});

const userInitials = computed(() => {
    const name = auth.state.user?.full_name || 'U';
    return name.charAt(0).toUpperCase();
});

const formatDate = (dateString: string) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
};

const getPlanSeverity = (name: string) => {
    if (name.includes('Enterprise')) return 'success';
    if (name.includes('Professional')) return 'info';
    return 'warning';
};

const onAvatarUpload = (event: any) => {
    const file = event.files[0];
    const reader = new FileReader();
    reader.onload = (e: any) => {
        auth.setAvatar(e.target.result);
    };
    reader.readAsDataURL(file);
};

const saveProfile = async () => {
    loading.value = true;
    try {
        const payload: any = { full_name: form.value.full_name };
        if (form.value.password) {
            payload.password = form.value.password;
        }
        const updatedUser = await updateMe(payload);
        auth.setUser(updatedUser);
        alert('Profile updated successfully!');
        form.value.password = ''; 
    } catch (e) {
        console.error(e);
        alert('Failed to update profile.');
    } finally {
        loading.value = false;
    }
};

const showPricing = () => {
    pricingDialog.value = true;
};

const renewSubscription = async () => {
    renewing.value = true;
    try {
        const currentExp = currentPlanExpiry.value ? new Date(currentPlanExpiry.value) : new Date();
        currentExp.setFullYear(currentExp.getFullYear() + 1);
        
        const payload = { plan_expiry: currentExp.toISOString() };
        const updatedUser = await updateMe(payload);
        auth.setUser(updatedUser);

        alert('Subscription successfully renewed for 1 year!');
    } catch (e) {
        console.error(e);
        alert('Failed to renew subscription');
    } finally {
        renewing.value = false;
    }
};

const selectPlan = async (plan: any) => {
    if (confirm(`Are you sure you want to switch to the ${plan.name} plan?`)) {
        try {
            const payload = {
                plan_name: plan.name,
                plan_price: plan.price,
                // If switching plan, maybe reset expiry or keep it? 
                // Let's set it to 1 year from now for simplicity of demo
                plan_expiry: new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toISOString()
            };
            
            const updatedUser = await updateMe(payload);
            auth.setUser(updatedUser);
            
            pricingDialog.value = false;
            alert(`Successfully switched to ${plan.name}!`);
        } catch (e) {
            console.error(e);
            alert('Failed to switch plan.');
        }
    }
};
</script>
