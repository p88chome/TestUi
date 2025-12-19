<template>
  <div class="card p-3">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2 class="text-xl font-bold m-0 text-900">User Management</h2>
      <Button label="New User" icon="pi pi-plus" size="small" @click="openNewUser" />
    </div>

    <!-- User List -->
    <DataTable :value="users" :loading="loading" class="p-datatable-sm" tableStyle="min-width: 50rem">
        <Column field="id" header="ID" style="width: 5%"></Column>
        <Column field="email" header="Email"></Column>
        <Column field="full_name" header="Full Name"></Column>
        <Column header="Current Plan">
             <template #body="slotProps">
                 <span v-if="!slotProps.data.is_superuser">{{ slotProps.data.plan_name }}</span>
                 <span v-else class="text-500">N/A (Admin)</span>
             </template>
        </Column>
        <Column header="Expiry Date">
             <template #body="slotProps">
                 <span v-if="!slotProps.data.is_superuser && slotProps.data.plan_expiry">{{ new Date(slotProps.data.plan_expiry).toLocaleDateString() }}</span>
                 <span v-else-if="!slotProps.data.is_superuser">-</span>
             </template>
        </Column>
        <Column field="is_active" header="Active">
            <template #body="slotProps">
                <Tag :value="slotProps.data.is_active ? 'Yes' : 'No'" :severity="slotProps.data.is_active ? 'success' : 'danger'" />
            </template>
        </Column>
        <Column field="is_superuser" header="Admin">
            <template #body="slotProps">
                <Tag :value="slotProps.data.is_superuser ? 'Yes' : 'No'" :severity="slotProps.data.is_superuser ? 'warning' : 'info'" />
            </template>
        </Column>
        <Column header="Actions" style="width: 10%">
             <template #body="slotProps">
                 <div class="flex gap-2">
                     <Button icon="pi pi-pencil" severity="secondary" text rounded aria-label="Edit" @click="editUser(slotProps.data)" />
                     <Button icon="pi pi-trash" severity="danger" text rounded aria-label="Delete" @click="confirmDeleteUser(slotProps.data)" />
                 </div>
             </template>
        </Column>
    </DataTable>

    <!-- Create/Edit User Dialog -->
     <Dialog v-model:visible="userDialog" :style="{ width: '550px' }" :header="isEditMode ? 'Edit User' : 'New User'" :modal="true" class="p-fluid">
        <div class="field">
            <label for="email" class="font-bold">Email</label>
            <InputText id="email" v-model.trim="user.email" required="true" autofocus :class="{ 'p-invalid': submitted && !user.email }" />
            <small class="p-error" v-if="submitted && !user.email">Email is required.</small>
        </div>
        
        <div class="field">
            <label for="password" class="font-bold">Password <span v-if="isEditMode" class="font-normal text-sm text-500">(Leave blank to keep current)</span></label>
            <Password id="password" v-model="user.password" :feedback="false" toggleMask :required="!isEditMode" :class="{ 'p-invalid': submitted && !isEditMode && !user.password }" />
             <small class="p-error" v-if="submitted && !isEditMode && !user.password">Password is required.</small>
        </div>

        <div class="field">
            <label for="fullName" class="font-bold">Full Name</label>
             <InputText id="fullName" v-model.trim="user.full_name" />
        </div>

        <div class="formgrid grid">
            <div class="field col">
                <label for="planName" class="font-bold">Plan Name</label>
                <InputText id="planName" v-model="user.plan_name" placeholder="e.g. Starter, Pro" />
            </div>
            <div class="field col">
                <label for="planPrice" class="font-bold">Plan Price</label>
                <InputText id="planPrice" v-model="user.plan_price" placeholder="e.g. $10, Free" />
            </div>
        </div>

        <div class="field">
             <label for="planExpiry" class="font-bold">Plan Expiry Date</label>
             <Calendar id="planExpiry" v-model="user.plan_expiry_date" showIcon dateFormat="yy-mm-dd" />
        </div>

        <div class="field-checkbox">
             <Checkbox id="isSuperuser" v-model="user.is_superuser" :binary="true" />
             <label for="isSuperuser" class="ml-2">Is Admin?</label>
        </div>
        <div class="field-checkbox">
             <Checkbox id="isActive" v-model="user.is_active" :binary="true" />
             <label for="isActive" class="ml-2">Is Active?</label>
        </div>

        <template #footer>
            <Button label="Cancel" icon="pi pi-times" text @click="hideDialog" />
            <Button label="Save" icon="pi pi-check" text @click="saveUser" />
        </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getUsers, createUser, updateUser, deleteUser, type User, type UserCreate } from '../api/users';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Checkbox from 'primevue/checkbox';
import Calendar from 'primevue/calendar';

const users = ref<User[]>([]);
const userDialog = ref(false);
const loading = ref(false);
const submitted = ref(false);
const isEditMode = ref(false);
const editingUserId = ref<number | null>(null);

const user = ref<UserCreate & { plan_expiry_date?: Date }>({
    email: '',
    password: '',
    full_name: '',
    is_superuser: false,
    is_active: true,
    plan_name: 'Starter',
    plan_price: 'Free',
    plan_expiry: undefined,
    plan_expiry_date: undefined
});

onMounted(() => {
    loadUsers();
});

const loadUsers = async () => {
    loading.value = true;
    try {
        users.value = await getUsers();
    } catch (error) {
        console.error('Failed to load users', error);
    } finally {
        loading.value = false;
    }
};

const openNewUser = () => {
    user.value = { 
        email: '', 
        password: '', 
        full_name: '', 
        is_superuser: false,
        is_active: true,
        plan_name: 'Starter',
        plan_price: 'Free'
    }; 
    submitted.value = false;
    isEditMode.value = false;
    editingUserId.value = null;
    userDialog.value = true;
};

const editUser = (data: User) => {
    user.value = { ...data, password: '' }; // Don't fill password on edit
    if (data.plan_expiry) {
        user.value.plan_expiry_date = new Date(data.plan_expiry);
    } else {
        user.value.plan_expiry_date = undefined;
    }
    editingUserId.value = data.id;
    isEditMode.value = true;
    submitted.value = false;
    userDialog.value = true;
};

const confirmDeleteUser = async (data: User) => {
    if (confirm(`Are you sure you want to delete user ${data.email}?`)) {
        try {
            await deleteUser(data.id);
            loadUsers();
        } catch (error) {
            console.error('Failed to delete user', error);
            alert('Failed to delete user.');
        }
    }
}

const hideDialog = () => {
    userDialog.value = false;
    submitted.value = false;
};

const saveUser = async () => {
    submitted.value = true;
    // Basic validation
    if (!user.value.email.trim()) return;
    if (!isEditMode.value && !user.value.password) return;

    // Handle Date conversion
    if (user.value.plan_expiry_date) {
        user.value.plan_expiry = user.value.plan_expiry_date.toISOString();
    } else {
        user.value.plan_expiry = undefined; // Clear if empty
    }

    try {
        // Remove auxiliary field before sending
        const { plan_expiry_date, ...payload } = user.value;

        if (isEditMode.value && editingUserId.value) {
             const updateData = { ...payload };
             if (!updateData.password) delete updateData.password; // Don't send empty password
             await updateUser(editingUserId.value, updateData);
        } else {
             await createUser(payload);
        }
        userDialog.value = false;
        loadUsers(); 
    } catch (error) {
        console.error('Failed to save user', error);
        alert('Failed to save user. Email might be already taken or other error.');
    }
};
</script>
